#!/bin/bash

# Directory to store all the puzzle inputs and descriptions
BASE_DIR="aoc_puzzles"

# Create the base directory if it doesn't exist
mkdir -p "$BASE_DIR"

# Loop through each year from 2015 to 2022
for YEAR in {2015..2022}; do
  # Loop through each day from 1 to 25
  for DAY in {1..25}; do
    # Directory to store the puzzle inputs and descriptions for the current year
    YEAR_DIR="$BASE_DIR/$YEAR"
    
    # Create the year directory if it doesn't exist
    mkdir -p "$YEAR_DIR"
    
    # File to store the puzzle input for the current day
    INPUT_FILE="$YEAR_DIR/day_$DAY.txt"
    
    # File to store the full puzzle description for the current day
    PUZZLE_FILE="$YEAR_DIR/day_$DAY.md"
    
    
    # Check if each part contains the line "Your puzzle answer was ..."
    for PART in part1 part2; do
      PART_FILE="$YEAR_DIR/day_${DAY}_$PART.md"
      if grep -q "Your puzzle answer was ..." "$PART_FILE"; then
        echo "Year $YEAR, day $DAY, $PART: The line 'Your puzzle answer was ...' was found."
      else
        echo "Year $YEAR, day $DAY, $PART: The line 'Your puzzle answer was ...' was NOT found."
      fi
    done
  done
done
