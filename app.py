from rembg import remove, new_session
from PIL import Image, UnidentifiedImageError
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from functools import wraps
import imghdr
import io
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# --- CORS ---
# Allows common localhost dev ports + an optional production origin via env var.
# When ready for production, set ALLOWED_ORIGIN=https://yoursite.com
allowed_origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:8080",
    "http://localhost:4200",
]
if os.getenv("ALLOWED_ORIGIN"):
    allowed_origins.append(os.getenv("ALLOWED_ORIGIN"))

CORS(app, origins=allowed_origins)

# --- File size limit: 10MB ---
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024

# --- Rate limiting ---
limiter = Limiter(get_remote_address, app=app)

# --- Constants ---
ALLOWED_IMAGE_TYPES = {"jpeg", "png", "webp", "bmp"}

# Load model once at startup instead of on every request
rembg_session = new_session("u2netp")

# --- API key auth ---
# Set API_KEY env var to enable. Unset = no auth (convenient for local dev).
API_KEY = os.getenv("API_KEY")

def require_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if API_KEY and request.headers.get("X-API-Key") != API_KEY:
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated


@app.route("/remove-background", methods=["POST"])
@limiter.limit("10 per minute")
@require_api_key
def handle_remove_background():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    file_bytes = file.read()

    # Validate actual file content (not client-supplied MIME type)
    detected_type = imghdr.what(None, h=file_bytes)
    if detected_type not in ALLOWED_IMAGE_TYPES:
        return jsonify({"error": "Unsupported or invalid image file"}), 400

    try:
        input_image = Image.open(io.BytesIO(file_bytes))
    except UnidentifiedImageError:
        return jsonify({"error": "Invalid or corrupt image"}), 400

    result_image = remove(input_image, session=rembg_session)

    img_io = io.BytesIO()
    result_image.save(img_io, "PNG")
    img_io.seek(0)

    print('image sent')

    return send_file(img_io, mimetype="image/png")


if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_DEBUG", "false").lower() == "true")
