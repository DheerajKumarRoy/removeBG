from flask import Flask, render_template, request, redirect, url_for, send_file, after_this_request
import os
from rembg import remove
from PIL import Image
import glob

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['PROCESSED_FOLDER'] = 'processed'

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

if not os.path.exists(app.config['PROCESSED_FOLDER']):
    os.makedirs(app.config['PROCESSED_FOLDER'])

def remove_bg_rembg(input_path, output_path):
    input_image = Image.open(input_path)
    output_image = remove(input_image)
    
    # Check if the image has an alpha channel
    if output_image.mode == 'RGBA':
        output_image = output_image.convert('RGB')
    
    output_image.save(output_path, 'JPEG')

def cleanup_directory(directory):
    files = glob.glob(os.path.join(directory, '*'))
    for file in files:
        try:
            os.remove(file)
            print(f'Successfully removed {file}')
        except Exception as e:
            print(f'Error removing {file}: {e}')

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
    if file:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        
        output_path = os.path.join(app.config['PROCESSED_FOLDER'], 'processed_' + file.filename)
        remove_bg_rembg(filepath, output_path)
        
        return redirect(url_for('download_file', filename='processed_' + file.filename))

@app.route('/download/<filename>')
def download_file(filename):
    file_path = os.path.join(app.config['PROCESSED_FOLDER'], filename)

    @after_this_request
    def cleanup(response):
        cleanup_directory(app.config['UPLOAD_FOLDER'])
        cleanup_directory(app.config['PROCESSED_FOLDER'])
        return response

    return send_file(file_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')
