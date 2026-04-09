# bg-remover

A simple Flask API that removes the background from images using [rembg](https://github.com/danielgatis/rembg).

## Requirements

- Python 3.9+

## Setup

1. Clone the repo and navigate to the project directory.

2. Install dependencies:
   ```bash
   pip3 install rembg Pillow flask flask-cors flask-limiter python-dotenv
   ```

3. Copy the example env file and configure it:
   ```bash
   cp .env.example .env
   ```

4. Run the server:
   ```bash
   python3 app.py
   ```

The API will be available at `http://localhost:5000`.

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `FLASK_DEBUG` | No | Set to `true` to enable debug mode. Default: `false` |
| `API_KEY` | No | Secret key for authenticating requests. If unset, auth is disabled |
| `ALLOWED_ORIGIN` | No | Production frontend URL for CORS (e.g. `https://yoursite.com`) |

For local development, the following origins are allowed by default:
`localhost:3000`, `localhost:5173`, `localhost:8080`, `localhost:4200`

## API Reference

### `POST /remove-background`

Removes the background from an uploaded image and returns a PNG.

**Headers**

| Header | Description |
|--------|-------------|
| `X-API-Key` | Required if `API_KEY` env var is set |

**Body** — `multipart/form-data`

| Field | Type | Description |
|-------|------|-------------|
| `file` | File | Image to process (`jpeg`, `png`, `webp`, `bmp`) |

**Limits**
- Max file size: 10MB
- Rate limit: 10 requests per minute per IP

**Response**

Returns the processed image as `image/png` on success.

| Status | Description |
|--------|-------------|
| `200` | Success — returns PNG image |
| `400` | Missing file, unsupported type, or corrupt image |
| `401` | Invalid or missing API key |
| `413` | File exceeds 10MB limit |
| `429` | Rate limit exceeded |

**Example**

```bash
curl -X POST http://localhost:5000/remove-background \
  -H "X-API-Key: your-secret-key" \
  -F "file=@image.jpg" \
  --output result.png
```
