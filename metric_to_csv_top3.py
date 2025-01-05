# -*- coding: utf-8 -*-
"""
Created on Sat Oct 26 20:15:34 2024

@author: moonh

The program processes text files in a specified directory containing evaluation 
metrics (e.g., SACREBLEU scores, precision, and SequenceMatcher scores). 
It extracts the data, organizes it into a DataFrame, 
and saves it as CSV files in an output directory

"""

import os
import re
import pandas as pd
from ast import literal_eval

# Convert metric logs from a text file into a DataFrame.
def metric_to_dataframe(file_path):
    
    # List to store parsed data
    data = []
    
    # Variables to track the current candidate list length and scores
    current_candidate_list_length = None
    scores = []
    
    # number of metrics 
    num_of_metrics = 9
    
    # Read the input file line by line
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            
            # Parse lines starting with 'Candidate List: '
            if line.startswith('Candidates List: '):
                # Add previous data block to the list
                if current_candidate_list_length is not None and ( len(scores) == num_of_metrics or len(scores) == current_candidate_list_length*3 ):
                    print(scores)
                    data.append([current_candidate_list_length] + scores)
                
                # Extract the candidate list length
                candidate_list_str = line.split('Candidates List: ')[1]
                candidate_list = literal_eval(candidate_list_str)
                #print(candidate_list)
                current_candidate_list_length = len(candidate_list)
                
                # Reset the scores list for the new block
                scores = []
            
            # Parse 'SACREBLEU score' lines
            elif line.startswith('SacreBLEU score'):
                sacrebleu_score = float(re.search(r": ([\d.]+)", line).group(1))
                scores.append(sacrebleu_score)
            
            # Parse 'First element of precision' lines
            elif line.startswith('First element of precision'):
                precision_score = float(re.search(r": ([\d.]+)", line).group(1))
                scores.append(precision_score)
            
            # Parse 'SequenceMatcher Score' lines
            elif line.startswith('SequenceMatcher Score'):
                sequence_matcher_score = float(re.search(r": ([\d.]+)", line).group(1))
                scores.append(sequence_matcher_score)
            
                # Save data when 9 scores are accumulated
                if len(scores) == num_of_metrics or len(scores) == current_candidate_list_length*3 :
                    print(scores)
                    data.append([current_candidate_list_length] + scores)
                    scores = []
    
    # Add the last block of data if it exists
    if current_candidate_list_length is not None and ( len(scores) == num_of_metrics or len(scores) == current_candidate_list_length*3 ):
        print(scores)
        data.append([current_candidate_list_length] + scores)
    
    # Define column names for the DataFrame
    columns = ['Candidate List length', 
               'SACREBLEU1', 'precision1', 'SequenceMatcher1',
               'SACREBLEU2', 'precision2', 'SequenceMatcher2',
               'SACREBLEU3', 'precision3', 'SequenceMatcher3']
    
    # Create and return the DataFrame
    df = pd.DataFrame(data, columns=columns)
    return df
    
# Convert all metric files in a directory to CSV format.
def save_metrics_to_csv(input_dir, output_dir):
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Process all files in the input directory
    for filename in os.listdir(input_dir):
        file_path = os.path.join(input_dir, filename)
        
        # Only process files (skip directories)
        if os.path.isfile(file_path):
            # Generate DataFrame from metrics
            df = metric_to_dataframe(file_path)
            
            # Set the output CSV file path
            csv_filename = f"{os.path.splitext(filename)[0]}.csv"
            csv_path = os.path.join(output_dir, csv_filename)
            
            # Save the DataFrame as a CSV file
            df.to_csv(csv_path, index=False)
            print(f"Saved {csv_filename} to {output_dir}")
            

# Example function calls
# Specify input and output directories for C11
input_directory = './Result_with_T3/C11'  # Input directory path
output_directory = './Result_with_T3/C11/CSV'  # Output directory path for CSV files

# Specify input and output directories for SmallBasic   
# input_directory = './Result_with_T3/SB'  # Input directory path
# output_directory = './Result_with_T3/SB/CSV'  # Output directory path for CSV files

save_metrics_to_csv(input_directory, output_directory)

# # 파일 경로 설정
# infile_path = './Result/any_result.txt'
# out_df = metric_to_dataframe(infile_path)
# # 결과 출력
# print(out_df)
# out_df.to_csv('./Result/any_result.csv', index=False)






