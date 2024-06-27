#!/bin/bash

# Install gdown if not already installed
if ! command -v gdown &> /dev/null
then
    echo "gdown could not be found, installing..."
    pip install gdown
fi

# Create datasets directory if it doesn't exist
DATASETS_DIR="."
#mkdir -p "$DATASETS_DIR"

# Google Drive folder ID
FOLDER_ID="1JGQo3PZsJOFJoDckPQOB-ln-k4MmuwP7"

# Download file list from Google Drive folder directly into datasets directory
cd "$DATASETS_DIR" || exit
gdown --folder --id "$FOLDER_ID"

# Loop through all zip files in the local datasets directory
cd "datasets" || exit
for FILE in *.zip; do
    if [[ -f "$FILE" ]]; then
        # Create a directory with the name of the zip file (without extension)
        DIR_NAME="${FILE%.zip}"
        #mkdir -p "$DIR_NAME"

        # Extract the zip file into the created directory
        if unzip -q "$FILE" ; then
            # Remove the zip file after successful extraction
            rm "$FILE"
        else
            echo "Failed to unzip $FILE"
        fi
    fi
done

# Clean up
cd ..
