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
# # ----------Hide API-Start---------------------------
# # Retrieve API key from environment variable
# api_key = os.environ.get("OPENAI_API_KEY")

# if api_key is None:
#     raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY environment variable.")

# client = OpenAI(api_key=api_key)
# # ----------Hide API-End---------------------------
# Initialize OpenAI client
client = OpenAI(api_key="Your_API_KEY") 
def read_data(file_name, sc_file_name, prog_lan, encoding): # for Small Basic Program: encoding='utf-16'
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
            for index, (state, cursor_position, resulted_prefix, struct_candi, text_candi) in enumerate(resultlist, start=1):
                # print (state, cursor_position, resulted_prefix, struct_candi, "text_candidate: ", text_candi, "\n")
                start_time = 0
                end_time = 0
                # Split the string by space and period---------------Word Modification-----------------------------------------
                words = struct_candi.split()
                # Replace 'ID' with 'Identifier' and 'STR' with 'String' and so on...
                modified_words = ['Identifier or Terminal' if word == 'ID' else 'String' if word == 'STR' else 'Number' if word == 'NUM' else 'Expression' if word == 'Exprs' else 'Expression' if word == 'Expr' else word for word in words]
                modified_struct_candi = ' '.join(modified_words)
                # print(index, state, resulted_prefix, " | ", modified_struct_candi, " | ", text_candi)
                print ("\nParse State: ", state, " Cursor Position: ", cursor_position, "\n")
                # # Define the prompt-------------------------------------------------------------
                # prompt = f"""
                # This is the incomplete {prog_lan} programming language code:
                # {resulted_prefix}
                # '{modified_struct_candi}'
                # Complete the '{modified_struct_candi}' part of the code in the {prog_lan} programming language. Just show your answer in place of '{modified_struct_candi}'. 
                # """ #Complete just the content of the curly brace (inside) part of the '{modified_struct_candi}'. Do not produce curly brace in the output.
                # ----Prompt Without Candidate Guidance----------
                prompt = f"""
                This is the incomplete {prog_lan} programming language code:
                {resulted_prefix}
                'next token or line'
                Complete the 'next token or line' part of the code in the {prog_lan} programming language. Just show your answer in place of 'next token or line'. 
                """
                print (prompt)
                # Send the query and measure time----------------------------------------------------------------
                start_time = time.time()
                chat_completion = client.chat.completions.create(
                    model="gpt-3.5-turbo-0125",
                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        },
                    ]
                )
                end_time = time.time()

                # Calculate the time taken
                query_time = end_time - start_time
                print("\nTime taken:", query_time, "seconds\n")

                # Get the response
                response = chat_completion.choices[0].message.content
                print("Received response:", response)

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

# infile = './C11_Text_Cand/copy_io.i.textual_collection.txt' # data file 
# infile1 = './C11_Sample/chapter_1/exercise_1_09/copy_io.i'   # source code file
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

# Define the folders
data_folder = './SB_Data'
sample_folder = './SB_Sample'
prog_lan = "Small Basic"
encoding = 'utf-16'

# List all files in the SB_Data folder
for data_file in os.listdir(data_folder):
    if data_file.endswith('.data'):
        # Get the base file name without the extension
        base_name = os.path.splitext(data_file)[0]
        
        # Construct the corresponding file path in SB_Sample folder
        sample_file = f"{base_name}.sb"
        sample_file_path = os.path.join(sample_folder, sample_file).replace("\\", "/")
        
        # Construct the data file path
        data_file_path = os.path.join(data_folder, data_file).replace("\\", "/")
        
        # Check if the corresponding .sb file exists
        if os.path.exists(sample_file_path):
            read_data(data_file_path, sample_file_path, prog_lan, encoding)
        else:
            print(f"Warning: No corresponding .sb file found for {data_file}")


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


