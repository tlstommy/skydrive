import os, datetime
from hurry.filesize import size
from werkzeug.utils import secure_filename
from flask import send_from_directory,send_file,jsonify
import zipfile
import mimetypes


#file ops
class FileHandler:
    def __init__(self, files_folder):
        self.device_files_folder = files_folder
        mimetypes.init()


    #get list of the files
    def get_file_list(self, relative_path=""):
        path = os.path.join(self.device_files_folder, relative_path.strip("/"))
        
        # If the path is a file, get the directory
        if os.path.isfile(path):
            path = os.path.dirname(path)

        print("Directory path: ", path)

        file_list = []
        # Check if the path is a directory or not
        if os.path.isdir(path):
            for item in os.listdir(path):
                full_path = os.path.join(path, item)
                stat = os.stat(full_path)
                is_directory = os.path.isdir(full_path)
                dataDict = {
                    'inode': stat.st_ino,
                    'name': secure_filename(item),
                    'size': size(stat.st_size) if not is_directory else "—",
                    'last_modified': datetime.datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                    'is_directory': is_directory,
                    'path': os.path.dirname(full_path) if not is_directory else full_path
                }
                file_list.append(dataDict)
        return file_list



    #get info of a file
    def get_file_info(self, inode, filename, filename_full,path):
        file_details_dict = {}
        
        print(inode,filename,filename_full,path)
        stat = os.stat(os.path.join(self.device_files_folder,filename_full))
        filename = filename_full
        print(stat)

        # check if the files match
        if(stat.st_ino != inode):
            print('ERROR! file mismatch.')
        
        print(f'Filename: {filename}')
        print(f'Inode: {stat.st_ino}')
        print(f'Size: {stat.st_size} bytes')
        print(f'Permissions: {oct(stat.st_mode)}')
        print(f'Last modified: {stat.st_mtime}')


        #check if its a dir
        is_directory = os.path.isdir(os.path.join(self.device_files_folder,filename_full))
        print("is dir?: " , is_directory)

        

        filename,filetype = os.path.splitext(filename)

        file_details_dict = {
            'inode': stat.st_ino,
            'filename': filename,
            'filetype': filetype,
            'size': size(stat.st_size),
            'last_modified': datetime.datetime.fromtimestamp(stat.st_mtime).strftime('%d/%m/%Y, %H:%M:%S'),
            'fileID':str(filename+filetype),
            'is_dir':is_directory,
            'path':str(os.path.join(self.device_files_folder,filename_full))
        }

        print(file_details_dict)

        return file_details_dict

    #download a single file
    def download_file(self, filename):
        print('download single file run')
        filename = secure_filename(filename)
        return send_from_directory(directory=self.device_files_folder, path=filename, as_attachment=True)
        
    #download multiple files
    def download_multiple_files_cleanup(self):
        zipfile_name = 'downloaded_files.zip'
        zipfile_path = os.path.join(self.device_files_folder, zipfile_name)
        os.remove(zipfile_path)

    def download_multiple_files(self,files):
        print('download multi call')

        zipfile_name = 'downloaded_files.zip'
        zipfile_path = os.path.join(self.device_files_folder, zipfile_name)


        #make a zip of the selected files
        with zipfile.ZipFile(zipfile_path, 'w') as zipf:
            for file in files:
                
                filename = secure_filename(file)
                file_path = os.path.join(self.device_files_folder, filename)
                
                # Check if the file exists
                if os.path.exists(file_path):
                    zipf.write(file_path, arcname=filename)
                else:
                    print(f'File not found: {file}')

        sentfile = send_file(zipfile_path)

        #intercept another request after this to delete the zip
        return sentfile


    #delete a single file
    def delete_file(self, filename):
        filename = secure_filename(filename)
        full_path = os.path.join(self.device_files_folder, filename)
        os.remove(full_path)

    #del multiple files
    def delete_multiple_files(self,files):
        print('delete multi call')
        print(files)
        for file in files:
            filename = secure_filename(file)
            full_path = os.path.join(self.device_files_folder, filename)
            os.remove(full_path)

    #upload a file/s
    def upload_files(self, files):
        for file in files:
            if file:
                filename = secure_filename(file.filename)
                file.save(os.path.join(self.device_files_folder, filename))
        return {'success': True, 'message': 'Files uploaded successfully'}
    
    def convert_to_pdf(self,mode,file):
        return

    #preview files
    def preview_file(self,filename):

        valid_application_types = ['pdf','pdf']
        filename = secure_filename(filename)
        
        filetype,encoding = mimetypes.guess_type(filename)
        print(filetype)
        print(encoding)
        print(type(encoding))
        #unsupported mimetype
        if(filetype == None and encoding == None):
            return f"Unable to preview file, {filename}."
        
        if(filetype.split("/")[0] == 'application' and encoding == None):
            if(filetype.split("/")[1] not in valid_application_types):
                return f"Unable to preview file, {filename}."
        
        print(filename.split('.')[-1])
        print(f'preview file ran, {filename}')
        return send_from_directory(directory=self.device_files_folder, path=filename,as_attachment=False)