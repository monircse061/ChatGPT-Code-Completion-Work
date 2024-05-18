# ChatGPT-Code-Completion-Tool
The first project at Chonnam National University in the Software Languages and Systems Lab

read_datafile_sb_C11.py
1. Set the OPENAI_API_KEY environment variable in the environment. You can do this in the editor terminal or command prompt before running my script:
   export OPENAI_API_KEY="your-api-key-here"
   Run the above line in terminal and replace "your-api-key-here" with your actual OpenAI API key.
2. For Small Basic Program encoding is: encoding ='utf-16' and for C11 encoding ='utf-8'
3. Run one at a time time
   infile = './C11_Text_Cand/copy_io.i.textual_collection.txt' # data file 
   infile1 = './C11_Sample/chapter_1/exercise_1_09/copy_io.i'   # source code file
   prog_lan= "C11"            # programming language
   read_data(infile, infile1,prog_lan)
5. You can run also use the shell script to run all the programs at a time. 
