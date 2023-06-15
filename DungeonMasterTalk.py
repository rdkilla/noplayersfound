import os
import json


# Initialize an empty set to store all of Matt's unique utterances
matt_utterances = set()

# Specify the directory containing the JSON files
directory = r"D:\ai\discordbot\noplayerfound\dungeonmastertalk"

# Iterate over every file in the directory
for filename in os.listdir(directory):
    # Check if the file is a JSON file
    if filename.endswith(".json"):
        # Construct the full file path
        filepath = os.path.join(directory, filename)
        
        # Open the file with utf-8 encoding and load it as a Python list of dictionaries
        with open(filepath, "r", encoding="utf-8") as file:
            data_list = json.load(file)
        
        # Iterate over each dictionary in the list
        for data in data_list:
            # Check if "TURNS" is in the dictionary keys
            if "TURNS" in data.keys():
                # Iterate over each turn in the "TURNS" list
                for turn in data["TURNS"]:
                    # Check if "NAMES" is in the turn dictionary keys
                    if "NAMES" in turn.keys():
                        # Check if "MATT" is in the "NAMES" list
                        if "MATT" in turn["NAMES"]:
                            # Check if "UTTERANCES" is in the turn dictionary keys
                            if "UTTERANCES" in turn.keys():
                                # Add all of Matt's utterances to the set, duplicates will automatically be ignored
                                # Join the utterances into a single string with a space separating each utterance
                                utterance = ' '.join(turn["UTTERANCES"])
                                matt_utterances.add(utterance)

# Define the max size for each file in bytes (500KB)
max_size = 100 * 1024 

# Initialize a counter for the output file names
file_counter = 0

# Initialize a list to hold the utterances for the current file
current_file_utterances = []

# Write all the unique utterances to new text files
for utterance in matt_utterances:
    # Add the current utterance to the list
    current_file_utterances.append(utterance)

    # Calculate the size of the current file
    current_file_size = sum(len(u) for u in current_file_utterances)

    # If the current file size is over the max size, start a new file
    if current_file_size > max_size:
        with open(f"matt_utterances_{file_counter}.txt", "w", encoding="utf-8") as file:
            for u in current_file_utterances:
                file.write(u + "\n\n\n")

        # Increment the file counter
        file_counter += 1

        # Clear the list for the next file
        current_file_utterances = []

# Write any remaining utterances to a final file
with open(f"matt_utterances_{file_counter}.txt", "w", encoding="utf-8") as file:
    for u in current_file_utterances:
        file.write(u + "\n\n\n")
