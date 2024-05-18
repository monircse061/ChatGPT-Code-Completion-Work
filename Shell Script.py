import os

# Directory containing the Small Basic files
SB_DIR = "./Sample"

# Directory containing the processed data files
DATA_DIR = "./SB_data"

# Path to the Python script handling Small Basic processing
PYTHON_SCRIPT = "read_datafile_as_text.py"

# Ensure both directories exist
if not os.path.isdir(SB_DIR) or not os.path.isdir(DATA_DIR):
    print("Error: SB directory or data directory not found.")
    exit(1)

# Iterate over each Small Basic file
for sb_file in os.listdir(SB_DIR):
    if sb_file.endswith(".sb"):
        # Get the base filename without extension
        filename = os.path.splitext(sb_file)[0]

        # Check if the corresponding data file exists
        data_file = os.path.join(DATA_DIR, filename + ".data")
        if os.path.isfile(data_file):
            print("Processing", sb_file)
            cmd = f"python {PYTHON_SCRIPT} '{os.path.join(SB_DIR, sb_file)}' '{data_file}'"
            os.system(cmd)
            if os.path.exists(data_file):
                print("Success:", sb_file, "processed.")
            else:
                print("Error: Failed to process", sb_file)
        else:
            print("Error: Data file not found for", sb_file)

print("All files processed.")

# Shell script that runs all the 27 Small Basic Programs
# #!/bin/bash

# # Directory containing the SmallBasic files
# DIR="/path/to/DIR"

# # Path to the .data file
# DATA_FILE="/path/to/DEF.data"

# # Loop over all .sb files in the specified directory
# for file in "$DIR"/*.sb
# do
#     echo "Processing $file..."
#     filename=$(basename "$file" .sb)
#     python MyProg.py "$file" "$filename.data" "$DATA_FILE"
# done

# echo "All files processed."


