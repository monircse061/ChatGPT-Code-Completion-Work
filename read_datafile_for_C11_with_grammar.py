from openai import OpenAI
import sys
import time
import evaluate
import os
from difflib import SequenceMatcher
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from tenacity import retry, wait_random_exponential, stop_after_attempt
# Load SACREBLEU metric using evaluate.load
sacrebleu = evaluate.load("sacrebleu")
# # ----------Hide API-Start---------------------------
# # Retrieve API key from environment variable
# api_key = os.environ.get("OPENAI_API_KEY")

# if api_key is None:
#     raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY environment variable.")

# client = OpenAI(api_key=api_key)
# # ----------Hide API-End---------------------------
# Initialize OpenAI client 
client = OpenAI(api_key="Your_API_KEY")
request_count = 0  # Counter for requests made (RPD calculation)
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

                if prog_lan == "C11":        
                    if text_line_num>appx_main_start_line:
                     resultlist.append([state, cursor_position, resulted_prefix, struct_candi, text_candi])  # state, structural candidate, textual candidate
                elif prog_lan == "Small Basic":
                    resultlist.append([state, cursor_position, resulted_prefix, struct_candi, text_candi])  # state, structural candidate, textual candidate
            total_precision = 0 
            total_sequenceMatcher_similarity = 0
            total_cosign_similarity = 0
            num_iterations = 0 
            # start_time1 = time.time() 
            for index, (state, cursor_position, resulted_prefix, struct_candi, text_candi) in enumerate(resultlist, start=1):
                # print (state, cursor_position, resulted_prefix, struct_candi, "text_candidate: ", text_candi, "\n")
                start_time = 0
                end_time = 0
                # Split the string by space and period---------------Word Modification-----------------------------------------
                words = struct_candi.split()
                # Replace 'ID' with 'Identifier' and 'STR' with 'String' and so on...
                modified_words = ['Identifier' if word == 'ID' else 'String' if word == 'STR' else 'Number' if word == 'NUM' else 'Expression' if word == 'Exprs' else 'Expression' if word == 'Expr' else word for word in words]
                modified_struct_candi = ' '.join(modified_words)
                # print(index, state, resulted_prefix, " | ", modified_struct_candi, " | ", text_candi)
                print ("\nParse State: ", state, " Cursor Position: ", cursor_position, "\n")
                # if time.time() - start_time1 >= 60:
                #   print("Pausing for a moment.")
                #   time.sleep(30)  
                #   start_time1 = time.time()
                # Define the prompt-------------------------------------------------------------
                prompt = f"""
                This is the incomplete {prog_lan} programming language code:
                {resulted_prefix}
                '{modified_struct_candi}'
                Complete the '{modified_struct_candi}' part of the code in the {prog_lan} programming language. Just show your answer in place of '{modified_struct_candi}'. 
                """ #Complete just the content of the curly brace (inside) part of the '{modified_struct_candi}'. Do not produce curly brace in the output.
                # ----Prompt Without Candidate Guidance----------
                # prompt = f"""
                # This is the incomplete {prog_lan} programming language code:
                # {resulted_prefix}
                # 'next token or line'
                # Complete the 'next token or line' part of the code in the {prog_lan} programming language. Just show your answer in place of 'next token or line'. 
                # """
                print (prompt)
                chat_completion = client.chat.completions.create(
                    model="gpt-3.5-turbo-0125",
                    max_tokens=50,
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
                response1 = chat_completion.choices[0].message.content
                print("\nResponse:", response1)
                # Send the query and measure time----------------------------------------------------------------
                start_time = time.time()
                chat_completion = client.chat.completions.create(
                    model="gpt-3.5-turbo-0125",
                    max_tokens=50,
                    messages=[
                        #  {
                        #     "role": "assistant",
                        #     "content": """
                        #     This is the SmallBasic Programming Language Grammar:
                        #     Prog' -> Prog
                        #     Prog -> MoreThanOneStmt
                        #     Stmt -> ExprStatement
                        #     Stmt -> While Expr CRStmtCRs EndWhile
                        #     Stmt -> ID :
                        #     Stmt -> Goto ID
                        #     Stmt -> For ID = Expr To Expr OptStep CRStmtCRs EndFor
                        #     Stmt -> Sub ID CRStmtCRs EndSub
                        #     Stmt -> If Expr Then CRStmtCRs MoreThanZeroElseIf
                        #     Stmt ->
                        #     MoreThanZeroElseIf -> OptionalElse
                        #     MoreThanZeroElseIf -> ElseIf Expr Then CRStmtCRs MoreThanZeroElseIf
                        #     OptionalElse -> EndIf
                        #     OptionalElse -> Else CRStmtCRs EndIf
                        #     ExprStatement -> ID = Expr
                        #     ExprStatement -> ID . ID = Expr
                        #     ExprStatement -> ID . ID ( Exprs )
                        #     ExprStatement -> ID ( )
                        #     ExprStatement -> ID Idxs = Expr
                        #     CRStmtCRs -> CR TheRest
                        #     TheRest ->
                        #     TheRest -> Stmt CR TheRest
                        #     MoreThanOneStmt -> Stmt
                        #     MoreThanOneStmt -> Stmt CR MoreThanOneStmt
                        #     OptStep ->
                        #     OptStep -> Step Expr
                        #     Expr -> CondExpr
                        #     Exprs ->
                        #     Exprs -> MoreThanOneExpr
                        #     MoreThanOneExpr -> Expr
                        #     MoreThanOneExpr -> Expr , MoreThanOneExpr
                        #     CondExpr -> OrExpr
                        #     OrExpr -> OrExpr Or AndExpr
                        #     OrExpr -> AndExpr
                        #     AndExpr -> AndExpr And EqNeqExpr
                        #     AndExpr -> EqNeqExpr
                        #     EqNeqExpr -> EqNeqExpr = CompExpr
                        #     EqNeqExpr -> EqNeqExpr <> CompExpr
                        #     EqNeqExpr -> CompExpr
                        #     CompExpr -> CompExpr < AdditiveExpr
                        #     CompExpr -> CompExpr <= AdditiveExpr
                        #     CompExpr -> CompExpr > AdditiveExpr
                        #     CompExpr -> CompExpr >= AdditiveExpr
                        #     CompExpr -> AdditiveExpr
                        #     AdditiveExpr -> AdditiveExpr + MultiplicativeExpr
                        #     AdditiveExpr -> AdditiveExpr - MultiplicativeExpr
                        #     AdditiveExpr -> MultiplicativeExpr
                        #     MultiplicativeExpr -> MultiplicativeExpr * UnaryExpr
                        #     MultiplicativeExpr -> MultiplicativeExpr / UnaryExpr
                        #     MultiplicativeExpr -> UnaryExpr
                        #     UnaryExpr -> - Primary
                        #     UnaryExpr -> Primary
                        #     Primary -> NUM
                        #     Primary -> STR
                        #     Primary -> ( Expr )
                        #     Primary -> ID
                        #     Primary -> ID . ID
                        #     Primary -> ID . ID ( Exprs )
                        #     Primary -> ID Idxs
                        #     Idxs -> [ Expr ]
                        #     Idxs -> [ Expr ] Idxs"""            
                        #  },
                        {
                            "role": "user",
                            "content": prompt
                        },
                        # {
                        #     "role": "assistant",
                        #     "content": f"Your answer should be in place of quotation ('')"
                        #  },
                    ]
                )
                end_time = time.time()
                # # Increment request count for RPD calculation
                # request_count += 1
                # print(f"\nRequest count so far (RPD): {request_count}\n")

                # Calculate the time taken
                query_time = end_time - start_time
                print("\nTime taken:", query_time, "seconds\n")

                # Get the response
                response = chat_completion.choices[0].message.content
                print("Received response:", response)
                # # Extract token usage
                # token_usage = chat_completion.usage
                # prompt_tokens += token_usage.prompt_tokens
                # completion_tokens += token_usage.completion_tokens
                # total_tokens += token_usage.total_tokens
                # # Print token usage
                # print(f"\nToken Usage Details:\nPrompt Tokens: {prompt_tokens}\nCompletion Tokens: {completion_tokens}\nTotal Tokens: {total_tokens}\n")
                
                score = sacrebleu.compute(predictions=[response], references=[text_candi])
                print ("\nActual Result: ", text_candi)
                print("\nSACREBLEU Score:", score, "\n")    # ['score', 'counts', 'totals', 'precisions', 'bp', 'sys_len', 'ref_len']
                precision_first_element = score["precisions"][0]
                
                print("\nFirst element of precision:", precision_first_element, "\n")
                total_precision += precision_first_element
                sequence__similarity = SequenceMatcher(None, response, text_candi).ratio()
                print(f"SequenceMatcher Similarity: {sequence__similarity:.2f}\n")
                total_sequenceMatcher_similarity+=sequence__similarity
                if response.strip() and text_candi.strip():
                    try:
                        vectorizer = CountVectorizer(stop_words=None).fit_transform([response, text_candi])
                        vectors = vectorizer.toarray()
                        cos_sim = cosine_similarity(vectors)
                        cosign_similarity = cos_sim[0][1]
                        total_cosign_similarity += cosign_similarity
                        print(f"\nCosine Similarity: {cos_sim[0][1]:.2f}\n")
                    except ValueError as e:
                        print(f"Error in CountVectorizer: {e}\n")
                        print(f"Response: '{response}'\nText Candidate: '{text_candi}'\n")
                num_iterations += 1
                # -----store the prompt and the chatgpt answer in a new folder with a new file-----------------
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
                with open(file_path,"a") as file:
                   file.write("Parse State: {}\tCursor Position: {}\n{}Time taken: {} seconds\nReceived response: {}\nActual result: {}\nSACREBLEU Score: {}\nFirst element of precision:{}\nSequence Matcher Similarity Precision:{}\nCosine Similarity Precision:{}\n\n".format(state, cursor_position, prompt + "\n", query_time, response, text_candi, score, precision_first_element,sequence__similarity,cosign_similarity))
            average_precision = total_precision / num_iterations
            average_sequenceMatcher_similarity = (total_sequenceMatcher_similarity/num_iterations)*100
            average_cosign_similarity = (total_cosign_similarity/num_iterations)*100
            print("\nAverage Precision:", average_precision)
            print("\nAverage Sequence Matcher Similarity Precision:", average_sequenceMatcher_similarity)
            print("\nAverage Cosine Similarity Precision:", average_cosign_similarity)
            with open(file_path,"a") as file:
                file.write("\nAverage Precision: {}".format(average_precision))
                file.write("\nAverage Sequence Matcher Similarity Precision: {}".format(average_sequenceMatcher_similarity))
                file.write("\nAverage Cosine Similarity Precision: {}".format(average_cosign_similarity))
    except FileNotFoundError:
        print("File not found:", file_name)


# chat_completion = client.chat.completions.create(
#     model="gpt-3.5-turbo-0125",
#     messages=[
        # # Assistant message 1
        # {
        #     "role": "assistant",
        #     "content": """
        #             This is a SmallBasic Programming Language code:
        #             TextWindow.WriteLine(“Hello World”) is tokenized into a stream,
        #             ID . ID ( STR )
                    
        #             The term “TextWindow” is processed into an identifier represented by the terminal ID, while a text dot is interpreted as a terminal dot. 
        #             Similarly, “WriteLine” is analyzed like TextWindow. Open and close parentheses undergo the same procedure as the dot, and the string 
        #             literal "Hello World" is translated into the terminal STR. """
        # },
        # # Assistant message 2
        # {
        #     "role": "assistant",""
        #     "content": """What are structural candidates ?
        #                 TextWindow.WriteLine("Hello World")
                        
        #                 Production Rule: ExprStatement ->  ID . ID ( Exprs )
                        
        #                 For example, programmers have written “TextWindow.(dot)”. Currently cursor at this position after the dot. At this point, programmers want 
        #                 the editor to complete the rest of the part of this line of code. Then our system looks for the appropriate production rule. Next, our system 
        #                 gets the rest of the symbols from that production rule. Our system considered this part as a structural candidate. We ask the ChatGPT to decorate 
        #                 the structural candidate by giving the prefix what the programmer writes before asking for code suggestions and the structural candidate."""
        # },
        # # Assistant message 3
        # {
        #     "role": "assistant",""
        #     "content": """For instance,
        #                   number = 100
        #                   While(number>1)
        #                   TextWindow.WriteLine(number)
        #                 Suggestions: 
        #                   ID = Expr

        #                 In the above example, the suggestion at the cursor position is an assignment statement formatted as ID = Expr. 
        #                 Here, the terminal ID signifies an identifier, the terminal = represents an assignment symbol, and the non-terminal “Expr” indicates 
        #                 an expression. Further, the third example in Figure 1 delves deeper into the syntax structures of “Expr”  after users input an identifier, 
        #                 number, followed by an assignment symbol. In contrast, Microsoft SmallBasic does not provide any suggestions at the same cursor position 
        #                 until the user starts typing the initial character n. Only then do suggestions appear, revealing one variable name, number, and one class 
        #                 name, Network, both beginning with that character."""
        # },
        # # Assistant message 4
        # {
        #     "role": "assistant",""
        #     "content": """Terminal: A terminal symbol, also known as a terminal or token, is a basic unit of syntax in a programming language. Terminals are the smallest units that cannot be broken down further within the language's syntax rules.

        #     Identifier: An identifier is a name given to various programming language entities, such as variables, functions, classes, and labels. Identifiers serve as unique labels to refer to these entities within a program.

        #     Non-terminal: A non-terminal symbol represents a syntactic category that can be decomposed into other symbols according to the rules of the language's grammar.

        #     Expression: In programming languages, an expression is a combination of one or more operands (variables, constants, literals, function calls) and operators that can be evaluated to produce a value."""
        # },
        #  # Assistant message 5
        # {
        #     "role": "assistant",""
        #     "content": """ Problem statement: This is the incomplete SmallBasic programming language code:
        #        number = 100
        #        While(number>1)
        #        TextWindow
        #        'ID (Expr)'
        #        Complete the 'ID (Expr)' part of the code in the SmallBasic programming language.                    
        #        Just show your answer in place of 'ID (Expr)'. 
               
        #        Your solution: .WriteLine(number)

        #        Expected solution: .WriteLine(number) """
        # },
          # Assistant message 6
        # {
        #     "role": "assistant",""
        #     "content": """  This is the SmallBasic Programming Language Grammar:
        #                     Prog' -> Prog
        #                     Prog -> MoreThanOneStmt
        #                     Stmt -> ExprStatement
        #                     Stmt -> While Expr CRStmtCRs EndWhile
        #                     Stmt -> ID :
        #                     Stmt -> Goto ID
        #                     Stmt -> For ID = Expr To Expr OptStep CRStmtCRs EndFor
        #                     Stmt -> Sub ID CRStmtCRs EndSub
        #                     Stmt -> If Expr Then CRStmtCRs MoreThanZeroElseIf
        #                     Stmt ->
        #                     MoreThanZeroElseIf -> OptionalElse
        #                     MoreThanZeroElseIf -> ElseIf Expr Then CRStmtCRs MoreThanZeroElseIf
        #                     OptionalElse -> EndIf
        #                     OptionalElse -> Else CRStmtCRs EndIf
        #                     ExprStatement -> ID = Expr
        #                     ExprStatement -> ID . ID = Expr
        #                     ExprStatement -> ID . ID ( Exprs )
        #                     ExprStatement -> ID ( )
        #                     ExprStatement -> ID Idxs = Expr
        #                     CRStmtCRs -> CR TheRest
        #                     TheRest ->
        #                     TheRest -> Stmt CR TheRest
        #                     MoreThanOneStmt -> Stmt
        #                     MoreThanOneStmt -> Stmt CR MoreThanOneStmt
        #                     OptStep ->
        #                     OptStep -> Step Expr
        #                     Expr -> CondExpr
        #                     Exprs ->
        #                     Exprs -> MoreThanOneExpr
        #                     MoreThanOneExpr -> Expr
        #                     MoreThanOneExpr -> Expr , MoreThanOneExpr
        #                     CondExpr -> OrExpr
        #                     OrExpr -> OrExpr Or AndExpr
        #                     OrExpr -> AndExpr
        #                     AndExpr -> AndExpr And EqNeqExpr
        #                     AndExpr -> EqNeqExpr
        #                     EqNeqExpr -> EqNeqExpr = CompExpr
        #                     EqNeqExpr -> EqNeqExpr <> CompExpr
        #                     EqNeqExpr -> CompExpr
        #                     CompExpr -> CompExpr < AdditiveExpr
        #                     CompExpr -> CompExpr <= AdditiveExpr
        #                     CompExpr -> CompExpr > AdditiveExpr
        #                     CompExpr -> CompExpr >= AdditiveExpr
        #                     CompExpr -> AdditiveExpr
        #                     AdditiveExpr -> AdditiveExpr + MultiplicativeExpr
        #                     AdditiveExpr -> AdditiveExpr - MultiplicativeExpr
        #                     AdditiveExpr -> MultiplicativeExpr
        #                     MultiplicativeExpr -> MultiplicativeExpr * UnaryExpr
        #                     MultiplicativeExpr -> MultiplicativeExpr / UnaryExpr
        #                     MultiplicativeExpr -> UnaryExpr
        #                     UnaryExpr -> - Primary
        #                     UnaryExpr -> Primary
        #                     Primary -> NUM
        #                     Primary -> STR
        #                     Primary -> ( Expr )
        #                     Primary -> ID
        #                     Primary -> ID . ID
        #                     Primary -> ID . ID ( Exprs )
        #                     Primary -> ID Idxs
        #                     Idxs -> [ Expr ]
        #                     Idxs -> [ Expr ] Idxs
        #                     """

        # },
        # # Assistant message 7
        # {
        #     "role": "assistant",""
        #     "content": """  Rule: MoreThanZeroElseIf -> OptionalElse
        #                     Indicates that there may be no ElseIf blocks, just an OptionalElse (either an Else block or an EndIf).
        #                     Rule: MoreThanZeroElseIf -> ElseIf Expr Then CRStmtCRs MoreThanZeroElseIf
        #                     Defines one or more ElseIf blocks, each with an expression and statements.
        #                     Rule: OptionalElse -> EndIf
        #                     No Else block; the If statement ends with EndIf.
        #                     Rule: OptionalElse -> Else CRStmtCRs EndIf
        #                     Defines an Else block with its own statements, followed by EndIf.
        #                     Rule: ExprStatement -> ID = Expr
        #                     An assignment statement where an identifier (ID) is assigned the value of an expression (Expr).
        #                     Rule: ExprStatement -> ID . ID = Expr
        #                     A member assignment statement where a member of an object or class (ID . ID) is assigned the value of an expression.
        #                     Rule: ExprStatement -> ID . ID ( Exprs )
        #                     A method call where an object or class member (ID . ID) is invoked with arguments (Exprs).
        #                     Rule: ExprStatement -> ID ( )
        #                     A function or method call without any arguments.
        #                     Rule: ExprStatement -> ID Idxs = Expr
        #                     An array assignment where an array element (ID Idxs) is assigned the value of an expression.
        #                     Rule: CRStmtCRs -> CR TheRest
        #                     A series of statements separated by carriage returns (CR), followed by the rest of the statements (TheRest).
        #                     Rule: TheRest ->
        #                     Defines an empty set of remaining statements (end of statement sequence).
        #                     Rule: TheRest -> Stmt CR TheRest
        #                     Defines one or more statements, each followed by a carriage return.
        #                     Rule: MoreThanOneStmt -> Stmt
        #                     A block of one statement.
        #                     Rule: MoreThanOneStmt -> Stmt CR MoreThanOneStmt
        #                     A block of multiple statements, each followed by a carriage return.
        #                     Optional Step in For Loops
        #                     Rule: OptStep ->
        #                     Defines an empty step (i.e., no Step keyword is used, so the loop increments by 1 by default).
        #                     Rule: OptStep -> Step Expr
        #                     Defines an optional Step clause in a For loop, with an expression for the step value."""
 
        # },
        # # Assistant message 8
        # {
        #     "role": "assistant",""
        #     "content": """  Rule 26: Expr -> CondExpr
        #                     An expression (Expr) can be a conditional expression (CondExpr).
        #                     Rules 27-30: Exprs, MoreThanOneExpr
        #                     Exprs can be empty (no arguments) or consist of one or more expressions, possibly separated by commas.
        #                     10. Logical and Comparison Operators
        #                     Rule 31: CondExpr -> OrExpr
        #                     A conditional expression is composed of Or expressions.
        #                     Rules 32-33: OrExpr -> OrExpr Or AndExpr | AndExpr
        #                     An OrExpr is a logical OR of two expressions, or simply an AndExpr.
        #                     Rules 34-35: AndExpr -> AndExpr And EqNeqExpr | EqNeqExpr
        #                     An AndExpr is a logical AND of two expressions, or an equality/inequality expression.
        #                     Rules 36-38: EqNeqExpr -> = | <> | CompExpr
        #                     An equality (=) or inequality (<>) expression compares two values. Alternatively, it can be a comparison expression (CompExpr).
        #                     11. Comparison Expressions
        #                     Rules 39-43: CompExpr -> < | <= | > | >= | AdditiveExpr
        #                     A comparison expression evaluates less than (<), less than or equal to (<=), greater than (>), or greater than or equal to (>=), or can be an additive expression.
        #                     Arithmetic Operations
        #                     Rules 44-46: AdditiveExpr -> + | - | MultiplicativeExpr
        #                     An additive expression uses + or - operators, or can be a multiplicative expression.
        #                     Rules 47-49: MultiplicativeExpr -> * | / | UnaryExpr
        #                     A multiplicative expression uses * or / operators, or can be a unary expression.
        #                     Unary Expressions and Primary Expressions
        #                     Rules 50-51: UnaryExpr -> - | Primary
        #                     A unary expression may negate a value or can be a primary expression.
        #                     Rules 52-58: Primary -> NUM | STR | ( Expr ) | ID | ID . ID | ID . ID ( Exprs ) | ID Idxs
        #                     Primary expressions include numbers (NUM), strings (STR), parentheses-enclosed expressions, identifiers, member accesses, method calls, or array indexing.
        #                     Array Indexing
        #                     Rules 59-60: Idxs -> [ Expr ] | [ Expr ] Idxs
        #                     Defines array indexing where one or more indices are provided within brackets.
        #                     """
 
        # },
        # # Assistant message 9
        # {
        #     "role": "system",
        #     "content": "You are a helpful assistant that provides programming code suggestions while typing code in an IDE (Integrated Development Environment). Just answer concisely and place your answer after the provided code."
        # },
#     ]
# )
# print(chat_completion.choices[0].message.content, "\n")
# {"messages": [{"role": "system", "content": "Marv is a factual chatbot that is also sarcastic."}, 
#               {"role": "user", "content": "What's the capital of France?"}, 
#               {"role": "assistant", "content": "Paris, as if everyone doesn't know that already."}]}

# infile = './C11_Text_Cand/bfree.i.textual_collection.txt' # data file 
# infile1 = './C11_Sample/chapter_8/exercise_8_08/bfree.i'   # source code file
# prog_lan= "C11"            # programming language
# encoding = 'utf-8'
# read_data(infile, infile1,prog_lan,encoding)

# infile = './C11/loop.i.textual_collection.txt' # textual data file 
# infile1 = './C11/loop.i'   # source code file
# prog_lan= "C11"            # programming language
# encoding = 'utf-8'
# read_data(infile, infile1,prog_lan,encoding)


# infile = './SB_Data/07_For.data' # data file 
# infile1 = './SB_Sample/07_For.sb'   # source code file
# prog_lan= "Small Basic"
# encoding = 'utf-16'
# read_data(infile, infile1,prog_lan,encoding)

# # Define the folders
# data_folder = './SB_Data'
# sample_folder = './SB_Sample'
# prog_lan = "Small Basic"
# encoding = 'utf-16'

# # List all files in the SB_Data folder
# for data_file in os.listdir(data_folder):
#     if data_file.endswith('.data'):
#         # Get the base file name without the extension
#         base_name = os.path.splitext(data_file)[0]
        
#         # Construct the corresponding file path in SB_Sample folder
#         sample_file = f"{base_name}.sb"
#         sample_file_path = os.path.join(sample_folder, sample_file).replace("\\", "/")
        
#         # Construct the data file path
#         data_file_path = os.path.join(data_folder, data_file).replace("\\", "/")
        
#         # Check if the corresponding .sb file exists
#         if os.path.exists(sample_file_path):
#             read_data(data_file_path, sample_file_path, prog_lan, encoding)
#         else:
#             print(f"Warning: No corresponding .sb file found for {data_file}")


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


