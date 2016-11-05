import os
from flask import Flask, render_template, request, redirect, url_for, jsonify
from werkzeug.utils import secure_filename
from flask_wtf import FlaskForm
from wtforms import SelectField, HiddenField
from flask_wtf.file import FileField, FileAllowed
from rq import Queue
from redis import Redis
import random
from process import detect_faces

app = Flask(__name__)
app.config.from_pyfile('facedemo.cfg')
try:
    app.config.from_pyfile('facedemo_local.cfg')
except IOError:
    pass

redis_conn = Redis()
q = Queue('facedemo', connection=redis_conn)


CLASSIFIERS = [
    ('haarcascade_frontalface_default.xml', 'face (default)'),
    ('haarcascade_frontalface_alt.xml', 'face (alternative)'),
    ('haarcascade_eye.xml', 'eye'),
    ('haarcascade_mcs_mouth.xml', 'mouth'),
    ('haarcascade_frontalcatface_extended.xml', 'cat face')
]


class FaceForm(FlaskForm):
    image = FileField('Your image', validators=[FileAllowed(['jpg', 'png'], 'Images only!')])
    scale_factor = SelectField('Scale factor', choices=[(str(v), v) for v in [x / 10.0 for x in range(11, 16, 1)]])
    min_neighbors = SelectField('Minimum Neighbors', choices=[(str(v), v) for v in range(1, 6, 1)])
    min_size = SelectField('Minimum size', choices=[(str(v), v) for v in range(50, 250, 50)])
    classifier = SelectField('Classifier', choices=CLASSIFIERS)
    image_filename = HiddenField('Current image')
    image_path = HiddenField('Current image path')


def choose_test():
    files = [f for f in os.listdir('static/tests') if f[-4:] == '.jpg']
    return random.choice(files)


@app.route('/facedemo/', methods=('GET', 'POST'))
def detect_face():
    form = FaceForm()
    if form.validate_on_submit():
        if form.image.has_file():
            filename = secure_filename(form.image.data.filename)
            path = 'uploads'
            filepath = os.path.join('static', path, filename)
            form.image.data.save(filepath)
        elif form.image_filename.data:
            filename = form.image_filename.data
            path = form.image_path.data
        else:
            path = 'tests'
            filename = choose_test()
        form.image_filename.data = filename
        form.image_path.data = path
        job = q.enqueue(detect_faces, ' | '.join([filename, path, form.scale_factor.data, form.min_neighbors.data, form.min_size.data, form.classifier.data]))
        return render_template('facedemo.html', form=form, job_id=job.id, path=path, filename=filename)
    else:
        filename = choose_test()
        form.image_filename.data = filename
        form.image_path.data = 'tests'
        return render_template('facedemo.html', form=form, image=os.path.join('tests', filename))


@app.route('/facedemo/check/<job_id>/')
def check_face_job(job_id):
    job = q.fetch_job(job_id)
    if job.result:
        result = job.result
    else:
        result = 'Waiting'
    return result


if __name__ == '__main__':
    app.run(host='0.0.0.0')
