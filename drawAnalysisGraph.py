#!/usr/bin/env python
# coding: utf-8
# This program analyzes precision comparison data based on the length of candidate lists 
# and visualizes the results using line graphs.

import pandas as pd

#df = pd.read_csv("./Result Analysis/C11/CSV/combined.csv", sep=",")
#df = pd.read_csv("./Result Analysis/SB/CSV/combined.csv", sep=",")
#df

# Prompt the user to input the file path
file_path = input("Enter the file path for the CSV file: ")

# Load the CSV file
try:
    df = pd.read_csv(file_path, sep=",")
except FileNotFoundError:
    print("File not found. Please check the file path and try again.")
    exit()
    
    
# Replace spaces in column names with underscores
df.columns = df.columns.str.replace(' ', '_')
df


# Function to count comparisons by candidate list length
# def count_comparisons_by_candidate_length(df):
#     # List to store the results
#     results = []
    
#     # Loop through all lengths up to the maximum value of Candidate_List_length
#     max_length = df['Candidate_List_length'].max()
#     for i in range(1, max_length + 1):
#         # Filter data where Candidate_List_length equals i
#         subset = df[df['Candidate_List_length'] == i]
        
#         # Count comparisons based on conditions
#         count_greater = (subset['precision1'] > subset['precision4']).sum()
#         count_equal = (subset['precision1'] == subset['precision4']).sum()
#         count_smaller = (subset['precision1'] < subset['precision4']).sum()
        
#         # Store the results
#         results.append({
#             'Candidate_List_length': i,
#             'with_guide_greater': count_greater,
#             'with_guide_equal': count_equal,
#             'with_guide_smaller': count_smaller
#         })
    
#     # Convert results to a DataFrame
#     result_df = pd.DataFrame(results)
#     return result_df

# Example usage
# comparison_df = count_comparisons_by_candidate_length(df)
# comparison_df


# Summing the columns of the comparison DataFrame
# column_sums = comparison_df.sum()
# column_sums


# Create a new DataFrame by filtering rows where precision1 > precision4
with_guide_greater_df = df[df['precision1'] > df['precision4']]

# Group by Candidate_List_length
count_by_length1 = with_guide_greater_df.groupby('Candidate_List_length').size()
count_by_length1

# Create a new DataFrame by filtering rows where precision1 == precision4
with_guide_equal_df = df[df['precision1'] == df['precision4']]

count_by_length2 = with_guide_equal_df.groupby('Candidate_List_length').size()
count_by_length2

# Create a new DataFrame by filtering rows where precision1 < precision4
with_guide_smaller_df = df[df['precision1'] < df['precision4']]

count_by_length3 = with_guide_smaller_df.groupby('Candidate_List_length').size()
count_by_length3


import matplotlib.pyplot as plt

# Plot line graphs
plt.figure(figsize=(12, 6))
plt.plot(count_by_length1.index, count_by_length1.values, marker='o', linestyle='-', color='b', label='with a guide > without a guide')
plt.plot(count_by_length2.index, count_by_length2.values, marker='o', linestyle='-', color='g', label='with a guide = without a guide')
plt.plot(count_by_length3.index, count_by_length3.values, marker='o', linestyle='-', color='r', label='with a guide < without a guide')

# Add graph title and labels
plt.title('Comparison between guided precision and unguided precision by number of candidates')
plt.xlabel('Candidate_List_length')
plt.ylabel('Count')
plt.legend()
plt.grid(True)
plt.show()


