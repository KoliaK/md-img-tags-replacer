import re
import os

# --- Configuration ---
MD_FILE = 'clean_file_with_tags.md' # The file you are editing manually
IMAGE_DIR = 'images'                # Your images folder
# ---------------------

def validate_project():
    print(f"--- Validating '{MD_FILE}' against '{IMAGE_DIR}/' ---")
    
    # 1. Read Markdown and find all [IMG n] tags
    try:
        with open(MD_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: File '{MD_FILE}' not found.")
        return

    # Find all numbers in [IMG n] tags
    # findall returns a list of strings: ['1', '2', '5']
    found_tags = [int(n) for n in re.findall(r'\[IMG\s+(\d+)\]', content)]
    found_tags.sort()

    if not found_tags:
        print("No [IMG n] tags found in the file.")
        return

    print(f"Found {len(found_tags)} tags. Range: {min(found_tags)} to {max(found_tags)}")

    # 2. Check for Duplicates
    # If set length is different from list length, we have dupes
    if len(set(found_tags)) != len(found_tags):
        print("\n[!] DUPLICATE TAGS FOUND:")
        seen = set()
        dupes = set()
        for x in found_tags:
            if x in seen:
                dupes.add(x)
            seen.add(x)
        print(f"    Numbers used multiple times: {sorted(list(dupes))}")
    else:
        print("\n[OK] No duplicate tags.")

    # 3. Check for Missing Numbers (Gaps)
    # We expect 1, 2, 3... if there is a gap, report it
    full_set = set(range(min(found_tags), max(found_tags) + 1))
    existing_set = set(found_tags)
    missing = sorted(list(full_set - existing_set))
    
    if missing:
        print("\n[!] MISSING NUMBERS IN SEQUENCE:")
        print(f"    skipped: {missing}")
    else:
        print("\n[OK] Sequence is continuous (no gaps).")

    # 4. Check if Images Actually Exist
    print("\n[?] CHECKING IMAGE FILES:")
    missing_files = []
    
    # Get all numbered files from directory
    dir_files = os.listdir(IMAGE_DIR)
    dir_map = {} # { 1: "1-foo.png" }
    
    for fname in dir_files:
        match = re.match(r'^(\d+)[-_].+', fname)
        if match:
            dir_map[int(match.group(1))] = fname

    # Check every tag found in MD against the directory map
    for tag_num in found_tags:
        if tag_num not in dir_map:
            missing_files.append(tag_num)

    if missing_files:
        print(f"    [FAIL] The following tags exist in '{MD_FILE}' but NO matching image in '{IMAGE_DIR}':")
        print(f"    {missing_files}")
    else:
        print("    [OK] All tags have a corresponding image file.")

if __name__ == "__main__":
    validate_project()