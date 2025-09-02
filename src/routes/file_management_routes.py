import os
import requests
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from werkzeug.utils import secure_filename
import urllib.parse

file_management_bp = Blueprint('file_management', __name__)

# Configuration - use same path logic as data_loader
DATA_DIR = 'data'
ALLOWED_EXTENSIONS = {'csv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_google_drive_file_id(share_url):
    """Extract file ID from Google Drive sharing URL"""
    # Handle different Google Drive URL formats
    if 'drive.google.com/file/d/' in share_url:
        # Format: https://drive.google.com/file/d/FILE_ID/view
        file_id = share_url.split('/file/d/')[1].split('/')[0]
    elif 'drive.google.com/open' in share_url:
        # Format: https://drive.google.com/open\?id\=FILE_ID
        parsed_url = urllib.parse.urlparse(share_url)
        query_params = urllib.parse.parse_qs(parsed_url.query)
        file_id = query_params.get('id', [None])[0]
    else:
        return None
    return file_id

def download_from_google_drive(file_id, filename):
    """Download file from Google Drive using file ID"""
    # Use the direct download URL format
    download_url = f"https://drive.google.com/uc?export=download&id={file_id}"
    
    try:
        response = requests.get(download_url, stream=True)
        response.raise_for_status()
        
        file_path = os.path.join(DATA_DIR, filename)
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        return True, None
    except Exception as e:
        return False, str(e)

@file_management_bp.route('/files')
def file_management():
    """Display file management interface"""
    # Ensure data directory exists
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # Get list of files in data directory
    files = []
    if os.path.exists(DATA_DIR):
        for filename in os.listdir(DATA_DIR):
            if filename.endswith('.csv'):
                file_path = os.path.join(DATA_DIR, filename)
                file_size = os.path.getsize(file_path)
                files.append({
                    'name': filename,
                    'size': file_size,
                    'size_mb': round(file_size / (1024 * 1024), 2)
                })
    
    # Sort files by name
    files.sort(key=lambda x: x['name'])
    
    # Get Google Drive URL from environment variable
    default_share_url = os.environ.get('GOOGLE_DRIVE_SHARE_URL', '')
    
    return render_template('file_management.html', files=files, default_share_url=default_share_url)

@file_management_bp.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload from PC"""
    if 'file' not in request.files:
        flash('No file selected', 'error')
        return redirect(url_for('file_management.file_management'))
    
    file = request.files['file']
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('file_management.file_management'))
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(DATA_DIR, filename)
        
        # Check if file already exists
        if os.path.exists(file_path):
            flash(f'File "{filename}" already exists! Please choose a different name or delete the existing file first.', 'error')
            return redirect(url_for('file_management.file_management'))
        
        # Ensure data directory exists
        os.makedirs(DATA_DIR, exist_ok=True)
        
        # Save file
        file.save(file_path)
        flash(f'File "{filename}" uploaded successfully!', 'success')
    else:
        flash('Invalid file type. Only CSV files are allowed.', 'error')
    
    return redirect(url_for('file_management.file_management'))

@file_management_bp.route('/download_from_drive', methods=['POST'])
def download_from_drive():
    """Handle download from Google Drive sharing link"""
    share_url = request.form.get('share_url', '').strip()
    custom_filename = request.form.get('filename', '').strip()
    override_existing = request.form.get('override_existing') == 'on'
    
    if not share_url:
        flash('Please provide a Google Drive sharing URL', 'error')
        return redirect(url_for('file_management.file_management'))
    
    # Extract file ID from URL
    file_id = get_google_drive_file_id(share_url)
    if not file_id:
        flash('Invalid Google Drive URL format', 'error')
        return redirect(url_for('file_management.file_management'))
    
    # Determine filename
    if custom_filename:
        if not custom_filename.endswith('.csv'):
            custom_filename += '.csv'
        filename = secure_filename(custom_filename)
    else:
        # Use placeholder as filename if no custom name provided
        filename = "andromoney.csv"
    
    file_path = os.path.join(DATA_DIR, filename)
    
    # Check if file already exists
    if os.path.exists(file_path) and not override_existing:
        flash(f'File "{filename}" already exists! Check "Override existing file" to replace it.', 'error')
        return redirect(url_for('file_management.file_management'))
    
    # Download file
    success, error = download_from_google_drive(file_id, filename)
    
    if success:
        action = "replaced" if os.path.exists(file_path) and override_existing else "downloaded"
        flash(f'File "{filename}" {action} successfully from Google Drive!', 'success')
    else:
        flash(f'Failed to download file: {error}', 'error')
    
    return redirect(url_for('file_management.file_management'))

@file_management_bp.route('/delete/<filename>', methods=['POST'])
def delete_file(filename):
    """Delete a file from the data directory"""
    # Security check - ensure filename is safe
    filename = secure_filename(filename)
    file_path = os.path.join(DATA_DIR, filename)
    
    if os.path.exists(file_path) and filename.endswith('.csv'):
        try:
            os.remove(file_path)
            flash(f'File "{filename}" deleted successfully!', 'success')
        except Exception as e:
            flash(f'Error deleting file: {str(e)}', 'error')
    else:
        flash('File not found or invalid file type', 'error')
    
    return redirect(url_for('file_management.file_management'))
