from rembg import remove
from PIL import Image
from flask import Flask, request, jsonify, send_file
import io
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def remove_background(image):
    output = remove(image)
    return output

@app.route('/remove-background', methods=['POST'])
def handle_remove_background():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    input_image = Image.open(file)

    # Apply background removal
    result_image = remove_background(input_image)

    # Save to a byte stream to send without saving to disk
    img_io = io.BytesIO()
    result_image.save(img_io, 'PNG')
    img_io.seek(0)

    return send_file(img_io, mimetype='image/png')
app
if __name__ == '__main__':
    app.run(debug=True)
