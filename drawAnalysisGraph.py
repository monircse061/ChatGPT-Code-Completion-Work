#!/usr/bin/env python
# coding: utf-8

import pandas as pd

# Load the first dataset (metrics for precision1 and precision4)
metric6_df = pd.read_csv("./Result Analysis/C11/CSV/combined.csv", sep=",")
# metric6_df = pd.read_csv("./Result Analysis/SB/CSV/combined.csv", sep=",")  # For SB
# Replace spaces in column names with underscores for easier access
metric6_df.columns = metric6_df.columns.str.replace(' ', '_')


# Count comparisons between precision1 and precision4
count1 = metric6_df[(metric6_df['precision1'] > metric6_df['precision4'])].shape[0]
count2 = metric6_df[(metric6_df['precision1'] == metric6_df['precision4'])].shape[0]
count3 = metric6_df[(metric6_df['precision1'] < metric6_df['precision4'])].shape[0]
print(count1,count2,count3)


# Load the second dataset (metrics for Top3 precision values)
top3_df = pd.read_csv("./Result_with_T3/C11/CSV/combined.csv", sep=",")
# top3_df = pd.read_csv("./Result_with_T3/SB/CSV/combined.csv", sep=",")  # For SB
top3_df.columns = top3_df.columns.str.replace(' ', '_')

# Create a new column "precisionMAX" as the maximum value among precision1, precision2, and precision3
top3_df['precisionMAX'] = top3_df[['precision1', 'precision2', 'precision3']].max(axis=1, skipna=True)

# Rename the "precision1" column in top3_df to "precisionTop1" for clarity
top3_df = top3_df.rename(columns={'precision1': 'precisionTop1'})

# Combine the two datasets by selecting relevant columns from both
result_df = pd.concat(
    [metric6_df[['name', 'Candidate_List_length', 'precision1', 'precision4']], top3_df[['precisionTop1','precisionMAX']]],
    axis=1
)

# Rename the "precision4" column in the combined dataset to "precisionWithout" for clarity
result_df = result_df.rename(columns={'precision4': 'precisionWithout'})
# Display the combined dataset
result_df

# Calculate and display the mean of each column in the combined dataset
result_mean = result_df.mean()
print(result_mean)

# Function to count comparisons by Candidate_List_length
def count_comparisons_by_candidate_length(df, col1, col2):
    """
    Counts how many times col1 > col2, col1 == col2, and col1 < col2 for each Candidate_List_length.

    Parameters:
        df (DataFrame): Input DataFrame containing the data.
        col1 (str): First column for comparison.
        col2 (str): Second column for comparison.

    Returns:
        DataFrame: Results with counts of comparisons grouped by Candidate_List_length.
    """    
    
    results = []
    
    # Loop through each Candidate_List_length value
    max_length = df['Candidate_List_length'].max()
    for i in range(1, max_length + 1):
        # Filter rows with the current Candidate_List_length
        subset = df[df['Candidate_List_length'] == i]
        
        # Count occurrences for each comparison condition
        count_greater = (subset[col1] > subset[col2]).sum()
        count_equal = (subset[col1] == subset[col2]).sum()
        count_smaller = (subset[col1] < subset[col2]).sum()
        
        # Append the results to the list
        results.append({
            'Candidate_List_length': i,
            'with_guide_greater': count_greater,
            'with_guide_equal': count_equal,
            'with_guide_smaller': count_smaller
        })
    
    # Convert the results list to a DataFrame and return
    result_df = pd.DataFrame(results)
    return result_df


import matplotlib.pyplot as plt

# Function to plot comparison results by Candidate_List_length
def plot_by_candidate_list_length(df):

    plt.figure(figsize=(12, 6))
    # Plot each comparison type with a unique style and color
    plt.plot(df['Candidate_List_length'], df['with_guide_greater'], marker='^', linestyle='-', color='b', label='with guide > without guide')
    plt.plot(df['Candidate_List_length'], df['with_guide_equal'], marker='o', linestyle='--', color='g', label='with guide = without guide')
    plt.plot(df['Candidate_List_length'], df['with_guide_smaller'], marker='v', linestyle=':', color='r', label='with guide < without guide')
    
    # Add labels, title, legend, and grid
    plt.title('Comparison between guided precision and unguided precision by number of candidates(C11)')
    plt.xlabel('the length of candidates list')
    plt.ylabel('Count')
    plt.legend()
    plt.grid(True)
    plt.show()
    
    # Display the plot
    plt.show()
    
# Example 1: Ideal candidate (precision1) vs Without (precisionWithout)
comparison_df = count_comparisons_by_candidate_length(result_df, 'precision1', 'precisionWithout')
print(comparison_df)

plot_by_candidate_list_length(comparison_df)

# Example 2: MAX candidate (precisionMAX) vs Without (precisionWithout)
comparison_df = count_comparisons_by_candidate_length(result_df, 'precisionMAX', 'precisionWithout')
print(comparison_df)
plot_by_candidate_list_length(comparison_df)

# Example 3: Top1 candidate (precisionTop1) vs Without (precisionWithout)
comparison_df = count_comparisons_by_candidate_length(result_df, 'precisionTop1', 'precisionWithout')
print(comparison_df)
plot_by_candidate_list_length(comparison_df)
