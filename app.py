from flask import Flask, render_template,jsonify,request,send_from_directory
import os,random,time,signal
from hurry.filesize import size
import datetime

from werkzeug.utils import secure_filename

import requests

# npx tailwindcss -i ./static/src/input.css -o ./static/dist/css/output.css --watch

PATH = os.path.dirname(os.path.dirname(__file__))
DEVICE_FILES_FOLDER = os.path.join(os.getcwd(),"device-files")
CWD_PATH = os.getcwd()


# Check whether the specified path exists or not
pathExist = os.path.exists(os.path.join(PATH,"device-files"))

if(pathExist == False):
   os.makedirs(os.path.join(PATH,"device-files"))

app = Flask(__name__)
app.config['DEVICE_FILES_FOLDER'] = DEVICE_FILES_FOLDER


def getFileList():
    #files
    file_list_names = os.listdir(app.config['DEVICE_FILES_FOLDER'])
    file_list = []

    for file in os.listdir(app.config['DEVICE_FILES_FOLDER']):
        stat = os.stat(os.path.join(DEVICE_FILES_FOLDER,file))
        print(stat)
        #convert sizes to appropriate units and times from unix
        dataDict = {'inode':stat.st_ino, 'name':file,'size':size(stat.st_size),'last_modified':datetime.datetime.fromtimestamp(stat.st_mtime).strftime("%d/%m/%Y, %H:%M:%S")}
        file_list.append(dataDict)
    return file_list

# file list
@app.route('/files', methods=['GET'])
def listFiles():
    return jsonify(getFileList())

# get details of singular file via inode
@app.route('/get-file-details', methods=['GET'])
def getFileInfo():

    fileDetailsDict = {}
    print(request)
    inode = int(request.args['inode'])
    filename = request.args['name']
    print(inode,filename)
    stat = os.stat(os.path.join(DEVICE_FILES_FOLDER,filename))

    # check if the files match
    if(stat.st_ino != inode):
        print("ERROR! Das a big problem.")

    print(f"Filename: {filename}")
    print(f"Inode: {stat.st_ino}")
    print(f"Size: {stat.st_size} bytes")
    print(f"Permissions: {oct(stat.st_mode)}")
    print(f"Last modified: {stat.st_mtime}")

    filename,filetype = os.path.splitext(filename)

    fileDetailsDict = {
        "inode": stat.st_ino,
        "filename": filename,
        "filetype": filetype,
        "size": size(stat.st_size),
        "last_modified": datetime.datetime.fromtimestamp(stat.st_mtime).strftime("%d/%m/%Y, %H:%M:%S"),
    }

    return jsonify(fileDetailsDict)

#download a file from this dev
@app.route('/download/<filename>')
def downloadFile(filename):
    filename = secure_filename(filename)  # Ensure the filename is secure
    return send_from_directory(app.config['DEVICE_FILES_FOLDER'], filename, as_attachment=True)

#Delete a file
@app.route('/delete/<filename>', methods=['DELETE'])
def deleteFile(filename):
    filename = secure_filename(filename)  # Ensure the filename is secure
    file_path = os.path.join(app.config['DEVICE_FILES_FOLDER'], filename)
    try:
        os.remove(file_path)
        return jsonify({"success": True, "message": "File deleted successfully"}), 200
    except FileNotFoundError:
        return jsonify({"success": False, "message": "File not found"}), 404
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


# upload files to deviceS
@app.route('/upload', methods=['POST'])
def uploadToDevice():
    print("upload ran!")
    
    print("req ",request.files)    
    files = request.files.getlist('file')
    for file in files:
        print(file)
        if file:
            print("valid file")
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['DEVICE_FILES_FOLDER'], filename))
            filename = os.path.join(app.config['DEVICE_FILES_FOLDER'],filename)
        else:
            print("invalid file")
           
    return jsonify({"success": True})


@app.route("/", methods=['GET', 'POST'])
@app.route("/index")
def index():
    return render_template("index.html", file_list=getFileList())

if __name__ == '__main__':
    app.run(debug=True)
