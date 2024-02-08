from flask import Flask
import os

app = Flask(__name__, template_folder='../templates',static_folder='../static')
app.config['DEVICE_FILES_FOLDER'] = os.path.join(os.getcwd(), "device-files")

from app import routes
