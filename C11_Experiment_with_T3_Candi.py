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
client = OpenAI(api_key="api-key")
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
                states = [state_number]
                file_path = os.path.join(os.path.dirname(__file__), "./c11-data-state-collection.txt")
                # Read the content of the file
                with open(file_path, "r", encoding="utf8") as file:
                    file_content = file.read()
                result = []
                # Iterate over each state
                for state in states:
                    start = f"State {state}"
                    end = f"State {state + 1}"
                    
                    start_idx = file_content.find(start)
                    end_idx = file_content.find(end)
                    
                    # Extract the relevant text
                    text = file_content[start_idx:end_idx]
                    
                    # Split the text into lines
                    lines = text.split("\n")
                    for line in lines:
                        # Skip empty lines and non-candidate lines
                        if not line.strip() or line[0] != "[":
                            continue
                        
                        # Split the line into parts around the last colon
                        parts = line.rsplit(":", 1)  # Split only on the last colon
                        
                        # Ensure that there are at least two parts (key and value)
                        if len(parts) < 2:
                            continue  # Skip lines that don't have at least one colon

                        key = parts[0].strip()  # The key is before the last colon
                        value_part = parts[1].strip()  # The value is after the last colon

                        # Try to convert the value to an integer (if it's numeric)
                        try:
                            value = int(value_part)
                        except ValueError:
                            # If it's not numeric, store the value as a string (expression)
                            value = value_part  # Keep the expression as string

                        # Skip lines with invalid or unexpected key-value formats
                        if not key or not value:
                            continue
                        
                        # Append the parsed data to the result
                        result.append({"key": key, "value": value})
                ranked_candi_list = []
                # Print the selected candidates with formatted keys
                for i, candidate in enumerate(result, start=1):
                    key = candidate['key']
                    value = candidate['value']
                    # Process the key for the completion word
                    completion_word = key
                    completion_word = re.sub(r"^\[", "", completion_word)  # Remove starting brackets
                    completion_word = re.sub(r"\]$", "", completion_word)  # Remove end brackets]
                    completion_word = re.sub(r",,", "<<COMMA>>", completion_word)  # Replace double commas with placeholder
                    completion_word = re.sub(r",", "", completion_word)  # Remove single commas
                    completion_word = re.sub(r"<<COMMA>>", ",", completion_word)  # Replace placeholder with actual comma
                    completion_word = re.sub(r"\s+\bT\b", " ", completion_word)  # Replace 'T' with a space
                    completion_word = re.sub(r"\bT\b", "", completion_word)  # Delete 'T'
                    completion_word = re.sub(r"\bNT\b", "", completion_word)  # Delete 'NT'
                    completion_word = re.sub(r"\s+", " ", completion_word)  # Change multiple spaces to 1 space
                    completion_word = re.sub(r"\s+\.", ".", completion_word)  # Remove spaces before '.'
                    completion_word = re.sub(r"\.\s+", ".", completion_word)  # Remove spaces after '.'
                    completion_word = re.sub(r"\bTO\b", " TO", completion_word)  # Normalize 'TO'
                    ranked_candi_list.append(completion_word)

                print ("\nParse State: ", state, " Cursor Position: ", cursor_position, "\n")
                
                # Generate prompts based on the number of candidates in ranked_candi_list
                prompt = []
                for i, candi in enumerate(ranked_candi_list):
                    if i >= 3:  # Limit to at most 3 prompts
                        break
                    prompt_text = f"""
                    This is the incomplete {prog_lan} programming language code:
                    {resulted_prefix}
                    '{ranked_candi_list[i].strip()}'
                    Complete the '{ranked_candi_list[i].strip()}' part of the code in the {prog_lan} programming language. Just show your answer in place of '{ranked_candi_list[i].strip()}.'
                    """
                    prompt.append(prompt_text)

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
                # List to store chat completions
                chat_completions = []
                # Iterate over the prompts and generate chat completions
                for prompt_txt in prompt:
                    chat_completion = client.chat.completions.create(
                        model="gpt-3.5-turbo-0125",
                        max_tokens=70,
                        messages=[
                            {
                                "role": "user",
                                "content": prompt_txt
                            },
                        ]
                    )
                    chat_completions.append(chat_completion)
                # List to store responses
                responses = []
                # Extract and print responses from chat completions
                for i, chat_completion in enumerate(chat_completions, start=1):
                    response = chat_completion.choices[0].message.content
                    responses.append(response)
                    print(f"Received response with candidate {i}:", response)
                sacrebleu_scores = []
                sequence_matcher_scores = []
                # all reponses
                for i, response in enumerate(responses):
                    # Compute SACREBLEU score
                    score = sacrebleu.compute(predictions=[response], references=[text_candi])
                    sacrebleu_scores.append(score)  # Append only the score dictionary
                    # Compute SequenceMatcher similarity
                    similarity = SequenceMatcher(None, response, text_candi).ratio()
                    sequence_matcher_scores.append(similarity)  # Append only the similarity as a float

                # Output Results
                parent_folder = "Result/Result_with_T3/C11" 
                if prog_lan == "C11":
                    text_file_name = file_name.replace('./C11_Text_Cand/', "").replace('.i.textual_collection.txt', "")
                elif prog_lan == "Microsoft Small Basic":
                    text_file_name = sc_file_name.replace('./SB_Sample/', "").replace('.sb', "")
                text_file_name += "_result.txt"

                # Create the parent folder if it doesn't exist
                if not os.path.exists(parent_folder):
                    os.makedirs(parent_folder)

                # Define the folder path for the child folder inside the parent folder
                file_path = os.path.join(parent_folder, text_file_name)

                # Write results to the file
                with open(file_path, "a") as file:
                    file.write("Parse State: {}\tCursor Position: {}\nCandidates List: {}\n{}\nTop One to Three Candidates: {}\n".format(
                        state, cursor_position, ranked_candi_list, "", ranked_candi_list[:3]))
                    file.write("{}".format(prompt[0]))
                    # Write response and score for prompts
                    for i in range(len(responses)):  # Use len(responses) to avoid index issues
                        # file.write("{}".format(prompt[i]))
                        file.write("\nReceived response with candidate {}: {}\n".format(i + 1, responses[i]))
                        # Access the SACREBLEU score dictionary
                        score_details = sacrebleu_scores[i]  # This is already a dictionary
                        file.write("SacreBLEU score {}: {} ".format(i + 1, score_details['score']))
                        file.write("Counts: {} ".format(score_details['counts']))
                        file.write("Totals: {} ".format(score_details['totals']))
                        file.write("Precisions: {} ".format(score_details['precisions']))
                        file.write("System length: {} ".format(score_details['sys_len']))
                        file.write("Reference length: {} ".format(score_details['ref_len']))
                        file.write("\nFirst element of precision: {} \n".format(score_details['precisions'][0]))
                        # Write SequenceMatcher score
                        file.write("SequenceMatcher Score {}: {:.2f}\n".format(i + 1, sequence_matcher_scores[i]))
                    # Write the actual result
                    file.write("\nActual result: {}\n\n".format(text_candi))
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



