#!/bin/bash

# Define source and destination directories
SRC_DIR="/workspace/LiteSORT/datasets/VIRAT-S/train"
DEST_DIR="/workspace/LiteSORT/TrackEval/data/gt/virat_s/virat_s-test"

echo "Starting to copy .ini and gt.txt files..."

# Function to copy files to the correct destination
copy_files() {
    find "$SRC_DIR" -name "$1" | while read -r file; do
        # Extract the relative path from the source directory
        relative_path="${file#$SRC_DIR/}"
        
        # Get the sequence directory path
        seq_dir=$(dirname "$relative_path")
        
        # Ensure the destination directory exists
        mkdir -p "$DEST_DIR/$seq_dir"
        
        # Copy the file to the destination directory
        cp "$file" "$DEST_DIR/$seq_dir/$2"
        
        echo "Copied $file to $DEST_DIR/$seq_dir/$2"
    done
}

# Copy seqinfo.ini files
copy_files "seqinfo.ini" "seqinfo.ini"

# Copy gt.txt files to the correct gt subdirectory
find "$SRC_DIR" -name "gt.txt" | while read -r gt_file; do
    # Extract the relative path from the source directory
    relative_path="${gt_file#$SRC_DIR/}"
    
    # Get the sequence directory path
    seq_dir=$(dirname "$relative_path")
    
    # Ensure the destination gt subdirectory exists
    mkdir -p "$DEST_DIR/$seq_dir/gt"
    
    # Copy the gt file to the destination gt subdirectory
    cp "$gt_file" "$DEST_DIR/$seq_dir/gt.txt"
    
    echo "Copied $gt_file to $DEST_DIR/$seq_dir/gt.txt"
done

echo "Finished copying .ini and gt.txt files."
