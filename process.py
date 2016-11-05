import os
import cv2
import cv2.cv as cv
import uuid


CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
STATIC_DIR = os.path.join(CURRENT_DIR, 'static')

# Change this if necessary
# FACE_CLASSIFIER = '/usr/local/Cellar/opencv/2.4.12/share/OpenCV/haarcascades/haarcascade_frontalface_default.xml'
# FACE_CLASSIFIER = '/usr/share/opencv/haarcascades/haarcascade_frontalface_default.xml'

if 'home' in CURRENT_DIR:
    CLASSIFIER_PATH = '/usr/share/opencv/haarcascades/'
else:
    CLASSIFIER_PATH = '/usr/local/Cellar/opencv/2.4.12/share/OpenCV/haarcascades/'


def detect_faces(data):
    filename, path, scale_factor, min_neighbors, min_size, classifier = data.split(' | ')
    newfile = '{}.jpg'.format(uuid.uuid4())
    face_cl = cv2.CascadeClassifier(os.path.join(CLASSIFIER_PATH, classifier))
    try:
        image = cv2.imread(os.path.join(STATIC_DIR, path, filename))
        oh, ow = image.shape[:2]
        if ow > 800:
            ih = int((800.00 / ow) * oh)
            iw = 800
            image = cv2.resize(image, (iw, ih), interpolation=cv2.INTER_AREA)
            cv2.imwrite(os.path.join(STATIC_DIR, path, filename), image)
        grey = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        faces = face_cl.detectMultiScale(grey, scaleFactor=float(scale_factor), minNeighbors=int(min_neighbors), minSize=(int(min_size), int(min_size)), flags=cv.CV_HAAR_SCALE_IMAGE)
        print faces
    except cv2.error:
        raise
    else:
        for (x, y, w, h) in faces:
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.imwrite(os.path.join(STATIC_DIR, 'processed', newfile), image)
    print os.path.join('processed', newfile)
    return os.path.join('processed', newfile)
