#!/bin/bash

# Check if an argument was provided (path to the directory containing MP3 files)
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 path_to_directory"
    exit 1
fi

DIRECTORY=$1

# Check if the provided directory exists
if [ ! -d "$DIRECTORY" ]; then
    echo "Directory does not exist: $DIRECTORY"
    exit 1
fi

# Loop through each MP3 file in the directory
for mp3file in "$DIRECTORY"/*.mp3; do
    # Check if the glob gets expanded to existing files.
    # If not, mp3file here will be exactly the pattern above
    # and the exists test will evaluate to false.
    [ -e "$mp3file" ] || continue
    # Process each MP3 file with the Python script
    echo "Processing $mp3file"
    python main.py "$mp3file"
done

echo "All MP3 files in $DIRECTORY have been processed."
