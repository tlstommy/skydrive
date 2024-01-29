from flask import Flask, render_template,jsonify,request
import os,random,time,signal
from hurry.filesize import size
import datetime

from werkzeug.utils import secure_filename

import requests


PATH = os.path.dirname(os.path.dirname(__file__))
DEVICE_FILES_FOLDER = os.path.join(os.getcwd(),"device-files")
CWD_PATH = os.getcwd()


# Check whether the specified path exists or not
pathExist = os.path.exists(os.path.join(PATH,"device-files"))

if(pathExist == False):
   os.makedirs(os.path.join(PATH,"device-files"))

app = Flask(__name__)
app.config['DEVICE_FILES_FOLDER'] = DEVICE_FILES_FOLDER

#files
file_list_names = os.listdir(app.config['DEVICE_FILES_FOLDER'])
file_list = []

for file in os.listdir(app.config['DEVICE_FILES_FOLDER']):
    stat = os.stat(os.path.join(DEVICE_FILES_FOLDER,file))

    #convert sizes to appropriate units and times from unix
    dataDict = {'name':file,'size':size(stat.st_size),'last_modified':datetime.datetime.fromtimestamp(stat.st_mtime).strftime("%d/%m/%Y, %H:%M:%S")}
    file_list.append(dataDict)

#upload files to deviceS
@app.route('/upload', methods=['POST'])
def uploadToDevice():
    print("upload ran!")
    print(request)
    print("req ",request.files)    
    files = request.files.getlist('file')
    for file in files:
        print(file)
        if file:
            print("valid file")
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['DEVICE-FILES-FOLDER'], filename))
            filename = os.path.join(app.config['DEVICE-FILES-FOLDER'],filename)
        else:
            print("invalid file")
           
    return jsonify({"success": True})
    

@app.route("/", methods=['GET', 'POST'])
@app.route("/index")
def index():
    return render_template("index.html", file_list=file_list)

if __name__ == '__main__':
    app.run(debug=True)
