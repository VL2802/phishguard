# PhishGuard — Clean Extension UI

This version restructures the Stitch design into:

- `manifest.json` — extension configuration
- `popup.html` — structure and the three UI states
- `popup.css` — all styling
- `popup.js` — state changes and interaction
- `assets/logo.svg` — supplied Stitch PhishGuard logo

## UI flow

1. Ready: "Inspect this email"
2. Analyzing: loading state
3. Result: phishing probability + indicators

## Next development step

Replace the simulated `setTimeout()` in `popup.js` with a request to your Python/FastAPI ML backend.

## Important

The original Stitch export used Tailwind CDN and remote Google font/icon resources. Those are convenient for a design mockup but should not be your final extension architecture because browser extensions have stricter Content Security Policy rules.

For a production extension, bundle your fonts/icons locally or replace the Material Symbols with local SVG icons.
