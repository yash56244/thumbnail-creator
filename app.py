import os
import time
import hashlib
import random
from flask import Flask, render_template, redirect, url_for, request
from flask_uploads import UploadSet, configure_uploads, IMAGES, \
    patch_request_class
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import SubmitField
from PIL import Image
from resizeimage import resizeimage
basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = '\xe2\xaez\xe9-vH\xea\xa2V\x04\xc5\xed\xde'
app.config['UPLOADED_PHOTOS_DEST'] = os.path.join(basedir, 'uploads')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)
patch_request_class(app)
db = SQLAlchemy(app)


class UploadForm(FlaskForm):

    photo = FileField(validators=[FileAllowed(photos, 'Image Only!'),
                      FileRequired('Choose a file!')])
    submit = SubmitField('Upload')


class Mapping(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    original = db.Column(db.String(20), nullable=False)
    thumbnail = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return 'Mapping({}, {})'.format(self.original, self.thumbnail)


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    form = UploadForm()
    if form.validate_on_submit():
        for filename in request.files.getlist('photo'):
            str_name = 'admin' + str(int(time.time()))
            name = hashlib.md5(str_name.encode('utf-8'
                               )).hexdigest()[:15]
            photos.save(filename, name=name + '.')
            str_name2 = 'yash' + str(int(time.time()))
            name2 = hashlib.md5(str_name2.encode('utf-8'
                                )).hexdigest()[:15]
            resize(name, name2)
            mapp = Mapping(original=name, thumbnail=name2)
            db.session.add(mapp)
            db.session.commit()
        success = True
    else:
        success = False
    return render_template('index.html', form=form, success=success)


@app.route('/manage')
def manage_file():
    files_list = Mapping.query.all()
    return render_template('manage.html', files_list=files_list,
                           photos=photos)


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
