# ChatGPT-Code-Completion-Tool
The first project at Chonnam National University in the Software Languages and Systems Lab

read_datafile_sb_C11.py
1. Install all necessary libraries or packages: openai, evaluate, os, difflib.
   
2. Set the OPENAI_API_KEY environment variable in the environment. You can do this in the editor terminal or command prompt before running the next line of code:
   
   export OPENAI_API_KEY="your-api-key-here"
   
   Run the above line in terminal and replace "your-api-key-here" with your actual OpenAI API key.
3. For Small Basic Program encoding is: encoding ='utf-16' and for C11 encoding ='utf-8'.
   
4. Run one program at a time in C11 using the folowing codes.And make sure to comment out the above eight lines of code (250-262 lines).

   infile = './C11_Text_Cand/copy_io.i.textual_collection.txt' # data file
   
   infile1 = './C11_Sample/chapter_1/exercise_1_09/copy_io.i'   # source code file
   
   prog_lan= "C11"            # programming language
   
   read_data(infile, infile1,prog_lan)

   OR, run one program at a time in Small Basic Programming.
   infile = './SB_Data/10_GraphicWindow.data' # data file 

   infile1 = './SB_Sample/10_GraphicWindow.sb'   # source code file

   prog_lan= "Small Basic"

   read_data(infile, infile1,prog_lan)
   
5. You can run also use the shell script to run all the programs at a time. For this use Shell_Script_for_SB.py for Small Basic Program and make sure to comment out the above eight lines of code (239-247 lines).
