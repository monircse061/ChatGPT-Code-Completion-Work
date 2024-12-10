# -*- coding: utf-8 -*-
"""
Created on Fri Nov 22 11:34:51 2024

@author: moonh

This program combines multiple CSV files from a directory into a single DataFrame. 
It adds a new column, name, containing the name of each file to track 
the origin of the data. The combined DataFrame is then saved as a new CSV file.

"""

import os
import pandas as pd


# Combine all CSV files in a directory into a single DataFrame, 
# adding a 'name' column to store the source file name.

def combine_csv_files_with_name_column(directory_path):
    combined_df = pd.DataFrame()  # Initialize the final DataFrame
    
    # Iterate through all files in the directory
    for filename in os.listdir(directory_path):
        if filename.endswith('.csv'):
            file_path = os.path.join(directory_path, filename)
            
            # Extract the file name without the extension
            name = os.path.splitext(filename)[0]
            
            # Read the CSV file
            df = pd.read_csv(file_path)
            
            # Add a 'name' column with the file name
            df.insert(0, 'name', name)  # Insert as the first column
            
            # Append the current DataFrame to the combined DataFrame
            combined_df = pd.concat([combined_df, df], ignore_index=True)
    
    return combined_df

# Example function calls
# for C11
# directory_path = './Result Analysis/C11/CSV' # Directory containing the CSV files
# combined_df = combine_csv_files_with_name_column(directory_path)
# print(combined_df)
# combined_df.to_csv('./Result Analysis/C11/CSV/combined.csv', index=False)

# for SB
directory_path = './Result Analysis/SB/CSV'
combined_df = combine_csv_files_with_name_column(directory_path)
print(combined_df)
# Save the combined DataFrame as a new CSV file
combined_df.to_csv('./Result Analysis/SB/CSV/combined.csv', index=False)

