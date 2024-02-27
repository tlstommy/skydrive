import os, datetime
from hurry.filesize import size
from werkzeug.utils import secure_filename
from flask import send_from_directory,send_file
import zipfile


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
                'truncate_name': 'test',
                'name': secure_filename(file),
                'size': size(stat.st_size),
                'last_modified': datetime.datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
            }
            file_list.append(dataDict)
        return file_list


    #get info of a file
    def get_file_info(self, inode, filename, filename_full):
        fileDetailsDict = {}
        
        print(inode,filename,filename_full)
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

        filename,filetype = os.path.splitext(filename)

        fileDetailsDict = {
            'inode': stat.st_ino,
            'filename': filename,
            'filetype': filetype,
            'size': size(stat.st_size),
            'last_modified': datetime.datetime.fromtimestamp(stat.st_mtime).strftime('%d/%m/%Y, %H:%M:%S'),
            'fileID':str(filename+filetype)
        }

        print(fileDetailsDict)

        return fileDetailsDict

    #download a single file
    def download_file(self, filename):
        print('download single file run')
        filename = secure_filename(filename)
        return send_from_directory(directory=self.device_files_folder, path=filename, as_attachment=True)
        
    #download multiple files
    def download_multiple_files_cleanup(self):
        zipFilename = 'downloaded_files.zip'
        zipFP = os.path.join(self.device_files_folder, zipFilename)
        os.remove(zipFP)

    def download_multiple_files(self,files):
        print('download multi call')

        zipFilename = 'downloaded_files.zip'
        zipFP = os.path.join(self.device_files_folder, zipFilename)


        #make a zip of the selected files
        with zipfile.ZipFile(zipFP, 'w') as zipf:
            for file in files:
                
                filename = secure_filename(file)
                file_path = os.path.join(self.device_files_folder, filename)
                
                # Check if the file exists
                if os.path.exists(file_path):
                    zipf.write(file_path, arcname=filename)
                else:
                    print(f'File not found: {file}')

        sentfile = send_file(zipFP)

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
    
    #preview files
    def preview_file(self,filename):

        validPreviewExts = ['jpg','png','jpeg','gif','webm','pdf','pdf']
        

        filename = secure_filename(filename)
        
        print(filename.split('.')[-1])
        print(f'preview file ran, {filename}')
        return send_from_directory(directory=self.device_files_folder, path=filename,as_attachment=False)
        
