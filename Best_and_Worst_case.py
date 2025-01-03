import os
import re

# Function to get the "Ideal Candidate" from SB_data file
def get_ideal_candidate(sb_file, parse_state, cursor_position1):
    ideal_candidate = ''
    sb_data_folder = "C11_Text_Cand"  # SB_Data
    sb_file_path = os.path.join(sb_data_folder, sb_file + '.i.textual_collection.txt').replace("\\", "/")
    
    try:
        with open(sb_file_path, 'r', encoding='utf-8') as f:
            current_state = None
            current_candidate = None
            while True:
                line = f.readline()
                if not line:  # If reading the file has finished
                    break
                line = line.strip()
                # Skip empty lines and lines that don't start with a numeric state
                if not line or not line[0].isdigit():
                    continue
                
                # If the line starts with a numeric state, extract it
                try:
                    state = int(line.split()[0])
                    struct_candi = line[len(str(state)):].strip()  # Extract the rest as candidate
                    # Debug: Print the current state and structural candidate
                    # print(f"Found state: {state}, Candidate: '{struct_candi}'")
                except ValueError:
                    continue
                
                # Update current state and candidate
                current_state = state
                current_candidate = struct_candi
                
                # Process the next lines for PR# and cursor positions
                while True:
                    next_line = f.readline().strip()
                    if not next_line:
                        break  # End of block
                    
                    # Debug: Print each next line within the block
                    # print(f"  Inside block, processing: '{next_line}'")
                    
                    if next_line.startswith("PR#"):
                        continue  # Skip PR# lines
                    
                    if ':' in next_line:
                        parts = next_line.split(':', 1)
                        ln_col = parts[0].split(',')  # Extract line and column
                        
                        try:
                            line_num = int(ln_col[0])
                            column_num = int(ln_col[1])
                            cursor_position = f"{line_num} {column_num}"
                            
                            # Debug: Print the current cursor position and check match
                            # print(f"    Found cursor position: '{cursor_position}'")
                            
                            # Match both parse state and cursor position
                            if current_state == parse_state and cursor_position == cursor_position1:
                                # print(f"Match found! State: {current_state}, Cursor: {cursor_position}")
                                return current_candidate
                        except ValueError:
                            pass
                    
                    # Break when a new block starts
                    if next_line[0].isdigit():
                        break

    except FileNotFoundError:
        print(f"File not found: {sb_file_path}")
    except Exception as e:
        print(f"An error occurred: {e}")

    return ideal_candidate

# # Example usage
# result = get_ideal_candidate('05_If', 58, '5 22')
# print(f"Ideal Candidate: '{result}'")

def extract_parse_state_data(input_text):
    # Split the text into individual parse state sections
    sections = re.split(r"Parse State: \d+", input_text)
    parse_state_headers = re.findall(r"Parse State: \d+", input_text)

    # Combine headers with their respective sections
    parse_state_data = {}
    for i, header in enumerate(parse_state_headers):
        parse_state_data[header] = sections[i + 1].strip()

    return parse_state_data

def classify_predictions(parse_state_data, file_name, base_name):
    # Classify predictions across all parse states
    best_predictions = []
    worst_predictions = []

    for header, state_data in parse_state_data.items():
        blocks = re.split(r"Actual result:", state_data)

        for block in blocks[:-1]:
            actual_result = blocks[-1].strip()
            candidates = re.findall(r"Received response with candidate \d+: (.*?)\n", block)

            # Extract the cursor position information after "Cursor Position: "
            cursor_position_match = re.findall(r"Cursor Position: (\d+ \d+)", block)
            cursor_position = cursor_position_match[0] if cursor_position_match else None

            # Extract the "Candidates List" line
            candidates_list_match = re.search(r"Candidates List: \[(.*?)\]", block)
            if candidates_list_match:
                # Extract all elements in the list
                candidates_list = candidates_list_match.group(1)
                individual_candidates = re.findall(r"'(.*?)'", candidates_list)
            else:
                individual_candidates = []

            # # Access each candidate individually
            # for candidate in individual_candidates:
            #     print(f"Candidate: {candidate}")

            # Extract the "Top One to Three Candidates" line
            top_candidates_match = re.search(r"Top One to Three Candidates: \[(.*?)\]", block)
            if top_candidates_match:
                # Extract the first element in the list
                top_candidates = top_candidates_match.group(1)
                first_candidate_match = re.search(r"'(.*?)'", top_candidates)
                first_candidate = first_candidate_match.group(1) if first_candidate_match else None
            else:
                first_candidate = None

            # Extract parse state number from header
            parse_state_number = int(header.split(":")[1].strip())
            
            ideal_candidate= get_ideal_candidate(file_name,parse_state_number,cursor_position)

            if not candidates or len(candidates) < 3:
                continue  # Exclude cases with fewer than 3 candidates

            top_1_candidate = candidates[0]

            if ideal_candidate.strip() == first_candidate.strip():
                if top_1_candidate.strip() == actual_result.strip():
                    best_predictions.append(
                        f"{base_name}\n{header}\nIdeal Candidate: {ideal_candidate}\n{block.strip()}\nActual result: {actual_result}"
                    )
            elif ideal_candidate.strip() in [candidate.strip() for candidate in individual_candidates[5:]]:
                if top_1_candidate.strip() != actual_result.strip():
                    worst_predictions.append(
                        f"{base_name}\n{header}\nIdeal Candidate: {ideal_candidate}\n{block.strip()}\nActual result: {actual_result}"
                    )

    return best_predictions, worst_predictions

def save_predictions_to_files(best_predictions, worst_predictions, best_file_path, worst_file_path):
    with open(best_file_path, "a") as best_file:
        for prediction in best_predictions:
            best_file.write(prediction + "\n\n")
    with open(worst_file_path, "a") as worst_file:
        for prediction in worst_predictions:
            worst_file.write(prediction + "\n\n")

if __name__ == "__main__":
    # Define the folder containing result files
    result_folder = "Result/Result_with_T3/C11"  # Result/Result_with_T3/SB
    best_file_path = os.path.join("Result", "best_predictions.txt").replace("\\", "/")
    worst_file_path = os.path.join("Result", "worst_predictions.txt").replace("\\", "/")

    # Clear existing files to avoid appending to old results
    open(best_file_path, "w").close()
    open(worst_file_path, "w").close()

    # Traverse all files in the result folder
    for result_file in os.listdir(result_folder):
        if result_file.endswith("_result.txt"):
            # Get the full path of the result file
            result_file_path = os.path.join(result_folder, result_file).replace("\\", "/")

            # Extract the base file name without the '_result' suffix
            # file_name = os.path.basename(result_file).split("_result")[0]
            # Extract the base name and remove "_result" suffix
            base_name = os.path.basename(result_file).split("_result")[0]

            # Remove numeric parts and join the remaining parts
            file_name = "_".join([part for part in base_name.split("_")[2:] if not part.isdigit()])

            # Read and process the result file
            with open(result_file_path, "r") as file:
                input_text = file.read()

            parse_state_data = extract_parse_state_data(input_text)
            best_predictions, worst_predictions = classify_predictions(parse_state_data, file_name,base_name)
            save_predictions_to_files(best_predictions, worst_predictions, best_file_path, worst_file_path)



