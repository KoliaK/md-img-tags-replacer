import re
import os
import shutil

# --- Configuration ---
INPUT_FILE = 'clean_file_with_tags.md'  # File with [IMG n] tags
OUTPUT_FILE = 'clean_file_renumbered.md' # New file with [IMG 1]...[IMG 100]
ALT_TEXT_FILE = 'backup_alt_text.txt'    # Your existing alt text file
NEW_ALT_FILE = 'backup_alt_text_renumbered.txt'
IMAGE_DIR = 'images'                     # Folder to check for filenames
# ---------------------

def renumber_sequence():
    # 1. Read the Markdown
    try:
        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: '{INPUT_FILE}' not found.")
        return

    # 2. Read existing Alt Texts (if available)
    old_alts = {}
    if os.path.exists(ALT_TEXT_FILE):
        with open(ALT_TEXT_FILE, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for i, line in enumerate(lines):
                # Line 1 = ID 1, Line 2 = ID 2...
                if line.strip():
                    old_alts[i + 1] = line.strip()
    
    # 3. Scan and Replace
    # We use a mutable counter inside the replacer function
    counter = {'val': 0}
    
    # Stores mapping: { New_ID : Old_ID }
    # e.g. { 1: 5 } means New [IMG 1] was originally [IMG 5]
    id_map = {}

    def replacer(match):
        old_num = int(match.group(1))
        counter['val'] += 1
        new_num = counter['val']
        
        # Record the mapping
        id_map[new_num] = old_num
        
        return f"[IMG {new_num}]"

    new_content = re.sub(r'\[IMG\s+(\d+)\]', replacer, content)
    total_tags = counter['val']

    # 4. Save the Renumbered Markdown
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    # 5. Save the Renumbered Alt Texts
    # We look up what "New ID 1" used to be, and grab that alt text
    if old_alts:
        with open(NEW_ALT_FILE, 'w', encoding='utf-8') as f:
            for i in range(1, total_tags + 1):
                original_id = id_map[i]
                text = old_alts.get(original_id, "") # Empty if original didn't have text
                f.write(f"{text}\n")

    print(f"--- SUCCESS ---")
    print(f"Renumbered {total_tags} tags.")
    print(f"Markdown saved to: {OUTPUT_FILE}")
    if old_alts:
        print(f"Alt texts reordered to: {NEW_ALT_FILE}")

    # 6. Generate Image Renaming Instructions
    print(f"\n--- FILE RENAMING PLAN ---")
    print("(Run these changes in your 'images' folder to match the new tags)")
    
    # Get actual files in directory
    if os.path.exists(IMAGE_DIR):
        files = os.listdir(IMAGE_DIR)
        # Create map of { number: filename }
        file_map = {}
        for fname in files:
            match = re.match(r'^(\d+)[-_].+', fname)
            if match:
                file_map[int(match.group(1))] = fname

        # Check what needs to change
        instructions = []
        for new_id in range(1, total_tags + 1):
            old_id = id_map[new_id]
            
            # If the old file exists
            if old_id in file_map:
                old_filename = file_map[old_id]
                # Construct new filename: "1-filename.png"
                # Remove old number prefix
                clean_name = re.sub(r'^\d+[-_]', '', old_filename)
                new_filename = f"{new_id}-{clean_name}"
                
                if new_id != old_id:
                     instructions.append(f"RENAME: {old_filename}  -->  {new_filename}")
                elif new_id == old_id:
                     # e.g. 1 -> 1, no change needed
                     pass
            else:
                instructions.append(f"MISSING: New [IMG {new_id}] needs an image (was [IMG {old_id}])")
        
        # Print results
        if instructions:
            for line in instructions:
                print(line)
        else:
            print("Files are already perfectly numbered!")
            
        # WARNING about duplicates
        # If ID 5 appears twice in text, it becomes ID 5 and ID 6.
        # The script will tell you to rename "5-img.png" to "5-img.png" AND "6-img.png".
        # Since you can't rename one file twice, you'll need to COPY it.
        values = list(id_map.values())
        if len(values) != len(set(values)):
            print("\n[!] WARNING: DUPLICATES DETECTED")
            print("Some original images appear multiple times in the text.")
            print("You will need to COPY the original file to satisfy the new unique numbers.")

if __name__ == "__main__":
    renumber_sequence()