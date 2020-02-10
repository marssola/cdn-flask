import os
import pathlib
from io import BytesIO
from PIL import Image

from configure import uploadFolder
UPLOAD_FOLDER = uploadFolder()

def convertImage(file, format=None):
    if not format:
        return file

    filepath = UPLOAD_FOLDER + file
    file_name, file_extension = os.path.splitext(file)
    file_extension = file_extension.replace('.', '')

    if file_extension == format:
        return file

    image = Image.open(filepath)
    image = image.convert('RGB')

    os.remove(filepath)

    file = file_name + '.' + format
    filepath = UPLOAD_FOLDER + file
    image.save(filepath)

    return file


def compressImage(file, quality=None):
    if not quality:
        quality = 80
    filepath = UPLOAD_FOLDER + file

    image = Image.open(filepath)
    image.save(filepath, image.format, optimize=True, quality=quality)
    return

def getImageFitSize(width, height, size):
    greaterWidth = width > height
    w = 0
    h = 0

    if size.find('x') > -1:
        w = int(size.split('x')[0])
        h = int(size.split('x')[1])
    elif size.find('w') > -1:
        w = int(size.replace('w', ''))
    elif size.find('h') > -1:
        h = int(size.replace('h', ''))
        greaterWidth = False
    else:
        if greaterWidth:
            w = int(size)
        else:
            h = int(size)

    if greaterWidth:
        percent = (w / float(width))
        h = int((float(height) * float(percent)))
    else:
        percent = (h / float(height))
        w = int(float(width) * float(percent))

    return {'width': w, 'height': h}

def resizeImage(file, size=None):
    if not size:
        return

    filepath = UPLOAD_FOLDER + file
    image = Image.open(filepath)
    width, height = image.size
    size = getImageFitSize(width, height, size)

    image = image.resize((size['width'], size['height']), Image.ANTIALIAS)
    image.save(filepath)

    return


def thumbnailImage(file, size=None):
    image = Image.open(file)
    width, height = image.size
    if size:
        size = getImageFitSize(width, height, size)
    else:
        size = { 'width': 150, 'height': 150 }

    bIO = BytesIO()
    
    image.thumbnail((size['width'], size['height']), Image.ANTIALIAS)
    image.save(bIO, image.format)

    return bIO.getvalue()
