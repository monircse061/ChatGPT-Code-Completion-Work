# -*- coding: utf-8 -*-
"""
Created on Wed May 22 15:41:51 2024

@author: moonh
"""

import os
import sys
import chardet
import pandas as pd


PL_NAME = ''
if len(sys.argv) != 2:
    print(f"Usage: python {sys.argv[0]} <PL_NAME>")
    sys.exit(1)

PL_NAME = sys.argv[1]

def extract_values_from_file(file_path):
    
    print(file_path)
    
    with open(file_path, 'rb') as f:
        raw_data = f.read()
        result = chardet.detect(raw_data)
        encoding = result['encoding']
        
    with open(file_path, 'r', encoding=encoding) as file:
        lines = file.readlines()
        if len(lines) >= 3:
            last_three_lines = lines[-3:]
            avg_precision = float(last_three_lines[0].split(": ")[1].strip())
            avg_sequence_precision = float(last_three_lines[1].split(": ")[1].strip())
            avg_cosine_precision = float(last_three_lines[2].split(": ")[1].strip())
            return avg_precision, avg_sequence_precision, avg_cosine_precision
        else:
            return None, None, None

def create_dataframe_from_directory(directory_path):
    data = []
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            if file.endswith('.txt'):  # Process only files with .txt extension
                file_path = os.path.join(root, file)
                avg_precision, avg_sequence_precision, avg_cosine_precision = extract_values_from_file(file_path)
                if avg_precision is not None:
                    file_name_without_extension = os.path.splitext(file)[0]
                    data.append([file_name_without_extension, avg_precision, avg_sequence_precision, avg_cosine_precision])

    df = pd.DataFrame(data, columns=['File Name', 'Average Precision', 'Average Sequence Matcher Similarity Precision', 'Average Cosine Similarity Precision'])
    return df


directory_path = './Result/' + PL_NAME # Change to your actual directory path
df = create_dataframe_from_directory(directory_path)
print(df)

# Save the DataFrame to a CSV file
df.to_csv(PL_NAME + '_output.csv', index=False)

# Calculate the mean of each column
mean_avg_precision = df['Average Precision'].mean()
mean_avg_sequence_precision = df['Average Sequence Matcher Similarity Precision'].mean()
mean_avg_cosine_precision = df['Average Cosine Similarity Precision'].mean()

print(f"Average Precision Mean: {mean_avg_precision}")
print(f"Average Sequence Matcher Similarity Precision Mean: {mean_avg_sequence_precision}")
print(f"Average Cosine Similarity Precision Mean: {mean_avg_cosine_precision}")
