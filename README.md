# Blood Assassin Image Suite

A focused toolkit for generating, previewing, and integrating visual assets for the Blood Assassin project. Includes an image generator (OpenRouter + Gemini), a web UI for manual prompting, utilities to insert images into documents, and a pitch deck builder.

## Highlights

- Image generation via OpenRouter (Gemini 2.5 Flash Image)
- Web UI: type or upload prompt text, generate, preview, and download
- Batch generation from `image-prompts/*.txt`
- DOCX inserter: builds a "Visual Reference Gallery" into a character dossier
- Pitch deck generator (PPTX) with optional portraits
- Canvas design artifacts and SVG examples

## Project Structure

```
/ (repo root)
├─ generate_images.py           # Core image generation (OpenRouter)
├─ server.py                    # Flask server for Web UI and API
├─ web/                         # Static Web UI assets
│  ├─ index.html
│  ├─ app.js
│  └─ styles.css
├─ image-prompts/               # .txt prompt files for batch mode
├─ generated-images/            # Output images saved here
├─ add_images_to_dossier.py     # Inserts images into DOCX with captions/sections
├─ create_pitch_deck.py         # Generates Blood Assassin pitch deck (PPTX)
├─ FOUR-PHASE-INTEGRATION-PLAN.md
├─ README_IMAGE_GEN.md          # CLI generator usage & notes
├─ WEB_UI_README.md             # Web UI quick start & API
├─ theme-factory/
│  └─ noir_theme_guide.txt      # Minimalist noir visual style guide
├─ canvas-design/
│  ├─ README.md                 # Canvas skill test notes
│  ├─ SVG_README.md             # SVG graphics overview
│  └─ decode_pdf.sh             # Example PDF asset
└─ requirements.txt
```

## Setup

1) Python env (optional but recommended)
```bash
python3 -m venv .venv
source .venv/bin/activate
```

2) Install deps
```bash
python3 -m pip install -r requirements.txt
```

3) Configure OpenRouter key in `.env` (repo root)
```
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxxxxx
```

## Usage

### A) Web UI (manual prompting)
Run the Flask server and open the UI:
```bash
# Change port if 5000 is busy
PORT=5050 python3 server.py
```
Then visit:
- http://127.0.0.1:5050

What you can do:
- Type a prompt or upload a .txt prompt file
- Optionally set an output base name
- Generate -> Preview -> Download
- Images are saved to `generated-images/`

API endpoint (if integrating elsewhere):
- POST `/api/generate`
  - JSON: `{ "prompt": "...", "name": "base" }`
  - Multipart: `prompt_file` (.txt), optional `prompt`, `name`
  - Response: `{ images: ["file.png"...], urls: ["/generated-images/file.png"...] }`

### B) CLI batch generation
Reads all `.txt` prompts in `image-prompts/` and writes images to `generated-images/`:
```bash
python3 generate_images.py
```
Notes:
- Uses model: `google/gemini-2.5-flash-image`
- Requires valid `OPENROUTER_API_KEY` (sk-or-v1-...)

### C) Insert images into the Character Dossier (DOCX)
Adds a "Visual Reference Gallery" with portraits, locations, and scenes.
```bash
python3 add_images_to_dossier.py
# Or specify paths
python3 add_images_to_dossier.py /path/to/Blood_Assassin_Character_Dossier.docx ./generated-images
```
Outputs:
- Backs up your original DOCX
- Saves an updated DOCX with images inserted

### D) Build the Story Pitch Deck (PPTX)
Creates a visual pitch deck and includes portraits if present.
```bash
python3 create_pitch_deck.py
```
Outputs:
- `Blood_Assassin_Pitch_Deck.pptx`

## Essential Scripts and Associated Files

- Image Generator: `generate_images.py`
  - Inputs: `.env` (OPENROUTER_API_KEY), `image-prompts/*.txt`
  - Output: `generated-images/*.png|jpg`

- Web Server & UI: `server.py` + `web/`
  - Uses: `generate_images.generate_image()`
  - Serves: `/` (UI), `/api/generate`, `/generated-images/<file>`

- DOCX Inserter: `add_images_to_dossier.py`
  - Inputs: `generated-images/*.png`, `Blood_Assassin_Character_Dossier*.docx`
  - Output: Updated DOCX with gallery sections

- Pitch Deck Builder: `create_pitch_deck.py`
  - Inputs: Optional images in `generated-images/`
  - Output: `Blood_Assassin_Pitch_Deck.pptx`

- Canvas & SVG Resources: `canvas-design/`, `theme-factory/`
  - Reference docs and example assets; helpful for styling and marketing artifacts

## Troubleshooting

- 401 Unauthorized / Missing images
  - Ensure `.env` has a valid OpenRouter key (starts with `sk-or-v1-`)
- Port already in use (web UI)
  - Run with another port: `PORT=5050 python3 server.py`
- Image not appearing in DOCX
  - Verify outputs exist in `generated-images/` and are PNG/JPG, not WebP

## License
Internal project assets. If you plan to publish, add a proper license and attribution for external services used (e.g., OpenRouter).
