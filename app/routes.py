from app import app
from app.file_handler import FileHandler
from flask import render_template, jsonify, request, send_from_directory
from werkzeug.utils import secure_filename

#routes for requests and such

file_handler = FileHandler(app.config['DEVICE_FILES_FOLDER'])

#call to get file list
@app.route('/files', methods=['GET'])
def list_files():
    return jsonify(file_handler.get_file_list())

#call to get file details
@app.route('/get-file-details', methods=['GET'])
def get_file_info():
    inode = int(request.args['inode'])
    filename = request.args['name']
    try:
        file_info = file_handler.get_file_info(inode, filename)
        return jsonify(file_info)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

#call to download file
@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    return file_handler.download_file(filename)

#call to delete a file
@app.route('/delete/<filename>', methods=['DELETE'])
def delete_file(filename):
    try:
        file_handler.delete_file(filename)
        return jsonify({"success": True, "message": "File deleted successfully"})
    except FileNotFoundError:
        return jsonify({"success": False, "message": "File not found"}), 404
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    
#call to delete multiple files
@app.route('/delete-multi/', methods=['DELETE'])
def delete_multiple_files():
    print("del multi call routes")
    deleteList = request.get_json()["files"]
    
    try:
        
        file_handler.delete_multiple_files(deleteList)
        return jsonify({"success": True, "message": "File deleted successfully"})
    
    except Exception as e:
        print("error, ",e)
        return jsonify({"success": False, "message": str(e)}), 500

#call to upload file
@app.route('/upload', methods=['POST'])
def upload_to_device():
    files = request.files.getlist('file')
    return file_handler.upload_files(files)

#home
@app.route("/", methods=['GET'])
def index():
    files = file_handler.get_file_list()
    return render_template("index.html", file_list=files)
