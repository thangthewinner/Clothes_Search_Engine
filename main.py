import os
import numpy as np
from flask import Flask, request, render_template, url_for, redirect, send_from_directory
from werkzeug.utils import secure_filename
from PIL import Image
from app.model import detect_clothes, search_similar_images
import tensorflow as tf 

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'static/uploads'
STATIC_FOLDER = 'static'
FAISS_INDEX_FILE = os.path.join(STATIC_FOLDER, 'faiss_index.index')
FILE_NAMES_FILE = os.path.join(STATIC_FOLDER, 'file_names.npy')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

DETECTION_MODEL = tf.saved_model.load("inference_graph/saved_model/")

def allowed_file(filename):
    """Check if the file is allowed based on its extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Render the main upload page."""
    return render_template('index.html')

@app.route('/static/uploads/<filename>')
def uploaded_file(filename):
    """Serve uploaded files."""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/upload', methods=['POST'])
def upload():
    """Handle file uploads and search for similar images."""
    file = request.files.get('file')
    if not file or not allowed_file(file.filename):
        return "Invalid file. Please upload a PNG, JPG, or JPEG image.", 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    file.save(filepath)

    try:
        cropped_img = detect_clothes(DETECTION_MODEL, filepath)
        cropped_filename = 'cropped_img.jpg'
        cropped_img_path = os.path.join(app.config['UPLOAD_FOLDER'], cropped_filename)
        Image.fromarray(cropped_img).save(cropped_img_path)

        if not os.path.exists(FILE_NAMES_FILE):
            return "File names data not found.", 500
        
        file_names = np.load(FILE_NAMES_FILE)
        similarity_scores, indices = search_similar_images(cropped_img_path, FAISS_INDEX_FILE)

        similar_image_paths = [
            f"{STATIC_FOLDER}/img/{file_names[idx].replace('_img_', '/img_').replace('.npy', '.jpg')}"
            for idx in indices[0]
        ]

        return render_template(
            'result.html',
            image_path=url_for('uploaded_file', filename=cropped_filename),
            original_image_path=url_for('uploaded_file', filename=filename),  # Add this line
            similar_image_paths=similar_image_paths,
            similarity_scores=similarity_scores[0]*100,
            zip=zip
        )
    except Exception as e:
        return f"Error: {str(e)}", 500

@app.route('/upload_again')
def upload_again():
    """Redirect back to the upload page."""
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)
