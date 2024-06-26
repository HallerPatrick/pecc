#!/bin/bash
#
set -e

export ADVENT_OF_CODE_SESSION=""

if [ -z "$ADVENT_OF_CODE_SESSION" ]; then
    echo "The ADVENT_OF_CODE_SESSION environment variable is not set. Please set it to your session cookie value."
    exit 1
fi

# Directory to store all the puzzle inputs and descriptions
BASE_DIR="aoc_puzzles"
MERGE_INTO_DATASET="true"
TARGET_DATASET="dataset/aoc_lite"

# Create the base directory if it doesn't exist
mkdir -p "$BASE_DIR"

for YEAR in {2015..2022}; do
    for DAY in {1..25}; do

        YEAR_DIR="$BASE_DIR/$YEAR"

        # Create the year directory if it doesn't exist
        mkdir -p "$YEAR_DIR"

        INPUT_FILE="$YEAR_DIR/day_$DAY.txt"
        PUZZLE_FILE="$YEAR_DIR/day_$DAY.md"
        JSON_FILE="$YEAR_DIR/day_$DAY.json"

        aoc download -d $DAY -y $YEAR -i "$INPUT_FILE" -p "$PUZZLE_FILE"

        jq -n --arg year "$YEAR" --arg day "$DAY" '{"year": $year, "day": $day}' >"$JSON_FILE"

        # Split the puzzle description into two parts: part one and part two, and extract the answer
        awk '/--- Part Two ---/{flag=1;next} flag{print > "'"$YEAR_DIR"'/day_'"$DAY"'_part2.md"} !flag{print > "'"$YEAR_DIR"'/day_'"$DAY"'_part1.md"}' "$PUZZLE_FILE"

        for PART in part1 part2; do
            PART_FILE="$YEAR_DIR/day_${DAY}_$PART.md"

            # If part file does not exist, continue to the next part
            if [ ! -f "$PART_FILE" ]; then
                continue
            fi

            # Extract the answer and remove the answer line and everything after it
            ANSWER=$(sed -n '/Your puzzle answer was /{s/Your puzzle answer was //;s/[`.]*//g;p}' "$PART_FILE")
            # sed -i '/Your puzzle answer was /Q' "$PART_FILE"
            #
            # # Remove the line "--- Day {day}: {title} ---" and everything before it from the part 1 description
            # if [ "$PART" == "part1" ]; then
            #   sed -i '1,/--- Day [0-9]\+: .\+ ---/d' "$PART_FILE"
            # fi
            #
            # sed -i '/^----------$/d' "$PART_FILE"
            # sed -i '1d' "$PART_FILE"
            #
            DESCRIPTION=$(python tools/cleanup.py "$PART_FILE")

            # Check if DESCRIPTION is empty
            if [ -z "$DESCRIPTION" ]; then
                echo "Error: Could not extract the puzzle description for year $YEAR, day $DAY, part $PART"
                exit 1
            fi

            # Add the puzzle description and answer to the JSON file
            # DESCRIPTION=$(<"$PART_FILE")
            jq --arg part "$PART" --arg description "$DESCRIPTION" --arg answer "$ANSWER" '.[$part] = {"description": $description, "answer": $answer}' "$JSON_FILE" | sponge "$JSON_FILE"
        done

        INPUT=$(<"$INPUT_FILE")

        # Some INPUT might be too big for linux command line stack, so we need to dump it into a JSON and 
        # use the slurpfile feature of jq
        echo -n "$INPUT" | jq -Rs '[.]' > /tmp/input.json
        jq --slurpfile input /tmp/input.json '.input = $input[0]' "$JSON_FILE" | sponge "$JSON_FILE"


        rm /tmp/input.json

        # Merge if wanted
        if [ "$MERGE_INTO_DATASET" == "true" ]; then
            DESCRIPTION_PART1=$(jq -r '.part1.description' "$JSON_FILE")
            DESCRIPTION_PART2=$(jq -r '.part2.description' "$JSON_FILE")

            # Replace the description with the one from the debug dataset
            jq --arg description "$DESCRIPTION_PART1" --arg description2 "$DESCRIPTION_PART2" '.part1.description = $description | .part2.description = $description2' "$TARGET_DATASET/$YEAR/day_$DAY.json" | sponge "$TARGET_DATASET/$YEAR/day_$DAY.json"
        fi

        # Print a message indicating that the puzzle input and description for the current day have been downloaded and processed
        echo "Processed puzzle for year $YEAR, day $DAY"
    done
done
