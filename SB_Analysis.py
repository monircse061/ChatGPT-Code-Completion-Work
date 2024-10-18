from openai import OpenAI
import sys
import time
import evaluate
import os
from difflib import SequenceMatcher
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
# Load SACREBLEU metric using evaluate.load
sacrebleu = evaluate.load("sacrebleu")
# Initialize OpenAI client 
client = OpenAI(api_key="")
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
                filename = "smallbasic-syntax-completion-candidates-results.txt"
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
                            "content": """This is the incomplete Small Basic programming language code:
                                            TextWindow.Write("Enter temperature in Fahrenheit: ") 
                                            fahr = TextWindow.ReadNumber() 
                                            celsius = 5 * (fahr - 32) / 9 
                                            TextWindow.WriteLine("Temperature in Celsius is " +
                                            'Identifier'
                                            Complete the 'Identifier' part of the code in the Small Basic programming language. Just show your answer in place of 'Identifier'"""
                         },
                        {
                            "role": "assistant",
                            "content": "celsius"
                        },
                                                 {
                            "role": "user",
                            "content": """This is the incomplete Small Basic programming language code:
                                            TextWindow.Write("Enter temperature in Fahrenheit: ") 
                                            For i
                                            '= Expression To Expression OptStep CRStmtCRs EndFor'
                                            Complete the '= Expression To Expression OptStep CRStmtCRs EndFor' part of the code in the Small Basic programming language. Just show 
                                            your answer in place of '= Expression To Expression OptStep CRStmtCRs EndFor'"""
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

infile = './SB_Data/07_For.data' # data file 
infile1 = './SB_Sample/07_For.sb'   # source code file
prog_lan= "Small Basic"
encoding = 'utf-16'
read_data(infile, infile1,prog_lan,encoding)




