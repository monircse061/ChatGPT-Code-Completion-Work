from openai import OpenAI
import sys
import time
import re
import evaluate
import os
from difflib import SequenceMatcher
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
# Load SACREBLEU metric using evaluate.load
sacrebleu = evaluate.load("sacrebleu")
# Initialize OpenAI client 
client = OpenAI(api_key="")
request_count = 0  
prompt_tokens = 0
completion_tokens = 0
total_tokens = 0 
def read_data(file_name, sc_file_name, prog_lan, encoding): # for Small Basic Program: encoding='utf-16'
    global request_count, prompt_tokens, completion_tokens, total_tokens  # Declare the variables as global inside the function
    resultlist = []
    appx_main_start_line = 0
    text_line_num = 0
    try:
        with open(sc_file_name, 'r',encoding=encoding) as fl:
           if prog_lan == "C11":
                linesnum = fl.readlines()
                # Iterate over each line and find the line number containing the substring "stdio.h"
                for i, line in enumerate(linesnum):  # enumerate() func : index (i) and the value (line)
                    if "/usr/include" in line:  #/usr/include
                        appx_main_start_line = i+1  # Adding 1 because the index starts from 0 but in our file it's 1      
        with open(file_name, 'r', encoding=encoding) as f:
            current_block = []
            while True:
                cursor_position = ""
                prefix_ln_col_num = 0
                line = f.readline()
                if not line:  # If reading the file has finished
                    break
                if line.strip().startswith("parse"):
                    continue
                str_struct_candi=line.strip()
                if not str_struct_candi or not str_struct_candi[0].isnumeric():  # Check if 'strings' is empty or first element is not numeric
                    continue
                state = int(str_struct_candi.split()[0])  # Extract the state from the first element
                struct_candi = str_struct_candi[len(str(state)):].strip()  # Remaining elements are structural candidate
                text_candi = ""
                resulted_prefix = ""
                 # Store the first line of the block
                current_block.append(line.strip())
                while True:
                    #--------------find_prefix function--------Start----------------------#
                    def find_prefix(filename, line_num, column_num):
                        with open(filename, 'r') as file:
                            prefix = ''
                            lines = file.readlines()
                            if prog_lan == "C11":
                                    line_start=line_num-10
                            elif prog_lan == "Small Basic":
                                    line_start=0
                            while line_start < line_num-1:
                                    prefix += lines[line_start] 
                                    line_start+=1

                            target_line = lines[line_num - 1] # print ("target line: ",target_line)
                            current_column = 0
                            # print ("line_num: ",line_num, "column_num ", column_num, "target_line:", target_line,"\n")
                            for char in target_line:
                                if char == ' ':
                                    current_column += 1
                                elif char == '\t':  # Counting tabs as one character
                                    current_column += 1  # Assuming tab width is 1 spaces
                                else:
                                    current_column += 1
                                if current_column >= column_num:
                                    break
                                prefix += char
                            return prefix.strip()
                    #--------------find_prefix function--------End----------------------#
                    content_line = f.readline().strip()  # Read the second line and to skip the first line
                    parts = content_line.split(':', 1)  # Split each line into two parts based on the first colon
                    ln_col = parts[0].split(',')   # Split each part into line and column number based on comma
        
                    if not content_line:  # Check if we've reached the end of the block
                        if len(current_block) >= 2:
                            # print("Second line of the block:", current_block[1].strip())
                            if current_block[1].startswith("PR#"):  # Skip lines starting with 'PR#'
                                parts = current_block[2].split(':', 1)  # Split each line into two parts based on the first colon
                            else:
                                parts = current_block[1].split(':', 1)  # Split each line into two parts based on the first colon
                            ln_col = parts[0].split(',')   # Split each line into two parts based on comma
                            line_num = int(ln_col[0])         # line number
                            column_num = int(ln_col[1])        # column number
                            text_line_num = line_num
                            if text_line_num>appx_main_start_line:
                                cursor_position = str(line_num) + " " + str(column_num)
                                resulted_prefix = find_prefix(sc_file_name, line_num, column_num)
                                # print(cursor_position, "\n",resulted_prefix, "\n")
                        # Reset the current block
                        current_block = []
                        break

                    if len(parts) >= 2:  # Check if 'parts' contains at least two elements
                        text_candi = text_candi +" "+ parts[1].strip()  # Append the second part (after colon) to the result string
                    # Append the current line to the block
                    current_block.append(content_line)
                text_candi = text_candi.replace("VARIABLE", "").replace(" ", "")
                if prog_lan == "C11":        
                    if text_line_num>appx_main_start_line and struct_candi != "VARIABLE":
                     resultlist.append([state, cursor_position, resulted_prefix, struct_candi, text_candi])  # state, structural candidate, textual candidate
                elif prog_lan == "Small Basic":
                    resultlist.append([state, cursor_position, resulted_prefix, struct_candi, text_candi])  # state, structural candidate, textual candidate
            # Initialize variables before they are used
            total_sequenceMatcher_similarity_with_candidate = 0
            total_sequenceMatcher_similarity_without_candidate = 0
            total_precision_with_candidate = 0
            total_precision_without_candidate = 0
            num_iterations = 0 
            # start_time1 = time.time() 
            for index, (state, cursor_position, resulted_prefix, struct_candi, text_candi) in enumerate(resultlist, start=1):
                # print (state, cursor_position, resulted_prefix, struct_candi, "text_candidate: ", text_candi, "\n")
                start_time = 0
                end_time = 0
                # Candidate Data Collection
                def extract_state_data(filename, target_state):
                    with open(filename, 'r') as file:
                        lines = file.readlines()

                    start_extracting = False
                    extracted_data = []
                    target_state_str = f"State {target_state}"
                    data_pattern = re.compile(r'\[.*?\] : \d+')  # Pattern to match the lines with the data format
                    i = 1
                    state_found = False
                    
                    for line in lines:
                        line = line.strip()

                        # Check if we encounter the target state
                        if line == target_state_str:
                            state_found = True  # Mark the state as found
                            start_extracting = True
                            continue

                        # If we encounter a new state without finding data yet, keep looking until we hit data
                        if line.startswith("State") and start_extracting and not extracted_data:
                            continue
                        
                        # Stop extracting when we hit the next state *after* collecting relevant data
                        if line.startswith("State") and extracted_data:
                            break

                        # Collect the data only if it matches the required pattern
                        if start_extracting and data_pattern.match(line):
                            extracted_data.append(f"{i}: {line}")
                            i += 1

                    # If no data was found for the exact state but there is data further along (e.g., State 5 data)
                    if state_found and not extracted_data:
                        for line in lines:
                            line = line.strip()
                            if data_pattern.match(line):
                                extracted_data.append(f"{i}: {line}")
                                i += 1

                    return extracted_data

                # Usage
                state_number = state
                filename = "c11-data-state-collection.txt"
                state_data = extract_state_data(filename, state_number)
                # Candidate Data Collection end               
                # Split the string by space and period---------------Word Modification-----------------------------------------
                words = struct_candi.split()
                # Replace 'ID' with 'Identifier' and 'STR' with 'String' and so on...
                modified_words = ['Identifier' if word == 'ID' else 'String' if word == 'STR' else 'Number' if word == 'NUM' else 'Expression' if word == 'Exprs' else 'Expression' if word == 'Expr' else word for word in words]
                modified_struct_candi = ' '.join(modified_words)
                # print(index, state, resulted_prefix, " | ", modified_struct_candi, " | ", text_candi)
                print ("\nParse State: ", state, " Cursor Position: ", cursor_position, "\n")

                # Define the prompt with Candidate Guidance-------------------------------------------------------------
                prompt1 = f"""
                This is the incomplete {prog_lan} programming language code:
                {resulted_prefix}
                '{modified_struct_candi}'
                Complete the '{modified_struct_candi}' part of the code **once** per response. Do not include more than one completion in each response.. 
                """ 
                # ----Prompt Without Candidate Guidance----------
                prompt2 = f"""
                This is the incomplete {prog_lan} programming language code:
                {resulted_prefix}
                'next token or line'
                Complete the 'next token or line' part of the code **once** per response. Do not include more than one completion in each response. 
                """
                print (prompt1)
                chat_completion = client.chat.completions.create(
                    model="gpt-3.5-turbo-0125",
                    max_tokens=100,
                    messages=[
                         {
                            "role": "system",
                            "content": """
                                  This is the C Programming Language Grammar:
                            typedef_name -> NAME TYPE
                            var_name -> NAME VARIABLE
                            typedef_name_spec -> typedef_name
                            general_identifier -> typedef_name
                            general_identifier -> var_name
                            save_context -> 
                            scoped_parameter_type_list -> save_context parameter_type_list
                            scoped_compound_statement -> save_context compound_statement
                            scoped_selection_statement -> save_context selection_statement
                            scoped_iteration_statement -> save_context iteration_statement
                            scoped_statement -> save_context statement
                            scoped_parameter_type_list -> save_context parameter_type_list
                            declarator_varname -> declarator
                            declarator_typedefname -> declarator
                            primary_expression -> var_name
                            primary_expression -> CONSTANT
                            primary_expression -> STRING_LITERAL
                            primary_expression -> ( expression )
                            primary_expression -> generic_selection
                            generic_selection -> _Generic ( assignment_expression , generic_assoc_list )
                            generic_assoc_list -> generic_association
                            generic_assoc_list -> generic_assoc_list , generic_association
                            generic_association -> type_name : assignment_expression
                            generic_association -> default : assignment_expression
                            postfix_expression -> primary_expression
                            postfix_expression -> postfix_expression [ expression ]
                            postfix_expression -> postfix_expression ( option_argument_expression_list )
                            postfix_expression -> __builtin_va_arg ( assignment_expression , type_name )
                            postfix_expression -> postfix_expression . general_identifier
                            postfix_expression -> postfix_expression -> general_identifier
                            postfix_expression -> postfix_expression ++
                            postfix_expression -> postfix_expression --
                            postfix_expression -> ( type_name ) { initializer_list option_comma }
                            argument_expression_list -> assignment_expression
                            argument_expression_list -> argument_expression_list , assignment_expression
                            unary_expression -> postfix_expression
                            unary_expression -> ++ unary_expression
                            unary_expression -> -- unary_expression
                            unary_expression -> unary_operator cast_expression
                            unary_expression -> sizeof unary_expression
                            unary_expression -> sizeof ( type_name )
                            unary_expression -> _Alignof ( type_name )
                            unary_operator -> &
                            unary_operator -> *
                            unary_operator -> +
                            unary_operator -> -
                            unary_operator -> ~
                            unary_operator -> !
                            cast_expression -> unary_expression
                            cast_expression -> ( type_name ) cast_expression
                            multiplicative_operator -> *
                            multiplicative_operator -> /
                            multiplicative_operator -> %
                            multiplicative_expression -> cast_expression
                            multiplicative_expression -> multiplicative_expression multiplicative_operator cast_expression
                            additive_operator -> +
                            additive_operator -> -
                            additive_expression -> multiplicative_expression
                            additive_expression -> additive_expression additive_operator multiplicative_expression
                            shift_operator -> <<
                            shift_operator -> >>
                            shift_expression -> additive_expression
                            shift_expression -> shift_expression shift_operator additive_expression
                            relational_operator -> <
                            relational_operator -> >
                            relational_operator -> <=
                            relational_operator -> >=
                            relational_expression -> shift_expression
                            relational_expression -> relational_expression relational_operator shift_expression
                            equality_operator -> ==
                            equality_operator -> !=
                            equality_expression -> relational_expression
                            equality_expression -> equality_expression equality_operator relational_expression
                            and_expression -> equality_expression
                            and_expression -> and_expression & equality_expression
                            exclusive_or_expression -> and_expression
                            exclusive_or_expression -> exclusive_or_expression ^ and_expression
                            inclusive_or_expression -> exclusive_or_expression
                            inclusive_or_expression -> inclusive_or_expression | exclusive_or_expression
                            logical_and_expression -> inclusive_or_expression
                            logical_and_expression -> logical_and_expression && inclusive_or_expression
                            logical_or_expression -> logical_and_expression
                            logical_or_expression -> logical_or_expression || logical_and_expression
                            conditional_expression -> logical_or_expression
                            conditional_expression -> logical_or_expression ? expression : conditional_expression
                            assignment_expression -> conditional_expression
                            assignment_expression -> unary_expression assignment_operator assignment_expression
                            assignment_operator -> =
                            assignment_operator -> *=
                            assignment_operator -> /=
                            assignment_operator -> %=
                            assignment_operator -> +=
                            assignment_operator -> -=
                            assignment_operator -> <<=
                            assignment_operator -> >>=
                            assignment_operator -> &=
                            assignment_operator -> ^=
                            assignment_operator -> |=
                            expression -> assignment_expression
                            expression -> expression , assignment_expression
                            constant_expression -> conditional_expression
                            declaration -> declaration_specifiers option_init_declarator_list_declarator_varname ;
                            declaration -> declaration_specifiers_typedef option_init_declarator_list_declarator_typedefname ;
                            declaration -> static_assert_declaration
                            declaration_specifier -> storage_class_specifier
                            declaration_specifier -> type_qualifier
                            declaration_specifier -> function_specifier
                            declaration_specifier -> alignment_specifier
                            declaration_specifiers -> list_eq1_type_specifier_unique_declaration_specifier
                            declaration_specifiers -> list_ge1_type_specifier_nonunique_declaration_specifier
                            declaration_specifiers_typedef -> list_eq1_eq1_typedef_type_specifier_unique_declaration_specifier
                            declaration_specifiers_typedef -> list_eq1_ge1_typedef_type_specifier_nonunique_declaration_specifier
                            init_declarator_list_declarator_varname -> init_declarator_declarator_varname
                            init_declarator_list_declarator_varname -> init_declarator_list_declarator_varname , init_declarator_declarator_varname
                            init_declarator_list_declarator_typedefname -> init_declarator_declarator_typedefname
                            init_declarator_list_declarator_typedefname -> init_declarator_list_declarator_typedefname , init_declarator_declarator_typedefname
                            init_declarator_declarator_varname -> declarator_varname
                            init_declarator_declarator_varname -> declarator = c_initializer
                            init_declarator_declarator_typedefname -> declarator_typedefname
                            init_declarator_declarator_typedefname -> declarator = c_initializer
                            storage_class_specifier -> extern
                            storage_class_specifier -> static
                            storage_class_specifier -> _Thread_local
                            storage_class_specifier -> auto
                            storage_class_specifier -> register
                            type_specifier_nonunique -> char
                            type_specifier_nonunique -> short
                            type_specifier_nonunique -> int
                            type_specifier_nonunique -> long
                            type_specifier_nonunique -> float
                            type_specifier_nonunique -> double
                            type_specifier_nonunique -> signed
                            type_specifier_nonunique -> unsigned
                            type_specifier_nonunique -> _Complex
                            type_specifier_unique -> void
                            type_specifier_unique -> _Bool
                            type_specifier_unique -> atomic_type_specifier
                            type_specifier_unique -> struct_or_union_specifier
                            type_specifier_unique -> enum_specifier
                            type_specifier_unique -> typedef_name_spec
                            struct_or_union_specifier -> struct_or_union option_general_identifier { struct_declaration_list }
                            struct_or_union_specifier -> struct_or_union general_identifier
                            struct_or_union -> struct
                            struct_or_union -> union
                            struct_declaration_list -> struct_declaration
                            struct_declaration_list -> struct_declaration_list struct_declaration
                            struct_declaration -> specifier_qualifier_list option_struct_declarator_list ;
                            struct_declaration -> static_assert_declaration
                            specifier_qualifier_list -> list_eq1_type_specifier_unique_type_qualifier
                            specifier_qualifier_list -> list_eq1_type_specifier_unique_alignment_specifier
                            specifier_qualifier_list -> list_ge1_type_specifier_nonunique_type_qualifier
                            specifier_qualifier_list -> list_ge1_type_specifier_nonunique_alignment_specifier
                            struct_declarator_list -> struct_declarator
                            struct_declarator_list -> struct_declarator_list , struct_declarator
                            struct_declarator -> declarator
                            struct_declarator -> option_declarator : constant_expression
                            enum_specifier -> enum option_general_identifier { enumerator_list option_comma }
                            enum_specifier -> enum general_identifier
                            enumerator_list -> enumerator
                            enumerator_list -> enumerator_list , enumerator
                            enumerator -> enumeration_constant
                            enumerator -> enumeration_constant = constant_expression
                            enumeration_constant -> general_identifier
                            atomic_type_specifier -> _Atomic ( type_name )
                            atomic_type_specifier -> _Atomic ATOMIC_LPAREN type_name )
                            type_qualifier -> const
                            type_qualifier -> restrict
                            type_qualifier -> volatile
                            type_qualifier -> _Atomic
                            function_specifier -> inline
                            function_specifier -> _Noreturn
                            alignment_specifier -> _Alignas ( type_name )
                            alignment_specifier -> _Alignas ( constant_expression )
                            declarator -> direct_declarator
                            declarator -> pointer direct_declarator
                            direct_declarator -> general_identifier
                            direct_declarator -> ( save_context declarator )
                            direct_declarator -> direct_declarator [ option_type_qualifier_list option_assignment_expression ]
                            direct_declarator -> direct_declarator [ static option_type_qualifier_list assignment_expression ]
                            direct_declarator -> direct_declarator [ type_qualifier_list static assignment_expression ]
                            direct_declarator -> direct_declarator [ option_type_qualifier_list * ]
                            direct_declarator -> direct_declarator ( scoped_parameter_type_list )
                            direct_declarator -> direct_declarator ( save_context option_identifier_list )
                            pointer -> * option_type_qualifier_list option_pointer
                            type_qualifier_list -> option_type_qualifier_list type_qualifier
                            parameter_type_list -> parameter_list option_comma_dotdotdot save_context
                            parameter_list -> parameter_declaration
                            parameter_list -> parameter_list , parameter_declaration
                            parameter_declaration -> declaration_specifiers declarator_varname
                            parameter_declaration -> declaration_specifiers option_abstract_declarator
                            identifier_list -> var_name
                            identifier_list -> identifier_list , var_name
                            type_name -> specifier_qualifier_list option_abstract_declarator
                            abstract_declarator -> pointer
                            abstract_declarator -> direct_abstract_declarator
                            abstract_declarator -> pointer direct_abstract_declarator
                            direct_abstract_declarator -> ( save_context abstract_declarator )
                            direct_abstract_declarator -> option_direct_abstract_declarator [ option_assignment_expression ]
                            direct_abstract_declarator -> option_direct_abstract_declarator [ type_qualifier_list option_assignment_expression ]
                            direct_abstract_declarator -> option_direct_abstract_declarator [ static option_type_qualifier_list assignment_expression ]
                            direct_abstract_declarator -> option_direct_abstract_declarator [ type_qualifier_list static assignment_expression ]
                            direct_abstract_declarator -> option_direct_abstract_declarator [ * ]
                            direct_abstract_declarator -> ( option_scoped_parameter_type_list )
                            direct_abstract_declarator -> direct_abstract_declarator ( option_scoped_parameter_type_list )
                            c_initializer -> assignment_expression
                            c_initializer -> { initializer_list option_comma }
                            initializer_list -> option_designation c_initializer
                            initializer_list -> initializer_list , option_designation c_initializer
                            designation -> designator_list =
                            designator_list -> option_designator_list designator
                            designator -> [ constant_expression ]
                            designator -> . general_identifier
                            static_assert_declaration -> _Static_assert ( constant_expression , STRING_LITERAL ) ;
                            statement -> labeled_statement
                            statement -> scoped_compound_statement
                            statement -> expression_statement
                            statement -> scoped_selection_statement
                            statement -> scoped_iteration_statement
                            statement -> jump_statement
                            labeled_statement -> general_identifier : statement
                            labeled_statement -> case constant_expression : statement
                            labeled_statement -> default : statement
                            compound_statement -> { option_block_item_list }
                            block_item_list -> option_block_item_list block_item
                            block_item -> declaration
                            block_item -> statement
                            expression_statement -> option_expression ;
                            selection_statement -> if ( expression ) scoped_statement else scoped_statement
                            selection_statement -> if ( expression ) scoped_statement
                            selection_statement -> switch ( expression ) scoped_statement
                            iteration_statement -> while ( expression ) scoped_statement
                            iteration_statement -> do scoped_statement while ( expression ) ;
                            iteration_statement -> for ( option_expression ; option_expression ; option_expression ) scoped_statement
                            iteration_statement -> for ( declaration option_expression ; option_expression ) scoped_statement
                            jump_statement -> goto general_identifier ;
                            jump_statement -> continue ;
                            jump_statement -> break ;
                            jump_statement -> return option_expression ;
                            translation_unit_file -> external_declaration translation_unit_file
                            translation_unit_file -> external_declaration $
                            external_declaration -> function_definition
                            external_declaration -> declaration
                            function_definition1 -> declaration_specifiers declarator_varname
                            function_definition -> function_definition1 option_declaration_list compound_statement
                            declaration_list -> declaration
                            declaration_list -> declaration_list declaration
                            option_argument_expression_list -> 
                            option_argument_expression_list -> argument_expression_list
                            option_comma -> 
                            option_comma -> ,
                            option_comma_dotdotdot -> 
                            option_comma_dotdotdot -> , ...
                            option_init_declarator_list_declarator_varname -> 
                            option_init_declarator_list_declarator_varname -> init_declarator_list_declarator_varname
                            option_init_declarator_list_declarator_typedefname -> 
                            option_init_declarator_list_declarator_typedefname -> init_declarator_list_declarator_typedefname
                            option_general_identifier -> 
                            option_general_identifier -> general_identifier
                            option_struct_declarator_list -> 
                            option_struct_declarator_list -> struct_declarator_list
                            option_declarator -> 
                            option_declarator -> declarator
                            option_general_identifier -> 
                            option_general_identifier -> general_identifier
                            option_type_qualifier_list -> 
                            option_type_qualifier_list -> type_qualifier_list
                            option_assignment_expression -> 
                            option_assignment_expression -> assignment_expression
                            option_type_qualifier_list -> 
                            option_type_qualifier_list -> type_qualifier_list
                            option_identifier_list -> 
                            option_identifier_list -> identifier_list
                            option_pointer -> 
                            option_pointer -> pointer
                            option_abstract_declarator -> 
                            option_abstract_declarator -> abstract_declarator
                            option_direct_abstract_declarator -> 
                            option_direct_abstract_declarator -> direct_abstract_declarator
                            option_assignment_expression -> 
                            option_assignment_expression -> assignment_expression
                            option_scoped_parameter_type_list -> 
                            option_scoped_parameter_type_list -> scoped_parameter_type_list
                            option_designation -> 
                            option_designation -> designation
                            option_designator_list -> 
                            option_designator_list -> designator_list
                            option_block_item_list -> 
                            option_block_item_list -> block_item_list
                            option_expression -> 
                            option_expression -> expression
                            option_declaration_list -> 
                            option_declaration_list -> declaration_list
                            list_eq1_type_specifier_unique_declaration_specifier -> type_specifier_unique list_declaration_specifier
                            list_eq1_type_specifier_unique_declaration_specifier -> declaration_specifier list_eq1_type_specifier_unique_declaration_specifier
                            list_declaration_specifier -> 
                            list_declaration_specifier -> declaration_specifier list_declaration_specifier
                            list_eq1_type_specifier_unique_type_qualifier -> type_specifier_unique list_type_qualifier
                            list_eq1_type_specifier_unique_type_qualifier -> type_qualifier list_eq1_type_specifier_unique_type_qualifier
                            list_type_qualifier -> 
                            list_type_qualifier -> type_qualifier list_type_qualifier
                            list_eq1_type_specifier_unique_alignment_specifier -> type_specifier_unique list_alignment_specifier
                            list_eq1_type_specifier_unique_alignment_specifier -> alignment_specifier list_eq1_type_specifier_unique_alignment_specifier
                            list_alignment_specifier -> 
                            list_alignment_specifier -> alignment_specifier list_alignment_specifier
                            list_ge1_type_specifier_nonunique_declaration_specifier -> type_specifier_nonunique list_declaration_specifier
                            list_ge1_type_specifier_nonunique_declaration_specifier -> type_specifier_nonunique list_ge1_type_specifier_nonunique_declaration_specifier
                            list_ge1_type_specifier_nonunique_declaration_specifier -> declaration_specifier list_ge1_type_specifier_nonunique_declaration_specifier
                            list_declaration_specifier -> 
                            list_declaration_specifier -> declaration_specifier list_declaration_specifier
                            list_ge1_type_specifier_nonunique_type_qualifier -> type_specifier_nonunique list_type_qualifier
                            list_ge1_type_specifier_nonunique_type_qualifier -> type_specifier_nonunique list_ge1_type_specifier_nonunique_type_qualifier
                            list_ge1_type_specifier_nonunique_type_qualifier -> type_qualifier list_ge1_type_specifier_nonunique_type_qualifier
                            list_type_qualifier -> 
                            list_type_qualifier -> type_qualifier list_type_qualifier
                            list_ge1_type_specifier_nonunique_alignment_specifier -> type_specifier_nonunique list_alignment_specifier
                            list_ge1_type_specifier_nonunique_alignment_specifier -> type_specifier_nonunique list_ge1_type_specifier_nonunique_alignment_specifier
                            list_ge1_type_specifier_nonunique_alignment_specifier -> alignment_specifier list_ge1_type_specifier_nonunique_alignment_specifier
                            list_alignment_specifier -> 
                            list_alignment_specifier -> alignment_specifier list_alignment_specifier
                            list_eq1_eq1_typedef_type_specifier_unique_declaration_specifier -> typedef list_eq1_type_specifier_unique_declaration_specifier
                            list_eq1_eq1_typedef_type_specifier_unique_declaration_specifier -> type_specifier_unique list_eq1_typedef_declaration_specifier
                            list_eq1_eq1_typedef_type_specifier_unique_declaration_specifier -> declaration_specifier list_eq1_eq1_typedef_type_specifier_unique_declaration_specifier
                            list_eq1_type_specifier_unique_declaration_specifier -> type_specifier_unique list_declaration_specifier
                            list_eq1_type_specifier_unique_declaration_specifier -> declaration_specifier list_eq1_type_specifier_unique_declaration_specifier
                            list_eq1_typedef_declaration_specifier -> typedef list_declaration_specifier
                            list_eq1_typedef_declaration_specifier -> declaration_specifier list_eq1_typedef_declaration_specifier
                            list_eq1_ge1_typedef_type_specifier_nonunique_declaration_specifier -> typedef list_ge1_type_specifier_nonunique_declaration_specifier
                            list_eq1_ge1_typedef_type_specifier_nonunique_declaration_specifier -> type_specifier_nonunique list_eq1_typedef_declaration_specifier
                            list_eq1_ge1_typedef_type_specifier_nonunique_declaration_specifier -> type_specifier_nonunique list_eq1_ge1_typedef_type_specifier_nonunique_declaration_specifier
                            list_eq1_ge1_typedef_type_specifier_nonunique_declaration_specifier -> declaration_specifier list_eq1_ge1_typedef_type_specifier_nonunique_declaration_specifier
                            list_ge1_type_specifier_nonunique_declaration_specifier -> type_specifier_nonunique list_declaration_specifier
                            list_ge1_type_specifier_nonunique_declaration_specifier -> type_specifier_nonunique list_ge1_type_specifier_nonunique_declaration_specifier
                            list_ge1_type_specifier_nonunique_declaration_specifier -> declaration_specifier list_ge1_type_specifier_nonunique_declaration_specifier
                            list_eq1_typedef_declaration_specifier -> typedef list_declaration_specifier
                            list_eq1_typedef_declaration_specifier -> declaration_specifier list_eq1_typedef_declaration_specifier
                            """            
                         },
                        {
                            "role": "system",
                            "content": "Replace the single quotation ('') with your response."
                         },
                         {
                            "role": "user",
                            "content": """This is the incomplete C11 programming language code:
                            upper = 300;
                            step = 20;

                            printf("Celsius\tFahr\n");
                            printf("---------------\n");

                            for (celsius = upper; celsius >= lower; celsius = celsius - step)
                            {
                                fahr = (9.0 / 5.0) * celsius + 32.0f;
                                printf("%3.0f\t\t%6.1f\n", celsius,
                            'NAME VARIABLE'
                            Complete the 'NAME VARIABLE' part of the code in the C11 programming language. Just show your answer in place of 'NAME VARIABLE'. """
                         },
                        {
                            "role": "assistant",
                            "content": "fahr"
                        },
                                                 {
                            "role": "user",
                            "content": """This is the incomplete C11 programming language code:
                            fahr = lower;
                            while (fahr <= upper)
                            {
                                celsius = (5.0 / 9.0) * (fahr - 32.0);
                                printf("%3.0f\t\t%6.1f\n", fahr, celsius);
                                fahr = fahr + step;
                            }
                            'return option_expression ;'
                            Complete the 'return option_expression ;' part of the code in the C11 programming language. Just show your answer in place of 'return option_expression ;'."""
                         },
                        {
                            "role": "assistant",
                            "content": """ return 0;"""
                        },
                    ]
                )
                res = chat_completion.choices[0].message.content
                print("\nResponse:", res)
                # Send the query and measure time----------------------------------------------------------------
                start_time = time.time()
                chat_completion1 = client.chat.completions.create(
                    model="gpt-3.5-turbo-0125",
                    max_tokens=70,
                    n=3,  # Request 3 separate completions
                    messages=[
                        {
                            "role": "user",
                            "content": prompt1
                        },
                    ]
                )
                end_time = time.time()
                chat_completion2 = client.chat.completions.create(
                    model="gpt-3.5-turbo-0125",
                    max_tokens=70,
                    n=3,  # Request 3 separate completions
                    messages=[
                        {
                            "role": "user",
                            "content": prompt2
                        },
                    ]
                )
                # Calculate the time taken
                query_time = end_time - start_time
                print("\nTime taken:", query_time, "seconds\n")

                # Get the response
                response1 = [choice.message.content for choice in chat_completion1.choices]
                print("Received response with candidate:", response1)

                response2 = [choice.message.content for choice in chat_completion2.choices]
                print("Received response without candidate:", response2)

                # Prepare lists to store scores
                sacrebleu_scores = []
                sequence_matcher_scores = []
                # Process each response for scores
                for i in range(3):  # Assuming 3 responses for each prompt
                    # Calculate scores for response1
                    score1 = sacrebleu.compute(predictions=[response1[i]], references=[text_candi])
                    sequence_similarity1 = SequenceMatcher(None, response1[i], text_candi).ratio()
                    sacrebleu_scores.append((score1, i + 1))  # Store score and response index
                    sequence_matcher_scores.append((sequence_similarity1, i + 1))  # Store similarity and response index
                    
                    # Calculate scores for response2
                    score2 = sacrebleu.compute(predictions=[response2[i]], references=[text_candi])
                    sequence_similarity2 = SequenceMatcher(None, response2[i], text_candi).ratio()
                    sacrebleu_scores.append((score2, i + 1 + 3))  # Store score and response index for response2
                    sequence_matcher_scores.append((sequence_similarity2, i + 1 + 3))  # Store similarity and response index
                num_iterations += 1
                total_sequenceMatcher_similarity_with_candidate+=sequence_matcher_scores[0][0]
                total_sequenceMatcher_similarity_without_candidate+=sequence_matcher_scores[3][0]
                # Output Results
                parent_folder = "Result"
                if prog_lan == "C11":
                    text_file_name = file_name.replace('./C11_Text_Cand/',"").replace('.i.textual_collection.txt',"")
                elif prog_lan == "Small Basic":
                  text_file_name = sc_file_name.replace('./SB_Sample/',"").replace('.sb',"")
                text_file_name +="_result.txt"
                # Create the parent folder if it doesn't exist
                if not os.path.exists(parent_folder):
                   os.makedirs(parent_folder)
                # Define the folder path for the child folder inside the parent folder
                file_path = os.path.join(parent_folder, text_file_name)
                # Write results to the file
                with open(file_path, "a") as file:
                    file.write("Parse State: {}\tCursor Position: {}\nCandidate List: {}\n{}Time taken: {} seconds\n".format(
                        state, cursor_position, state_data, "", query_time))
                    
                    file.write("{}".format(prompt1))
                    # Write responses and their scores for prompt 1
                    for i in range(3):
                        file.write("\nReceived response with candidate {}: {}\n".format(i + 1, response1[i]))
                        # Access the SACREBLEU score dictionary
                        score_details = sacrebleu_scores[i][0]
                        # Write SACREBLEU score and other details
                        file.write("SACREBLEU score {}: {} ".format(i + 1, score_details['score']))
                        file.write("Counts: {} ".format(score_details['counts']))
                        file.write("Totals: {} ".format(score_details['totals']))
                        file.write("Precisions: {} ".format(score_details['precisions']))
                        file.write("System length: {} ".format(score_details['sys_len']))
                        file.write("Reference length: {} ".format(score_details['ref_len']))
                        file.write("\nFirst element of precision: {} ".format(score_details['precisions'][0]))
                        # Write SequenceMatcher score
                        file.write("\nSequenceMatcher Score{}: {:.2f}\n".format(i + 1, sequence_matcher_scores[i][0]))

                    file.write("{}".format(prompt2))
                    # Write responses and their scores for prompt 2
                    for i in range(3):
                        # Write the response without candidate
                        file.write("\nReceived response without candidate {}: {}\n".format(i + 1, response2[i]))
                        
                        # Access the SACREBLEU score dictionary for responses without candidate (offset by 3)
                        score_details = sacrebleu_scores[i + 3][0]  # +3 for the second prompt
                        
                        # Write SACREBLEU score and other details
                        file.write("SACREBLEU score {}: {} ".format(i + 1 + 3, score_details['score']))
                        file.write("Counts: {} ".format(score_details['counts']))
                        file.write("Totals: {} ".format(score_details['totals']))
                        file.write("Precisions: {} ".format(score_details['precisions']))
                        file.write("System length: {} ".format(score_details['sys_len']))
                        file.write("Reference length: {} ".format(score_details['ref_len']))
                        file.write("\nFirst element of precision: {} ".format(score_details['precisions'][0]))
                        # Write SequenceMatcher score
                        file.write("\nSequenceMatcher Score{}: {:.2f}\n".format(i + 1 + 3, sequence_matcher_scores[i + 3][0]))

                    # Write the actual result
                    file.write("Actual result: {}\n\n".format(text_candi))
                    # Calculate average precision        
                    total_precision_with_candidate += sacrebleu_scores[0][0]["precisions"][0]  # First response of prompt 1
                    total_precision_without_candidate += sacrebleu_scores[3][0]["precisions"][0]  # First response of prompt 2
            average_precision_with_candidate = total_precision_with_candidate / num_iterations  # Only the first response
            average_precision_without_candidate = total_precision_without_candidate / num_iterations  # Only the first response

            # Calculate averages for Sequence Matcher similarity
            average_sequenceMatcher_similarity_with_candidate = (total_sequenceMatcher_similarity_with_candidate/num_iterations)*100
            average_sequenceMatcher_similarity_without_candidate = (total_sequenceMatcher_similarity_without_candidate/num_iterations)*100
            # Output averages
            print("\nAverage Precision with Candidate Guidance:", average_precision_with_candidate)
            print("\nAverage Precision without Candidate Guidance:", average_precision_without_candidate)
            print("\nAverage Sequence Matcher Similarity with Candidate Guidance:", average_sequenceMatcher_similarity_with_candidate)
            print("\nAverage Sequence Matcher Similarity without Candidate Guidance:", average_sequenceMatcher_similarity_without_candidate)
            # Write average precisions
            with open(file_path, "a") as file:
                file.write("Average Precision with Candidate Guidance: {}\n".format(average_precision_with_candidate))
                file.write("Average Precision without Candidate Guidance: {}\n".format(average_precision_without_candidate))
                file.write("Average Sequence Matcher Similarity with Candidate Guidance: {}\n".format(average_sequenceMatcher_similarity_with_candidate))
                file.write("Average Sequence Matcher Similarity without Candidate Guidance: {}\n".format(average_sequenceMatcher_similarity_without_candidate))                   

    except FileNotFoundError:
        print("File not found:", file_name)
        
data_folder = './C11_Text_Cand'
sample_folder = './C11_Sample'
prog_lan = "C11"
encoding = 'utf-8'

# List all files in the C11_Text_Cand folder
for data_file in os.listdir(data_folder):
    if data_file.endswith('.i.textual_collection.txt'):
        # Get the base file name without the '.txt' extension but keep '.i.textual_collection'
        base_name = data_file.replace('.textual_collection.txt', '')  # Removes the '.textual_collection.txt' part
        
        # Construct the corresponding file path in the C11_Sample folder
        sample_file_path = os.path.join(sample_folder, base_name).replace("\\", "/")
        
        # Construct the data file path (keeping the full original name)
        data_file_path = os.path.join(data_folder, data_file).replace("\\", "/")
    
        # Check if the corresponding file exists in the sample folder
        if os.path.exists(sample_file_path):
            read_data(data_file_path, sample_file_path, prog_lan, encoding)
        else:
            print(f"Warning: No corresponding file found for {sample_file_path}")





