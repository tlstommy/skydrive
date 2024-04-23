from flask import Flask
from flask_httpauth import HTTPBasicAuth
from functools import wraps

import json
import os

settings_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config/settings.json")
with open(settings_file, "r") as f:
    settings_data = json.load(f)


app = Flask(__name__, template_folder='../templates',static_folder='../static')
app.config['REQUIRE_AUTH'] = settings_data["require_pass"]


app.config['DEVICE_FILES_FOLDER'] = "/mnt/nvme/data"
auth = HTTPBasicAuth()


from app import routes
