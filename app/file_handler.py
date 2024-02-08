import os, datetime
from hurry.filesize import size
from werkzeug.utils import secure_filename
from flask import send_from_directory

class FileHandler:
    def __init__(self, files_folder):
        self.files_folder = files_folder

    def get_file_list(self):
        file_list = []
        for file in os.listdir(self.files_folder):
            full_path = os.path.join(self.files_folder, file)
            stat = os.stat(full_path)
            dataDict = {
                'inode': stat.st_ino,
                'name': secure_filename(file),
                'size': size(stat.st_size),
                'last_modified': datetime.datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
            }
            file_list.append(dataDict)
        return file_list

    def get_file_info(self, inode, filename):
        full_path = os.path.join(self.files_folder, secure_filename(filename))
        stat = os.stat(full_path)
        if stat.st_ino != inode:
            raise ValueError("File inode does not match.")
        file_info = {
            "inode": stat.st_ino,
            "filename": filename,
            "size": size(stat.st_size),
            "last_modified": datetime.datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
        }
        return file_info

    def download_file(self, filename):
        filename = secure_filename(filename)
        return send_from_directory(directory=self.files_folder, path=filename, as_attachment=True)

    def delete_file(self, filename):
        filename = secure_filename(filename)
        full_path = os.path.join(self.files_folder, filename)
        os.remove(full_path)

    def upload_files(self, files):
        for file in files:
            if file:
                filename = secure_filename(file.filename)
                file.save(os.path.join(self.files_folder, filename))
        return {"success": True, "message": "Files uploaded successfully"}