# # Folder information
# data_folder = './C11_Text_Cand'
# sample_folder = './C11_Sample'
# prog_lan = "C11"
# encoding = 'utf-8'

# # List of file names to iterate over
# file_names = [
#     "exercise_7_05_calculator_result", "exercise_4_03_calculator_result", "exercise_5_12_detab_result", 
#     "exercise_1_01_hello_world_result", "exercise_5_19_undcl_result", "exercise_7_06_compare_result", 
#     "exercise_4_06_variables_result", "exercise_2_10_lower_result", "exercise_7_01_case_result", 
#     "exercise_4_09_getch_result", "exercise_4_02_atof_result", "exercise_8_07_malloc_free_result", 
#     "exercise_5_02_getfloat_result", "exercise_5_12_entab_result"
# ]

# # Function to map file names to their chapter and exercise directories and extract base file name
# def get_chapter_exercise_and_base_name(file_name):
#     # Extract the chapter and exercise numbers from the file name
#     parts = file_name.split('_')
#     if len(parts) >= 3:
#         chapter = parts[1]  # The second part after 'exercise' is the chapter number
#         exercise = parts[2]  # The third part is the exercise number
#         # The actual file name should be after 'exercise_XX_XX' (e.g., 'bfree' in 'bfree.i')
#         base_name = "_".join(parts[3:]).replace('_result', '')  # Remove '_result' suffix
#         return f"chapter_{chapter}/exercise_{chapter}_{exercise}", base_name
#     return None, None

# # Iterate over the provided file names
# for file_name in file_names:
#     # Get the chapter, exercise directory and the base file name
#     subdir, base_name = get_chapter_exercise_and_base_name(file_name)
    
#     if subdir and base_name:
#         # Construct the corresponding file path in the C11_Sample folder (using only base name)
#         sample_file_path = os.path.join(sample_folder, subdir, f"{base_name}.i").replace("\\", "/")
        
#         # Construct the data file path (keeping the full original name)
#         data_file_path = os.path.join(data_folder, f"{base_name}.i.textual_collection.txt").replace("\\", "/")
        
#         # Check if the corresponding file exists in the sample folder
#         if os.path.exists(sample_file_path):
#             # Call the read_data function with the appropriate parameters
#             read_data(data_file_path, sample_file_path, prog_lan, encoding)
#         else:
#             print(f"Warning: No corresponding file found for {sample_file_path}")
#     else:
#         print(f"Error: Could not determine chapter, exercise, or base file name for {file_name}")

# infile = './C11_Text_Cand/fahrenheit_celsius.i.textual_collection.txt' # data file 
# infile1 = './C11_Sample/chapter_1/exercise_1_03/fahrenheit_celsius.i'   # source code file  
# prog_lan= "C11"            # programming language
# encoding = 'utf-8'
# read_data(infile, infile1,prog_lan,encoding)