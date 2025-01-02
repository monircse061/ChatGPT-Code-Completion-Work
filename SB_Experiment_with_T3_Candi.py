from openai import OpenAI
import sys
import time
import evaluate
import os
import re
from difflib import SequenceMatcher
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
# Load SACREBLEU metric using evaluate.load
sacrebleu = evaluate.load("sacrebleu")
# Initialize OpenAI client 
client = OpenAI(api_key="api-key")
request_count = 0  # Counter for requests made (RPD calculation)
prompt_tokens = 0
completion_tokens = 0
total_tokens = 0 
def read_data(file_name, sc_file_name, prog_lan, encoding): # for Microsoft Small Basic Program: encoding='utf-16'
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
                            elif prog_lan == "Microsoft Small Basic":
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
                elif prog_lan == "Microsoft Small Basic":
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
                    i=1
                    for line in lines:
                        line = line.strip()
                        
                        # Start extracting when we hit the target state
                        if line == target_state_str:
                            start_extracting = True
                            continue
                        
                        # Stop extracting when we hit the next state
                        if line.startswith("State") and start_extracting:
                            break
                        
                        # Collect the data once the target state is found
                        if start_extracting:
                            extracted_data.append(f"{i} : ")
                            extracted_data.append(line)
                            i=i+1
                    
                    return extracted_data

                # Usage
                state_number = state
                states = [state_number]
                file_path = os.path.join(os.path.dirname(__file__), "./smallbasic-syntax-completion-candidates-results.txt")
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
                            This is the SmallBasic Programming Language Grammar:
                            Prog' -> Prog
                            Prog -> MoreThanOneStmt
                            Stmt -> ExprStatement
                            Stmt -> While Expr CRStmtCRs EndWhile
                            Stmt -> ID :
                            Stmt -> Goto ID
                            Stmt -> For ID = Expr To Expr OptStep CRStmtCRs EndFor
                            Stmt -> Sub ID CRStmtCRs EndSub
                            Stmt -> If Expr Then CRStmtCRs MoreThanZeroElseIf
                            Stmt ->
                            MoreThanZeroElseIf -> OptionalElse
                            MoreThanZeroElseIf -> ElseIf Expr Then CRStmtCRs MoreThanZeroElseIf
                            OptionalElse -> EndIf
                            OptionalElse -> Else CRStmtCRs EndIf
                            ExprStatement -> ID = Expr
                            ExprStatement -> ID . ID = Expr
                            ExprStatement -> ID . ID ( Exprs )
                            ExprStatement -> ID ( )
                            ExprStatement -> ID Idxs = Expr
                            CRStmtCRs -> CR TheRest
                            TheRest ->
                            TheRest -> Stmt CR TheRest
                            MoreThanOneStmt -> Stmt
                            MoreThanOneStmt -> Stmt CR MoreThanOneStmt
                            OptStep ->
                            OptStep -> Step Expr
                            Expr -> CondExpr
                            Exprs ->
                            Exprs -> MoreThanOneExpr
                            MoreThanOneExpr -> Expr
                            MoreThanOneExpr -> Expr , MoreThanOneExpr
                            CondExpr -> OrExpr
                            OrExpr -> OrExpr Or AndExpr
                            OrExpr -> AndExpr
                            AndExpr -> AndExpr And EqNeqExpr
                            AndExpr -> EqNeqExpr
                            EqNeqExpr -> EqNeqExpr = CompExpr
                            EqNeqExpr -> EqNeqExpr <> CompExpr
                            EqNeqExpr -> CompExpr
                            CompExpr -> CompExpr < AdditiveExpr
                            CompExpr -> CompExpr <= AdditiveExpr
                            CompExpr -> CompExpr > AdditiveExpr
                            CompExpr -> CompExpr >= AdditiveExpr
                            CompExpr -> AdditiveExpr
                            AdditiveExpr -> AdditiveExpr + MultiplicativeExpr
                            AdditiveExpr -> AdditiveExpr - MultiplicativeExpr
                            AdditiveExpr -> MultiplicativeExpr
                            MultiplicativeExpr -> MultiplicativeExpr * UnaryExpr
                            MultiplicativeExpr -> MultiplicativeExpr / UnaryExpr
                            MultiplicativeExpr -> UnaryExpr
                            UnaryExpr -> - Primary
                            UnaryExpr -> Primary
                            Primary -> NUM
                            Primary -> STR
                            Primary -> ( Expr )
                            Primary -> ID
                            Primary -> ID . ID
                            Primary -> ID . ID ( Exprs )
                            Primary -> ID Idxs
                            Idxs -> [ Expr ]
                            Idxs -> [ Expr ] Idxs"""            
                         },
                        {
                            "role": "system",
                            "content": "Replace the single quotation ('') with your response."
                         },
                         {
                            "role": "user",
                            "content": """This is the incomplete Microsoft Small Basic programming language code:
                                            TextWindow.Write("Enter temperature in Fahrenheit: ") 
                                            fahr = TextWindow.ReadNumber() 
                                            celsius = 5 * (fahr - 32) / 9 
                                            TextWindow.WriteLine("Temperature in Celsius is " +
                                            'ID'
                                            Complete the 'ID' part of the code in the Microsoft Small Basic programming language. Just show your answer in place of 'ID'"""
                         },
                        {
                            "role": "assistant",
                            "content": "celsius"
                        },
                                                 {
                            "role": "user",
                            "content": """This is the incomplete Microsoft Small Basic programming language code:
                                            TextWindow.Write("Enter temperature in Fahrenheit: ") 
                                            For i
                                            '= Expr To Expr OptStep CRStmtCRs EndFor'
                                            Complete the '= Expr To Expr OptStep CRStmtCRs EndFor' part of the code in the Microsoft Small Basic programming language. Just show 
                                            your answer in place of '= Expr To Expr OptStep CRStmtCRs EndFor'"""
                         },
                        {
                            "role": "assistant",
                            "content": """ i = 10 To 1 Step -1
                                             TextWindow.WriteLine(i)
                                           EndFor"""
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
                parent_folder = "Result/Result_with_T3/SB" 
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

# # Define the folders
# data_folder = './SB_Data'
# sample_folder = './SB_Sample'
# prog_lan= "Microsoft Small Basic"  
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
        
infile = './SB_Data/07_For.data' # data file    05_If
infile1 = './SB_Sample/07_For.sb'   # source code file               
prog_lan= "Microsoft Small Basic"   
encoding = 'utf-16'
read_data(infile, infile1,prog_lan,encoding)




