import os
import json
import time
from random import random
import mimetypes

from flask_api import FlaskAPI, status, exceptions
from flask import jsonify, request, url_for, redirect
from slugify import slugify
from PIL import Image

app = FlaskAPI(__name__)

UPLOAD_FOLDER='./upload'
PUBLIC_FOLDER='./public'

mimetypes.init()
MIMES_COMPRESSION = [
    'image/jpeg',
    'image/png'
]

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'online': True
    })

def compressImage(file, quality = None):
    if not quality:
        quality = 80
    filepath = UPLOAD_FOLDER + file

    image = Image.open(filepath)
    image.save(filepath, image.format, optimize=True, quality=quality)
    return

def resizeImage(file, size = None):
    if not size:
        return
    filepath = UPLOAD_FOLDER + file
    image = Image.open(filepath)
    width, height = image.size
    print(width, height)

    return

def saveFile(file, name, folder=None, format = None):
    path = ''
    if folder:
        path += '/' + folder
    
    if not os.path.exists(UPLOAD_FOLDER + path):
        os.makedirs(UPLOAD_FOLDER + path)

    if name == 'file':
        name = str(int(random() * 1000000000000000))
    path += '/' + slugify(name.lower())

    if not format:
        format = file.filename.split('.')[-1]
    path += '.' + format

    file.save(UPLOAD_FOLDER + path)
    return path


@app.route('/upload', methods=['POST'])
def upload():
    if len(request.files) == 0:
        response = jsonify({ 'error': 'No files uploaded' })
        response.status_code = 400
        return response

    folder = None
    quality = None
    size = None

    if 'folder' in request.form:
        folder = request.form.get('folder')
    if 'quality' in request.form:
        quality = request.form.get('quality')
    if 'size' in request.form:
        size = request.form.get('size')
    
    files = []
    for key, file in request.files.items():
        if file.filename == '':
            response = jsonify({ 'error': 'No file selected for uploading' })
            response.status_code = 400
            return response
        
        data = {}
        data['name'] = key
        data['file'] = file
        data['folder'] = folder
        savedFile = saveFile(**data)
        
        file_name, file_extension = os.path.splitext(savedFile)
        mimetype = mimetypes.types_map[file_extension]
        if mimetype in MIMES_COMPRESSION:
            compressImage(savedFile, quality)
            resizeImage(savedFile, size)
        
        files.append(savedFile)

    
    message = { 'success': 'Request successfully uploaded' }
    if len(files) == 1:
        message['file'] = files[0]
    else:
        message['files'] = files

    response = jsonify(message)
    response.status_code = 201
    return response


if __name__ == "__main__":
    app.run(debug=True)