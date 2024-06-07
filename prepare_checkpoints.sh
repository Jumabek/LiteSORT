#!/bin/bash

# Install gdown if not already installed
if ! command -v gdown &> /dev/null
then
    echo "gdown could not be found, installing..."
    pip install gdown
fi

# Define the Google Drive file ID and the output file name
FILE_ID="1u8G6Kl0MtO3RO3RlP2jfS1oNMvk0OryH"
OUTPUT_FILE="checkpoint.zip"

# Download the file using gdown
gdown --id "$FILE_ID" -O "$OUTPUT_FILE"

# Check if the file was downloaded
if [[ -f "$OUTPUT_FILE" ]]; then
    # Create a directory for the extracted files
    DIR_NAME="${OUTPUT_FILE%.zip}"
    mkdir -p "$DIR_NAME"

    # Extract the zip file into the created directory
    unzip -q "$OUTPUT_FILE" -d "$DIR_NAME"

    # Remove the zip file after extraction
    rm "$OUTPUT_FILE"

    echo "Download and extraction complete."
else
    echo "Failed to download $OUTPUT_FILE"
fi
