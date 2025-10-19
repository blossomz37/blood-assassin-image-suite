# Blood Assassin Image Generator

Automated image generation script using OpenRouter API and Google's Gemini 2.5 Flash Image model.

## Setup

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure API key:**
   - Copy `.env.template` to `.env`
   - Get your OpenRouter API key from: https://openrouter.ai/keys
   - Add your key to `.env`:
     ```
     OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxx
     ```
    - Note: Keys must be standard OpenRouter keys (prefix `sk-or-v1-`). Project keys (e.g., `sk-proj-...`) are not accepted for `chat/completions` and will return 401.

3. **Ensure prompts exist:**
   - Prompts should be in the `image-prompts/` directory
   - Each prompt should be a `.txt` file

## Usage

Run the script:
```bash
python generate_images.py
```

The script will:
- Read all `.txt` files from `image-prompts/`
- Send each prompt to Gemini 2.5 Flash Image via OpenRouter
- Save generated images to `generated-images/` with matching filenames
- Add a 2-second delay between requests to respect rate limits
 - Perform an auth pre-check and print a masked key prefix

## Output

Generated images will be saved as:
- `generated-images/01_elara_nightshade_portrait.png`
- `generated-images/02_queen_lysandria_portrait.png`
- etc.

## Notes

- Model: `google/gemini-2.5-flash-image`.
- Image responses are base64 data URLs returned under `choices[0].message.images[*].image_url.url`.
- We explicitly request image outputs with `modalities: ["image", "text"]` as required by OpenRouter's Image Generation docs.
- The script includes an auth pre-check (`/api/v1/models`), improved error messages, timeouts, and safer request handling.
- See OpenRouter docs for aspect ratio (`image_config.aspect_ratio`) and pricing.

## Troubleshooting

**"OPENROUTER_API_KEY not found"**
- Ensure `.env` file exists in the project root
- Verify the key is correctly formatted

**Request timeouts**
- Increase timeout value in the script (default 30s per request)
- Check your internet connection

**Unexpected response format**
- Ensure you're including `"modalities": ["image", "text"]` in the request.
- The script expects base64 data URLs in `message.images`. If a provider changes format, the script falls back to checking inline `message.content` for a data URL.
- If you still see no images, verify your model supports image output and try again.

**401 Unauthorized / "No auth credentials found"**
- Ensure your key starts with `sk-or-v1-` and is copied exactly into `.env`.
- Project keys (e.g., `sk-proj-...`) may work for some endpoints but will fail on `chat/completions`.
- After updating `.env`, re-run the script so it reloads the key.