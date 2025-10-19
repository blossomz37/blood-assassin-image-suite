# Image Insertion Script for Blood Assassin Character Dossier

## Quick Start

1. **Install python-docx** (if not already installed):
   ```bash
   pip install python-docx
   ```

2. **Run the script** from your project directory:
   ```bash
   cd ~/2025_10_19_Claude_Skills_Practice
   python3 add_images_to_dossier.py
   ```

3. **Done!** The script will:
   - Create a backup of your original file (`Blood_Assassin_Character_Dossier_backup.docx`)
   - Add all 12 images organized into sections
   - Save the updated document

## What the Script Does

The script adds your generated images to the document in an organized Visual Reference Gallery with three sections:

1. **Character Portraits**
   - Elara Nightshade
   - Queen Lysandria
   - Seraphiel

2. **Key Locations**
   - Prophecy Chamber
   - Crimson Court Throne Room
   - Rebel Encampment
   - Blood Moon Fortress

3. **Key Scenes**
   - Elara vs Lysandria Confrontation
   - Nightbringer Manifestation
   - Twilight Accord Signing
   - Elara Midnight Hunt
   - Seraphiel Celestial Powers

## Manual Usage

If you need to specify custom paths:

```bash
python3 add_images_to_dossier.py /path/to/document.docx /path/to/images/
```

## Troubleshooting

**"python-docx not installed"**
```bash
pip install python-docx
# or
pip3 install python-docx
```

**"Document not found"**
- Make sure you're running from the correct directory
- Or provide the full path as an argument

**"Images directory not found"**
- Ensure the `generated-images` folder exists in your project
- Or provide the full path as a second argument

## Output

The script creates:
- `Blood_Assassin_Character_Dossier_backup.docx` - Your original file (backup)
- `Blood_Assassin_Character_Dossier.docx` - Updated file with images

## Notes

- Images are added at the END of the document in a new "Visual Reference Gallery" section
- Each image has a centered title and is properly sized
- The original document content is preserved
- A backup is automatically created before modification