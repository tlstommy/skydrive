import os, datetime
from hurry.filesize import size
from werkzeug.utils import secure_filename
from flask import send_from_directory


#file ops
class FileHandler:
    def __init__(self, files_folder):
        self.device_files_folder = files_folder

    #get list of the files
    def get_file_list(self):
        file_list = []
        for file in os.listdir(self.device_files_folder):
            full_path = os.path.join(self.device_files_folder, file)
            stat = os.stat(full_path)
            dataDict = {
                'inode': stat.st_ino,
                'name': secure_filename(file),
                'size': size(stat.st_size),
                'last_modified': datetime.datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
            }
            file_list.append(dataDict)
        return file_list


    #get info of a file
    def get_file_info(self, inode, filename):
        fileDetailsDict = {}
        
        print(inode,filename)
        stat = os.stat(os.path.join(self.device_files_folder,filename))

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

        print(fileDetailsDict)

        return fileDetailsDict

    #download a single file
    def download_file(self, filename):
        filename = secure_filename(filename)
        return send_from_directory(directory=self.device_files_folder, path=filename, as_attachment=True)

    #delete a single file
    def delete_file(self, filename):
        filename = secure_filename(filename)
        full_path = os.path.join(self.device_files_folder, filename)
        os.remove(full_path)

    #upload a single file
    def upload_files(self, files):
        for file in files:
            if file:
                filename = secure_filename(file.filename)
                file.save(os.path.join(self.device_files_folder, filename))
        return {"success": True, "message": "Files uploaded successfully"}
