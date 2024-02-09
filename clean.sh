#!/bin/bash

# Remove all .json file in sample directory
for file in sample/*.json; do
    rm "$file"
done