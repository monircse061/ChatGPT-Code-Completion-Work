# -*- coding: utf-8 -*-
"""
Created on Wed May 22 15:41:51 2024
@author: moonh
"""

import os
import sys
import chardet
import pandas as pd

PL_NAME = 'C11'   # # Change the programming language as needed
if len(sys.argv) != 2:
    print(f"Usage: python {sys.argv[0]} <PL_NAME>")
    sys.exit(1)

PL_NAME = sys.argv[1]

def extract_values_from_file(file_path):
    print(f"Processing file: {file_path}")
    
    # Detect encoding with chardet
    with open(file_path, 'rb') as f:
        raw_data = f.read()
        result = chardet.detect(raw_data)
        encoding = result['encoding']
        
    try:
        # Attempt to read the file with the detected encoding
        with open(file_path, 'r', encoding=encoding) as file:
            lines = file.readlines()
    except (UnicodeDecodeError, TypeError):
        print(f"Warning: Detected encoding '{encoding}' failed for file {file_path}. Trying utf-8.")
        try:
            # Retry with utf-8 encoding if the detected encoding fails
            with open(file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
        except UnicodeDecodeError as e:
            print(f"Error reading file {file_path} with utf-8 encoding: {e}")
            return None, None, None, None

    # Ensure there are at least 4 lines to process
    if len(lines) < 4:
        print(f"Warning: File {file_path} does not contain the required 4 lines.")
        return None, None, None, None

    try:
        avg_precision_with = float(lines[-4].split(": ")[1].strip())
        avg_precision_without = float(lines[-3].split(": ")[1].strip())
        avg_sequence_with = float(lines[-2].split(": ")[1].strip())
        avg_sequence_without = float(lines[-1].split(": ")[1].strip())
        return avg_precision_with, avg_precision_without, avg_sequence_with, avg_sequence_without
    except (IndexError, ValueError) as e:
        print(f"Error processing values in file {file_path}: {e}")
        return None, None, None, None

def create_dataframe_from_directory(directory_path):
    data = []
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            if file.endswith('.txt'):  # Process only files with .txt extension
                file_path = os.path.join(root, file)
                avg_precision_with, avg_precision_without, avg_sequence_with, avg_sequence_without = extract_values_from_file(file_path)
                if None not in (avg_precision_with, avg_precision_without, avg_sequence_with, avg_sequence_without):
                    file_name_without_extension = os.path.splitext(file)[0]
                    data.append([file_name_without_extension, avg_precision_with, avg_precision_without, avg_sequence_with, avg_sequence_without])

    df = pd.DataFrame(data, columns=[
        'File Name', 
        'Average Precision with Candidate Guidance', 
        'Average Precision without Candidate Guidance', 
        'Average Sequence Matcher Similarity with Candidate Guidance', 
        'Average Sequence Matcher Similarity without Candidate Guidance'
    ])
    return df

directory_path = './Result/Result Analysis/C11_with-without-Candi-with-Precision/'    # Change the directory path as needed
df = create_dataframe_from_directory(directory_path)
print(df)

# Calculate the mean of each column
if not df.empty:
    mean_avg_precision_with = df['Average Precision with Candidate Guidance'].mean()
    mean_avg_precision_without = df['Average Precision without Candidate Guidance'].mean()
    mean_avg_sequence_with = df['Average Sequence Matcher Similarity with Candidate Guidance'].mean()
    mean_avg_sequence_without = df['Average Sequence Matcher Similarity without Candidate Guidance'].mean()

    # Print mean values
    print(f"Average Precision with Candidate Guidance Mean: {mean_avg_precision_with}")
    print(f"Average Precision without Candidate Guidance Mean: {mean_avg_precision_without}")
    print(f"Average Sequence Matcher Similarity with Candidate Guidance Mean: {mean_avg_sequence_with}")
    print(f"Average Sequence Matcher Similarity without Candidate Guidance Mean: {mean_avg_sequence_without}")
    
    # Append the mean values as a new row in the DataFrame
    df.loc['Mean'] = [
        'Mean',
        mean_avg_precision_with,
        mean_avg_precision_without,
        mean_avg_sequence_with,
        mean_avg_sequence_without
    ]
else:
    print("DataFrame is empty. No data to calculate means.")

# Save the DataFrame to a CSV file with the mean values appended
df.to_csv(PL_NAME + '_output_with-without-Candi-with-Precision.csv', index=False)

# Type in the terminal to run one of the following
# python summary.py SB

# python summary.py C11
