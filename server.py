#!/usr/bin/env python3
"""
Tiny Flask server to expose image generation over HTTP and serve a static UI.

Endpoints:
- GET / -> serve web UI
- POST /api/generate -> generate images from prompt text or uploaded .txt file
- GET /generated-images/<filename> -> serve generated images
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import List, Optional

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

# Local import
from generate_images import generate_image, OUTPUT_DIR, PROMPTS_DIR, OPENROUTER_API_KEY

ROOT = Path(__file__).parent
WEB_DIR = ROOT / "web"

app = Flask(__name__, static_folder=str(WEB_DIR), static_url_path="")
CORS(app)


@app.route("/")
def index():
    # Serve the static index.html
    index_path = WEB_DIR / "index.html"
    if not index_path.exists():
        return "UI not built. Missing web/index.html", 404
    return app.send_static_file("index.html")


@app.route("/api/generate", methods=["POST"])
def api_generate():
    """
    Accepts either JSON body { prompt: string, name?: string }
    or multipart/form-data with fields:
      - prompt_file: uploaded .txt file (optional)
      - prompt: text (optional)
      - name: base output filename without extension (optional)
    Returns: { images: ["filename.png", ...] }
    """
    # Check auth quickly to fail fast with meaningful error
    if not OPENROUTER_API_KEY or not str(OPENROUTER_API_KEY).startswith("sk-or-v1-"):
        return jsonify({
            "error": "Missing or invalid OPENROUTER_API_KEY. Check your .env and restart server."
        }), 400

    prompt_text: Optional[str] = None
    base_name: str = "image"

    if request.content_type and request.content_type.startswith("application/json"):
        data = request.get_json(silent=True) or {}
        prompt_text = (data.get("prompt") or "").strip() or None
        base_name = (data.get("name") or base_name).strip() or base_name
    else:
        # multipart form
        if "prompt_file" in request.files:
            f = request.files["prompt_file"]
            try:
                text = f.read().decode("utf-8", errors="ignore").strip()
                if text:
                    prompt_text = text
                # Use the uploaded filename (stem) if provided and name not set
                if f.filename:
                    stem = Path(f.filename).stem
                    if stem:
                        base_name = stem
            except UnicodeDecodeError:
                # Keep going; user may also provide text in textarea
                pass
        form_prompt = (request.form.get("prompt") or "").strip()
        if form_prompt:
            prompt_text = form_prompt
        form_name = (request.form.get("name") or "").strip()
        if form_name:
            base_name = form_name

    if not prompt_text:
        return jsonify({"error": "No prompt provided. Provide JSON {prompt} or upload a .txt file."}), 400

    images: List[str] = generate_image(prompt_text, base_name) or []

    if not images:
        return jsonify({"error": "No images returned from model."}), 502

    # Return URLs for the generated files
    urls = [f"/generated-images/{name}" for name in images]
    return jsonify({"images": images, "urls": urls})


@app.route('/generated-images/<path:filename>')
def serve_generated(filename: str):
    directory = str(OUTPUT_DIR.resolve())
    return send_from_directory(directory, filename, as_attachment=False)


@app.route('/image-prompts/<path:filename>')
def serve_prompts(filename: str):
    # Optional: expose prompt files for convenience in UI if needed
    directory = str(PROMPTS_DIR.resolve())
    return send_from_directory(directory, filename, as_attachment=False)


def main():
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="127.0.0.1", port=port, debug=True)


if __name__ == "__main__":
    main()
