#!/bin/bash
set -x

export ADVENT_OF_CODE_SESSION="53616c7465645f5f014c497bab378e1e053f4f4475ce8a2dc27e1997919bbff11ae1f034ed4d73163e23d4083e463a21985da9defeb39250931031e94719c2dc"

MERGE_INTO_DATASET="true"
TARGET_DATASET="dataset/aoc_lite_debug"

# Directory to store all the puzzle inputs and descriptions
BASE_DIR="aoc_puzzles"

# Create the base directory if it doesn't exist
mkdir -p "$BASE_DIR"

for YEAR in {2015..2023}; do
  for DAY in {1..25}; do

    YEAR_DIR="$BASE_DIR/$YEAR"

    # Create the year directory if it doesn't exist
    mkdir -p "$YEAR_DIR"

    INPUT_FILE="$YEAR_DIR/day_$DAY.txt"
    PUZZLE_FILE="$YEAR_DIR/day_$DAY.md"
    JSON_FILE="$YEAR_DIR/day_$DAY.json"

    aoc download -d $DAY -y $YEAR -i "$INPUT_FILE" -p "$PUZZLE_FILE"

    jq -n --arg year "$YEAR" --arg day "$DAY" '{"year": $year, "day": $day}' > "$JSON_FILE"

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
      sed -i '/Your puzzle answer was /Q' "$PART_FILE"

      # Remove the line "--- Day {day}: {title} ---" and everything before it from the part 1 description
      if [ "$PART" == "part1" ]; then
        sed -i '1,/--- Day [0-9]\+: .\+ ---/d' "$PART_FILE"
      fi

      sed -i '/^----------$/d' "$PART_FILE"
      sed -i '1d' "$PART_FILE"

      # Add the puzzle description and answer to the JSON file
      DESCRIPTION=$(<"$PART_FILE")
      jq --arg part "$PART" --arg description "$DESCRIPTION" --arg answer "$ANSWER" '.[$part] = {"description": $description, "answer": $answer}' "$JSON_FILE" | sponge "$JSON_FILE"
    done

    INPUT=$(<"$INPUT_FILE")

    jq --arg input "$INPUT" '.input = $input' "$JSON_FILE" | sponge "$JSON_FILE"
    
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
