import os
import re

# --- Configuration ---
MD_FILE = 'file.md' # ORIGINAL FILE
OUTPUT_FILE = 'file_with_images.md' # FILE WITH TAGS REPLACED FOR IMAGES REFERENCE
IMAGE_DIR = 'images' # FILE WITH IMAGES
ALT_TEXT_FILE = 'alt_text.txt' # FILE WITH THE ALT TEXTS
# ---------------------

def get_image_map(directory):
    """Maps numbers to filenames (e.g., {1: '1-image.png'})."""
    image_map = {}
    if not os.path.exists(directory):
        print(f"Error: Directory '{directory}' not found.")
        return {}

    valid_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.webp')
    for filename in os.listdir(directory):
        if filename.lower().endswith(valid_extensions):
            match = re.match(r'^(\d+)[-_].+', filename)
            if match:
                number = int(match.group(1))
                image_map[number] = filename
    return image_map

def get_alt_texts(filepath):
    """
    Reads the text file and returns a dictionary where keys are line numbers.
    Line 1 = ID 1, Line 2 = ID 2, etc.
    """
    alt_map = {}
    if not os.path.exists(filepath):
        print(f"Warning: '{filepath}' not found. Using default alt text.")
        return alt_map

    with open(filepath, 'r', encoding='utf-8') as f:
        # enumerate starts at 0, so we use i+1 to match Image 1 to Line 1
        lines = f.readlines()
        for i, line in enumerate(lines):
            clean_line = line.strip()
            # Only store if line is not empty
            if clean_line:
                alt_map[i + 1] = clean_line
    return alt_map

def replace_tags():
    image_map = get_image_map(IMAGE_DIR)
    alt_map = get_alt_texts(ALT_TEXT_FILE)
    
    try:
        with open(MD_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: Could not find '{MD_FILE}'.")
        return

    def replacer(match):
        img_num = int(match.group(1))
        
        # Default Alt Text (if file is missing/incomplete)
        final_alt = "Alt text" 
        
        if img_num in image_map:
            filename = image_map[img_num]
            
            # Check if we have a specific alt text for this number
            if img_num in alt_map:
                final_alt = alt_map[img_num]
            
            return f"![{final_alt}]({IMAGE_DIR}/{filename})"
        else:
            print(f"Warning: [IMG {img_num}] has no matching image file.")
            return match.group(0)

    # Replace [IMG num]
    new_content = re.sub(r'\[IMG\s+(\d+)\]', replacer, content)

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"Success! Processed file saved as '{OUTPUT_FILE}'.")

if __name__ == "__main__":
    replace_tags()