import re
import os

# --- Configuration ---
INPUT_FILE = 'messy_file.md'         # THE FILE WITH MESSY TAGS
OUTPUT_FILE = 'clean_file_with_tags.md'        # THE OUTPUT WITH [IMG n] TAGS
BACKUP_ALT_FILE = 'backup_alt_text.txt' # SAVES THE PREVIOUS ALT TEXTS
# ---------------------

def revert_and_extract():
    try:
        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: Could not find '{INPUT_FILE}'.")
        return

    # Dictionary to hold { image_number: "alt text string" }
    extracted_alts = {}

    def replacer(match):
        # group(1) is the Alt Text inside ![...]
        current_alt = match.group(1)
        # group(2) is the path inside (...)
        full_path = match.group(2)
        
        filename = os.path.basename(full_path)
        
        # Look for leading number in filename (e.g. "12" from "12-image.png")
        num_match = re.match(r'^(\d+)[-_\.]', filename)
        
        if num_match:
            number = int(num_match.group(1))
            
            # Save the alt text to our dictionary
            extracted_alts[number] = current_alt
            
            # Replace the tag in the markdown
            return f"[IMG {number}]"
        else:
            # If no number found, change nothing
            return match.group(0)

    # Regex captures both the Alt Text (group 1) and the URL (group 2)
    new_content = re.sub(r'!\[(.*?)\]\((.*?)\)', replacer, content)

    # 1. Save the clean Markdown
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f"File cleaned and saved to '{OUTPUT_FILE}'.")

    # 2. Save the Backup Alt Text
    if extracted_alts:
        max_id = max(extracted_alts.keys())
        print(f"Extracting alt text up to Image {max_id}...")
        
        with open(BACKUP_ALT_FILE, 'w', encoding='utf-8') as f:
            # Loop from 1 to the highest image number found
            for i in range(1, max_id + 1):
                # Get the text if it exists, otherwise write an empty line
                text = extracted_alts.get(i, "")
                f.write(f"{text}\n")
        
        print(f"Alt text backup saved to '{BACKUP_ALT_FILE}'.")
    else:
        print("No numbered images found to extract.")

if __name__ == "__main__":
    revert_and_extract()