DESCRIPTION_PART1=$(jq -r '.part1.description' aoc_puzzles/2017/day_1.json)
DESCRIPTION_PART2=$(jq -r '.part2.description' aoc_puzzles/2017/day_1.json)

# Replace the description with the one from the debug dataset
jq --arg description "$DESCRIPTION_PART1" --arg description2 "$DESCRIPTION_PART2" '.part1.description = $description | .part2.description = $description2' dataset/aoc_lite_debug/2017/day_1.json

# jq -s --arg description "$DESCRIPTION_PART2" '.[0].part2.description = $description' dataset/aoc_lite_debug/2016/day_1.json | sponge dataset/aoc_lite_debug/2016/day_1.json
