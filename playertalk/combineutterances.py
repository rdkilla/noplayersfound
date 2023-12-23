import os

# Specify the directory containing the text files
directory = r"D:\ai\discordbot\noplayerfound\dungeonmastertalk"

# Specify the name of the output file
output_file_name = "combined_utterances.txt"

# Open the output file in write mode
with open(output_file_name, "w", encoding="utf-8") as output_file:
    # Iterate over every file in the directory
    for filename in os.listdir(directory):
        # Check if the file is a text file and follows the naming pattern
        if filename.startswith("non_matt_utterances_") and filename.endswith(".txt"):
            # Construct the full file path
            filepath = os.path.join(directory, filename)

            # Open the current file in read mode
            with open(filepath, "r", encoding="utf-8") as file:
                # Read the content of the file
                content = file.read()

                # Write the content to the output file
                output_file.write(content)
                output_file.write("\n\n")  # Add extra newlines for separation

print(f"All files have been concatenated into {output_file_name}")