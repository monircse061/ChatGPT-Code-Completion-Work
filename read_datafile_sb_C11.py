from openai import OpenAI
import time
import evaluate
import os
from difflib import SequenceMatcher
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
# Load SACREBLEU metric using evaluate.load
sacrebleu = evaluate.load("sacrebleu")
# ----------Hide API-Start---------------------------
# Retrieve API key from environment variable
api_key = os.environ.get("OPENAI_API_KEY")

if api_key is None:
    raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY environment variable.")

client = OpenAI(api_key=api_key)

# Now, Set the OPENAI_API_KEY environment variable in the environment. You can do this in the editor terminal or command prompt before running my script:
# export OPENAI_API_KEY="your-api-key-here"
# Run the above line in terminal and replace "your-api-key-here" with your actual OpenAI API key.
 
def read_data(file_name, sc_file_name, prog_lan, encoding = 'utf-8'): # for Small Basic Program: encoding='utf-16'
    resultlist = []
    appx_main_start_line = 0
    text_line_num = 0
    try:
        with open(sc_file_name, 'r',encoding=encoding) as fl:
           if prog_lan == "C11":
                linesnum = fl.readlines()
                # Iterate over each line and find the line number containing the substring "stdio.h"
                for i, line in enumerate(linesnum):
                    if "/usr/include" in line:  #/usr/include
                        appx_main_start_line = i+1  # Adding 1 because line numbers start from 1, not 0      
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
                # Prefix variable and the corresponding textual candidate variable
                text_candi = ""
                resulted_prefix = " "
                 # Store the first line of the block
                current_block.append(line.strip())
                while True:
                    #--------------find_prefix function--------Start----------------------#
                    def find_prefix(filename, line_num, column_num):
                        with open(filename, 'r') as file:
                            prefix = ''
                            lines = file.readlines()
                            if prog_lan == "C11":
                                if line_num-1 != 0:
                                    line_start=line_num-10
                                    while line_start < line_num-1:
                                            prefix += lines[line_start] 
                                            line_start+=1
                            elif prog_lan == "Small Basic":
                                if line_num-1 != 0:
                                    line_start=0
                                    while line_start < line_num-1:
                                            prefix += lines[line_start] 
                                            line_start+=1

                            target_line = lines[line_num - 1] # print ("target line: ",target_line)
                            current_column = 0
                            if prog_lan == "C11":
                                for char in target_line:
                                    if char == '\t':
                                        # Counting tabs as one character
                                        current_column += 4  # Assuming tab width is 4 spaces
                                    else:
                                        current_column += 1
                                    prefix += char
                                    if current_column == column_num-1:
                                        break
                                return prefix.strip()
                            elif prog_lan == "Small Basic":
                                for char in target_line:
                                    if char == ' ':
                                        current_column += 1
                                    else:
                                        current_column += 1
                                        if current_column == column_num:
                                            break
                                    prefix += char
                                return prefix.strip()
                    #--------------find_prefix function--------End----------------------#
                    content_line = f.readline().strip()
                    parts = content_line.split(':', 1)  # Split each line into two parts based on the first colon
                    ln_col = parts[0].split(',')   # Split each line into two parts based on comma
                    if prog_lan == "C11":
                        if not content_line:  # Check if we've reached the end of the block
                            if len(current_block) >= 2:
                                # print("Second line of the block:", current_block[1].strip())
                                parts = current_block[1].split(':', 1)  # Split each line into two parts based on the first colon
                                ln_col = parts[0].split(',')   # Split each line into two parts based on comma
                                line_num = int(ln_col[0])         # line number
                                column_num = int(ln_col[1])        # column number
                                text_line_num = line_num
                                if text_line_num>appx_main_start_line:
                                  cursor_position = str(line_num) + " " + str(column_num)
                                  resulted_prefix = find_prefix(sc_file_name, line_num, column_num)
                            # Reset the current block
                            current_block = []
                            break

                        if len(parts) >= 2:  # Check if 'parts' contains at least two elements
                            text_candi = text_candi +" "+ parts[1].strip()  # Append the second part (after colon) to the result string
                        # Append the current line to the block
                        current_block.append(content_line)

                    elif prog_lan == "Small Basic":
                        if not content_line:
                            break
                        if content_line.startswith("PR#"):  # Skip lines starting with 'PR#' 
                            prefix_ln_col_num=1
                            continue
                        parts = content_line.split(':', 1)  # Split each line into two parts based on the first colon
                        ln_col = parts[0].split(',')   # Split each line into two parts based on comma
                        # Access once the first line and column number for each block
                        if prefix_ln_col_num == 1:
                            # find the line and column number of the prefix
                            line_num = int(ln_col[0])         # line number
                            column_num = int(ln_col[1])        # column number
                            cursor_position = str(line_num) + " " + str(column_num)
                            resulted_prefix = find_prefix(sc_file_name, line_num, column_num)
                            prefix_ln_col_num=0
                        if len(parts) >= 2:  # Check if 'parts' contains at least two elements
                            text_candi = text_candi +" "+ parts[1].strip()  # Append the second part (after colon) to the result stringe
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
                modified_words = ['Identifier' if word == 'ID' else 'String' if word == 'STR' else 'Expression' if word == 'Exprs' else 'Expression' if word == 'Expr' else word for word in words]
                modified_struct_candi = ' '.join(modified_words)
                # print(index, state, resulted_prefix, " | ", modified_struct_candi, " | ", text_candi)
                print ("Parse State: ", state, " Cursor Position: ", cursor_position, "\n")
                # Define the prompt-------------------------------------------------------------
                prompt = f"""
                This is the incomplete {prog_lan} programming language code:
                {resulted_prefix}
                '{modified_struct_candi}'
                Complete the '{modified_struct_candi}' part of the code in the {prog_lan} programming language. Just show your answer in place of '{modified_struct_candi}'. 
                """
                #Complete just the content of the curly brace (inside) part of the '{modified_struct_candi}'. Do not produce curly brace in the output.
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

                print("\nSACREBLEU Score:", score, "\n")    # ['score', 'counts', 'totals', 'precisions', 'bp', 'sys_len', 'ref_len']
                precision_first_element = score["precisions"][0]
                
                print("\nFirst element of precision:", precision_first_element, "\n")
                total_precision += precision_first_element
                sequence__similarity = SequenceMatcher(None, response, text_candi).ratio()
                print(f"SequenceMatcher Similarity: {sequence__similarity:.2f}\n\n")
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
                   file.write("Parse State: {}\tCursor Position: {}\n{}Time taken: {} seconds\nReceived response: {}\nSACREBLEU Score: {}\nFirst element of precision:{}\n\n".format(state, cursor_position, prompt + "\n", query_time, response, score, precision_first_element))
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

infile = './C11_Text_Cand/copy_io.i.textual_collection.txt' # data file 
infile1 = './C11_Sample/chapter_1/exercise_1_09/copy_io.i'   # source code file
prog_lan= "C11"            # programming language
read_data(infile, infile1,prog_lan)

# infile = './SB_Data/05_If.data' # data file 
# infile1 = './SB_Sample/05_If.sb'   # source code file
# prog_lan= "Small Basic"
# read_data(infile, infile1,prog_lan)

# # If you use Shell_Script_for_SB, uncomment the rest of the code and comment out the above eight lines of code (239-247 lines).
# def main():
#     if len(sys.argv) != 4:
#         print("Usage: python read_datafile_as_text.py <datafile> <sbfile> <prog_lan>")
#         sys.exit(1)

#     datafile = sys.argv[1]
#     sbfile = sys.argv[2]
#     prog_lan = sys.argv[3]

#     read_data(datafile, sbfile, prog_lan)

# if __name__ == "__main__":
#     main()

