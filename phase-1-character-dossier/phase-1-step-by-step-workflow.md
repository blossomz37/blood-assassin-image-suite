# Step-by-Step: Adding Images to DOCX Files via Claude

## The Problem We Solved
- Claude's container can LIST files on user's filesystem (/Users/carlo/...) via Filesystem tools
- BUT Claude cannot READ/COPY binary files from user's filesystem to the container
- Solution: User uploads files to chat → Claude processes them → User downloads result

## Complete Workflow

### Step 1: User Uploads Files to Chat
- User drags and drops files into chat interface
- Files land in: `/mnt/user-data/uploads/`
- This makes files accessible to Claude's Python scripts

### Step 2: Install Required Libraries
```bash
pip install python-docx --break-system-packages
# Also need PIL/Pillow (usually pre-installed)
```

### Step 3: Discovered Image Format Issue
- Files named `.png` were actually WebP format
- python-docx doesn't support WebP
- Check format: `file /path/to/image.png`
- Result: "RIFF (little-endian) data, Web/P image"

### Step 4: Convert WebP to PNG
```python
from PIL import Image

# Convert WebP to PNG
img = Image.open('/mnt/user-data/uploads/image.png')  # Actually WebP
temp_png = '/tmp/converted.png'
img.save(temp_png, 'PNG')  # Now proper PNG
```

### Step 5: Load DOCX and Add Content
```python
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

# Load document
doc = Document('/mnt/user-data/uploads/document.docx')

# Add page break
doc.add_page_break()

# Add header
header = doc.add_heading('Visual Reference Gallery', level=1)
header.alignment = WD_ALIGN_PARAGRAPH.CENTER

# Add section
doc.add_heading('Character Portrait', level=2)

# Add title
title_para = doc.add_paragraph()
title_run = title_para.add_run("Queen Lysandria - Portrait")
title_run.bold = True
title_run.font.size = Pt(14)
title_para.alignment = WD_ALIGN_PARAGRAPH.CENTER

# Add spacing
doc.add_paragraph()

# Add image (use converted PNG)
para = doc.add_paragraph()
run = para.add_run()
run.add_picture(temp_png, width=Inches(4.5))
para.alignment = WD_ALIGN_PARAGRAPH.CENTER

# Add spacing after
doc.add_paragraph()
```

### Step 6: Save to Outputs Directory
```python
output_file = '/mnt/user-data/outputs/document_v2.docx'
doc.save(output_file)
```

### Step 7: User Downloads Result
- File appears in outputs with download link
- Format: `[Download file](computer:///mnt/user-data/outputs/file.docx)`

## Key Lessons Learned

1. **File Upload Required**: Claude cannot directly access user's local filesystem for binary files
2. **Format Verification**: Always check actual file format (`file` command), don't trust extensions
3. **Image Conversion**: Use PIL to convert WebP→PNG before using with python-docx
4. **Path Structure**:
   - Uploads: `/mnt/user-data/uploads/`
   - Outputs: `/mnt/user-data/outputs/`
5. **Library Installation**: Use `--break-system-packages` flag in Claude's container

## Complete Working Script Template

```python
import os
from PIL import Image
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

# Paths
docx_input = "/mnt/user-data/uploads/input.docx"
image_input = "/mnt/user-data/uploads/image.png"  # May be WebP
output_file = "/mnt/user-data/outputs/output.docx"

# Convert image to proper PNG if needed
temp_png = "/tmp/converted.png"
img = Image.open(image_input)
img.save(temp_png, 'PNG')

# Load and modify document
doc = Document(docx_input)
doc.add_page_break()

# Add your content here...
header = doc.add_heading('New Section', level=1)
header.alignment = WD_ALIGN_PARAGRAPH.CENTER

para = doc.add_paragraph()
run = para.add_run()
run.add_picture(temp_png, width=Inches(4.5))
para.alignment = WD_ALIGN_PARAGRAPH.CENTER

# Save
doc.save(output_file)
print(f"✓ Saved: {os.path.getsize(output_file):,} bytes")
```

## Troubleshooting

**"UnrecognizedImageError"**
→ Image is probably WebP, convert to PNG first

**"No such file or directory: /Users/carlo/..."**
→ Need to upload files to chat, can't access local filesystem

**"externally-managed-environment"**
→ Add `--break-system-packages` flag to pip install

## Alternative: Local Script
If user prefers to run locally (doesn't need Claude to process):
- Use the script Claude created: `add_images_to_dossier.py`
- Runs on user's machine with direct filesystem access
- No upload/download needed