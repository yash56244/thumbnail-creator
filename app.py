import os
import time
import hashlib
import random
from flask import Flask, render_template, redirect, url_for, request
from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import SubmitField
from PIL import Image
from resizeimage import resizeimage
basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = '\xe2\xaez\xe9-vH\xea\xa2V\x04\xc5\xed\xde'
app.config['UPLOADED_PHOTOS_DEST'] = os.path.join(basedir, 'uploads') 

photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)
patch_request_class(app) 
class UploadForm(FlaskForm):
    photo = FileField(validators=[FileAllowed(photos, 'Image Only!'), FileRequired('Choose a file!')])
    submit = SubmitField('Upload')
class File:
    def __init__(self, name1, name2):
        self.original = name1
        self.thumbnail = name2
files_list = []

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    form = UploadForm()
    if form.validate_on_submit():
        for filename in request.files.getlist('photo'):
            str_name='admin' + str(int(time.time()))
            name = hashlib.md5(str_name.encode("utf-8")).hexdigest()[:15]
            photos.save(filename, name=name + '.')
            str_name2='yash' + str(int(time.time()))
            name2 = hashlib.md5(str_name2.encode("utf-8")).hexdigest()[:15]
            resize(name, name2)
            files_list.append(File(name, name2))
        success = True
    else:
        success = False
    return render_template('index.html', form=form, success=success)


@app.route('/manage')
def manage_file():
    return render_template('manage.html', files_list=files_list, photos = photos)


@app.route('/open/<filename>')
def open_file(filename):
    file_url = photos.url(filename + '.jpg')
    return render_template('browser.html', file_url=file_url)


def resize(name, name2):
    with Image.open('uploads/' + name + '.jpg') as image:
        cover = resizeimage.resize_cover(image, [200, 200])
        cover.save('static/' + name2 + '.jpg', image.format)

if __name__ == '__main__':
    app.run(debug=True)