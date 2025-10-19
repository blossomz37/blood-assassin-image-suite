# Web UI for Image Generation

This adds a small web interface and API on top of your existing generator.

## Quick start

1) Optional: create a virtualenv
```bash
python3 -m venv .venv
source .venv/bin/activate
```

2) Install dependencies
```bash
python3 -m pip install -r requirements.txt
```

3) Set your API key in `.env` (repo root)
```
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxxxxx
```

4) Run the server
```bash
python3 server.py
```

5) Open the UI
- Visit http://127.0.0.1:5000
- Type a prompt or upload a .txt file
- Optionally set an output base name (defaults to “image” or the file stem)
- Click Generate, then preview and download your images

Optional: Temporary API key input
- The UI has a password field where you can paste a temporary `OPENROUTER_API_KEY` (prefix `sk-or-v1-`).
- This key is sent only with your request and is NOT stored server-side.
- If omitted, the server falls back to the `.env` key.

Deploying to Railway
- This server binds to `0.0.0.0` and respects the `PORT` env var automatically.
- Set your `OPENROUTER_API_KEY` as a Railway environment variable.

## API
- POST /api/generate
  - JSON: `{ "prompt": "text...", "name": "optional-base-name" }`
  - Multipart form: `prompt_file` (.txt), optional `prompt`, optional `name`
  - Response: `{ "images": ["name.png", ...], "urls": ["/generated-images/name.png", ...] }`

## Files
- `server.py` — Flask server for the UI and API
- `web/index.html`, `web/app.js`, `web/styles.css` — Static UI assets
- Saves images to `generated-images/` (already in this repo)

## Notes
- Uses your `generate_images.py` as-is; only the return value of `generate_image` was enhanced to list saved filenames.
- The CLI mode of `generate_images.py` still works to batch process `image-prompts/*.txt`.
