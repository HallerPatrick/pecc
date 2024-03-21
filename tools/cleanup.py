import sys

def cleanup_part1(content):
    found_header = False

    cleaned = []
    for i, line in enumerate(content):

        if found_header:
            # Remove share links
            if "Twitter" and "https" in line:
                continue

            if "Your puzzle answer was" in line:
                break
            else:
                cleaned.append(line)

        elif line.startswith("\\---"):
            found_header = True
            cleaned.append(line)
            continue

    # Remove first and/or lasnt empty lines
    if cleaned[0] == "\n":
        cleaned = cleaned[1:]

    if cleaned[-1] == "\n":
        cleaned = cleaned[:-1]

    return "".join(cleaned)

def cleanup_part2(content):

    found_header = False

    cleaned = []
    for i, line in enumerate(content):

        if found_header:
            # Remove share links
            if "Twitter" and "https" in line:
                continue

            if "Your puzzle answer was" in line:
                break
            else:
                cleaned.append(line)

        elif line.startswith("----------"):
            found_header = True
            continue
    # Remove first and/or lasnt empty lines
    if cleaned[0] == "\n":
        cleaned = cleaned[1:]

    if cleaned[-1] == "\n":
        cleaned = cleaned[:-1]

    return "".join(cleaned)

def main(filepath: str):
    root_dir, year, filename = filepath.split("/")
    _, day, part = filename.split("_")

    part = int(part.replace("part", "").replace(".md", ""))

    with open(filepath, "r") as f:
        content = f.readlines()
    
    if part == 1:
        cleaned = cleanup_part1(content)
    elif part == 2:
        cleaned = cleanup_part2(content)
    else:
        raise ValueError(f"Invalid part: {part}")

    print(repr(cleaned))


if __name__ == "__main__":
    markdown_file = sys.argv[1]
    main(markdown_file)

