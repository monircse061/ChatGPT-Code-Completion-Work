# This python shell script for Small Basic Program
import os
import subprocess
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# Directory containing the Small Basic files
SB_DIR = "./SB_Sample"

# Directory containing the processed data files
DATA_DIR = "./SB_Data"

# Path to the Python script handling Small Basic processing
PYTHON_SCRIPT = "read_datafile_for_c11 copy.py"

def main():
    # Ensure both directories exist
    if not os.path.isdir(SB_DIR):
        logging.error(f"SB directory not found: {SB_DIR}")
        return

    if not os.path.isdir(DATA_DIR):
        logging.error(f"Data directory not found: {DATA_DIR}")
        return

    # Iterate over each data file
    for data_file in os.listdir(DATA_DIR):
        if data_file.endswith(".data"):
            # Get the base filename without extension
            filename = os.path.splitext(data_file)[0]

            # Check if the corresponding Small Basic file exists
            sb_file = os.path.join(SB_DIR, filename + ".sb")
            if os.path.isfile(sb_file):
                logging.info(f"Processing {sb_file} with {data_file}")
                cmd = ["python", PYTHON_SCRIPT, os.path.join(DATA_DIR, data_file), sb_file, "Small Basic"]
                
                try:
                    subprocess.run(cmd, check=True)
                    logging.info(f"Success: {sb_file} processed with {data_file}.")
                except subprocess.CalledProcessError as e:
                    logging.error(f"Error processing {sb_file} with {data_file}: {e}")
            else:
                logging.error(f"SB file not found for {data_file}")

    logging.info("All files processed.")

if __name__ == "__main__":
    main()
