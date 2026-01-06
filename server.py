"""
Vector My Shit MVP - Image to SVG conversion service
Uses vtracer for high-quality bitmap to vector conversion
"""

import os
import uuid
import vtracer
from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
from PIL import Image
import io
import base64

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def convert_to_svg(input_path, output_path, options=None):
    """
    Convert image to SVG using vtracer
    
    Options:
    - colormode: 'color' or 'binary'
    - hierarchical: 'stacked' or 'cutout'
    - mode: 'spline', 'polygon', or 'none'
    - filter_speckle: remove small artifacts (default 4)
    - color_precision: color clustering precision (default 6)
    - layer_difference: color difference for layering (default 16)
    - corner_threshold: corner detection (default 60)
    - length_threshold: path simplification (default 4.0)
    - max_iterations: optimization iterations (default 10)
    - splice_threshold: curve splice threshold (default 45)
    - path_precision: decimal precision for paths (default 8)
    """
    
    opts = options or {}
    
    vtracer.convert_image_to_svg_py(
        input_path,
        output_path,
        colormode=opts.get('colormode', 'color'),
        hierarchical=opts.get('hierarchical', 'stacked'),
        mode=opts.get('mode', 'spline'),
        filter_speckle=opts.get('filter_speckle', 4),
        color_precision=opts.get('color_precision', 6),
        layer_difference=opts.get('layer_difference', 16),
        corner_threshold=opts.get('corner_threshold', 60),
        length_threshold=opts.get('length_threshold', 4.0),
        max_iterations=opts.get('max_iterations', 10),
        splice_threshold=opts.get('splice_threshold', 45),
        path_precision=opts.get('path_precision', 8)
    )

@app.route('/')
def index():
    html_path = os.path.join(os.path.dirname(__file__), 'index.html')
    with open(html_path, 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/api/convert', methods=['POST'])
def convert():
    """Handle image upload and conversion to SVG"""
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed. Use PNG, JPG, GIF, BMP, or WebP'}), 400
    
    # Check file size
    file.seek(0, 2)
    size = file.tell()
    file.seek(0)
    
    if size > MAX_FILE_SIZE:
        return jsonify({'error': 'File too large. Maximum size is 10MB'}), 400
    
    try:
        # Generate unique filenames
        file_id = str(uuid.uuid4())
        original_ext = file.filename.rsplit('.', 1)[1].lower()
        input_filename = f"{file_id}.{original_ext}"
        output_filename = f"{file_id}.svg"
        
        input_path = os.path.join(UPLOAD_FOLDER, input_filename)
        output_path = os.path.join(OUTPUT_FOLDER, output_filename)
        
        # Save uploaded file
        file.save(input_path)
        
        # Get conversion options from request
        options = {
            'colormode': request.form.get('colormode', 'color'),
            'hierarchical': request.form.get('hierarchical', 'stacked'),
            'mode': request.form.get('mode', 'spline'),
            'filter_speckle': int(request.form.get('filter_speckle', 4)),
            'color_precision': int(request.form.get('color_precision', 6)),
            'layer_difference': int(request.form.get('layer_difference', 16)),
            'corner_threshold': int(request.form.get('corner_threshold', 60)),
            'length_threshold': float(request.form.get('length_threshold', 4.0)),
            'max_iterations': int(request.form.get('max_iterations', 10)),
            'splice_threshold': int(request.form.get('splice_threshold', 45)),
            'path_precision': int(request.form.get('path_precision', 8))
        }
        
        # Convert to SVG
        convert_to_svg(input_path, output_path, options)
        
        # Read the SVG content
        with open(output_path, 'r') as f:
            svg_content = f.read()
        
        # Get file sizes for stats
        input_size = os.path.getsize(input_path)
        output_size = os.path.getsize(output_path)
        
        # Clean up input file (keep output for download)
        os.remove(input_path)
        
        return jsonify({
            'success': True,
            'file_id': file_id,
            'svg': svg_content,
            'stats': {
                'original_size': input_size,
                'svg_size': output_size
            }
        })
        
    except Exception as e:
        # Clean up on error
        if os.path.exists(input_path):
            os.remove(input_path)
        return jsonify({'error': str(e)}), 500

@app.route('/api/download/<file_id>')
def download(file_id):
    """Download the converted SVG file"""
    filename = f"{file_id}.svg"
    filepath = os.path.join(OUTPUT_FOLDER, filename)
    
    if not os.path.exists(filepath):
        return jsonify({'error': 'File not found'}), 404
    
    return send_file(
        filepath,
        mimetype='image/svg+xml',
        as_attachment=True,
        download_name='vectorized.svg'
    )

@app.route('/api/health')
def health():
    return jsonify({'status': 'ok', 'service': 'vector-my-shit-mvp'})

if __name__ == '__main__':
    # Use environment variable for port (for production) or default to 5001 for local dev
    port = int(os.environ.get('PORT', 5001))
    debug = os.environ.get('FLASK_ENV') != 'production'
    app.run(debug=debug, host='0.0.0.0', port=port)
