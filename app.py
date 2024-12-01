from flask import Flask, render_template, request, send_from_directory, redirect, url_for
import os
import uuid
from psd_tools import PSDImage
from PIL import Image

# Initialize Flask app
app = Flask(__name__)

# Set the directory for file uploads and converted files
UPLOAD_FOLDER = 'static/uploads'
CONVERTED_FOLDER = 'static/converted'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['CONVERTED_FOLDER'] = CONVERTED_FOLDER

# Create folders if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CONVERTED_FOLDER, exist_ok=True)

# Function to convert PSD to JPEG
def convert_psd_to_jpeg(psd_file_path, jpeg_file_path, quality=85):
    # Open the PSD file
    psd = PSDImage.open(psd_file_path)
    
    # Composite the image to create a full image (flattening the layers)
    composite_image = psd.composite()

    # Convert the composite image (PIL Image) to RGB mode if it's in another mode (e.g., RGBA)
    if composite_image.mode != 'RGB':
        composite_image = composite_image.convert('RGB')

    # Save the image as a JPEG
    composite_image.save(jpeg_file_path, 'JPEG', quality=quality)

    print(f"Converted {psd_file_path} to {jpeg_file_path} with quality={quality}")

# Function to convert PSD to Thumbnail (JPEG)
def convert_psd_to_thumbnail(psd_file_path, thumbnail_file_path, max_size=320):
    # Open the PSD file
    psd = PSDImage.open(psd_file_path)
    
    # Composite the image to create a full image (flattening the layers)
    composite_image = psd.composite()

    # Convert the composite image (PIL Image) to RGB mode if it's in another mode (e.g., RGBA)
    if composite_image.mode != 'RGB':
        composite_image = composite_image.convert('RGB')

    # Resize the image to create a thumbnail (max dimension of 320 px)
    composite_image.thumbnail((max_size, max_size))

    # Save the thumbnail as JPEG
    composite_image.save(thumbnail_file_path, 'JPEG')

    print(f"Converted {psd_file_path} to thumbnail at {thumbnail_file_path} with max size={max_size} px")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    
    file = request.files['file']
    
    if file.filename == '':
        return redirect(request.url)
    
    if file and file.filename.lower().endswith('.psd'):
        filename = str(uuid.uuid4()) + '.psd'
        psd_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(psd_path)

        # Define the output JPEG and thumbnail file paths
        jpeg_filename = filename.replace('.psd', '.jpeg')
        jpeg_path = os.path.join(app.config['CONVERTED_FOLDER'], jpeg_filename)
        
        thumbnail_filename = filename.replace('.psd', '_thumbnail.jpeg')
        thumbnail_path = os.path.join(app.config['CONVERTED_FOLDER'], thumbnail_filename)

        # Convert PSD to JPEG and Thumbnail
        convert_psd_to_jpeg(psd_path, jpeg_path)
        convert_psd_to_thumbnail(psd_path, thumbnail_path)

        return render_template('index.html', jpeg_filename=jpeg_filename, thumbnail_filename=thumbnail_filename)
    else:
        return "Please upload a valid PSD file.", 400

@app.route('/downloads/<filename>')
def download_file(filename):
    return send_from_directory(app.config['CONVERTED_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)
