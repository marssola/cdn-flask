import os
from random import random
from slugify import slugify

from configure import uploadFolder
UPLOAD_FOLDER = uploadFolder()

def saveFile(file, name, folder=None, format=None):
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
