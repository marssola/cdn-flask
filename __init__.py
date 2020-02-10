import os
import json
import time
import mimetypes
import pathlib

from flask_api import FlaskAPI, status, exceptions
from flask import jsonify, request, url_for, redirect, abort, Response

from File import saveFile
from ImageManipulation import convertImage, compressImage, resizeImage, thumbnailImage

from configure import uploadFolder
UPLOAD_FOLDER = uploadFolder()

app = FlaskAPI(__name__)

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

@app.route('/upload', methods=['POST'])
def upload():
    if len(request.files) == 0:
        response = jsonify({ 'error': 'No files uploaded' })
        response.status_code = 400
        return response

    folder = None
    quality = None
    size = None
    format = None

    if 'folder' in request.form:
        folder = request.form.get('folder')
    if 'quality' in request.form:
        quality = request.form.get('quality')
    if 'size' in request.form:
        size = request.form.get('size')
    if 'format' in request.form:
        format = request.form.get('format')
    
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

        file_extension = pathlib.Path(savedFile).suffix
        mimetype = mimetypes.types_map[file_extension]
        if mimetype in MIMES_COMPRESSION:
            savedFile = convertImage(savedFile, format)
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

@app.route('/thumbnail/<path:filename>', methods=['GET'])
def getResourceThumbnail(filename):
    filepath = UPLOAD_FOLDER + '/' + filename
    if not os.path.exists(filepath):
        return abort(404)
    
    file_extension = pathlib.Path(filepath).suffix
    mimetype = mimetypes.types_map[file_extension]
    if mimetype not in MIMES_COMPRESSION:
        return abort(400)

    size = None
    if (request.args.get('size')):
        size = request.args.get('size')
    data = thumbnailImage(filepath, size)

    return Response(data, mimetype=mimetype)

@app.route('/<path:filename>', methods=['GET'])
def getResource(filename):
    filepath = UPLOAD_FOLDER + '/' + filename
    if not os.path.exists(filepath):
        return abort(404)

    mimetype = mimetypes.guess_type(filepath)[0]
    with open(filepath, 'rb') as content:
        data = content.read()
    return Response(data, mimetype=mimetype)

if __name__ == "__main__":
    app.run(debug=True)
