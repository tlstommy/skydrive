#!/usr/bin/env python

#file_handler - handles all file operations for the device
#Copyright (C) 2024 Thomas Logan Smith

#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <https://www.gnu.org/licenses/>.

import os, datetime
from werkzeug.utils import secure_filename
from flask import send_from_directory,send_file,jsonify
import zipfile
import mimetypes


#file ops
class FileHandler:
    def __init__(self, files_folder):
        self.device_files_folder = files_folder
        mimetypes.init()


    #function to clac size instead of hurry.filesize cred so
    def size(self,size):
        for unit in ("", "K", "M", "G", "T"):
            if abs(size) < 1024.0:
                return f"{size:3.1f}{unit}B"
            size /= 1024.0
        return "null"

    #get list of the files
    def get_file_list(self, relative_path=""):

        relative_path = relative_path.replace(self.device_files_folder,"")
        
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
                    'size': self.size(stat.st_size) if not is_directory else "—",
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
       
        if os.path.exists(os.path.join(self.device_files_folder,filename_full)):
            stat = os.stat(os.path.join(self.device_files_folder,filename_full))
            path = os.path.join(self.device_files_folder,filename_full)
        else:
            print(os.path.join(path,filename_full))
            stat = os.stat(os.path.join(path,filename_full))
            path = os.path.join(path,filename_full)

        filename = filename_full
        
        # check if the files match
        if(stat.st_ino != inode):
            print('ERROR! file mismatch.')
        
        #print(f'Filename: {filename}')
        #print(f'Inode: {stat.st_ino}')
        #print(f'Size: {stat.st_size} bytes')
        #print(f'Permissions: {oct(stat.st_mode)}')
        #print(f'Last modified: {stat.st_mtime}')


        #check if its a dir
        is_directory = os.path.isdir(os.path.join(self.device_files_folder,filename_full))
        
        filename,filetype = os.path.splitext(filename)

        file_details_dict = {
            'inode': stat.st_ino,
            'filename': filename,
            'filetype': filetype,
            'size': self.size(stat.st_size),
            'last_modified': datetime.datetime.fromtimestamp(stat.st_mtime).strftime('%d/%m/%Y, %H:%M:%S'),
            'fileID':str(filename+filetype),
            'is_dir':is_directory,
            'path':str(os.path.join(self.device_files_folder,filename_full))
        }

        return file_details_dict

    #download a single file
    def download_file(self, filename):

        head, tail = os.path.split(filename)
        secure_tail = secure_filename(tail)
        secure_path = os.path.join(head, secure_tail)

        return send_from_directory(directory=self.device_files_folder, path=secure_path, as_attachment=True)
        
    #download multiple files
    def download_multiple_files_cleanup(self):
        zipfile_name = 'downloaded_files.zip'
        zipfile_path = os.path.join(self.device_files_folder, zipfile_name)
        os.remove(zipfile_path)

    def download_multiple_files(self, files):
        
        zipfile_name = 'downloaded_files.zip'
        zipfile_path = os.path.join(self.device_files_folder, zipfile_name)

        #make zip of the selected files
        with zipfile.ZipFile(zipfile_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file in files:
                full_path = os.path.join(self.device_files_folder, file)
                
                
                head, tail = os.path.split(file)
                
                #root check
                if head == '/':
                    head = ''

                secure_tail = secure_filename(tail)
                secure_path = os.path.join(head, secure_tail)
                
                file_to_zip = os.path.join(self.device_files_folder, secure_path)
                
                if os.path.exists(file_to_zip):
                    zipf.write(file_to_zip, arcname=secure_tail)
                else:
                    print(f'File not found: {secure_path}')
                

        return send_from_directory(directory=self.device_files_folder, path=zipfile_name, as_attachment=True)

    


    #delete a single file
    def delete_file(self, filename):
        
        head, tail = os.path.split(filename)
        print(head,tail)
        secure_tail = secure_filename(tail)
        secure_path = os.path.join(head, secure_tail)
        print("Sec path: ",secure_path)
        fp = os.path.join(self.device_files_folder,secure_path)
        print(fp)
        os.remove(fp)

    #del multiple files
    def delete_multiple_files(self,files):
        print('delete multi call')
        print(files)
        for file in files:
            
            head, tail = os.path.split(file)

            print("TEST: |",head,tail)

            filename = secure_filename(file)
            full_path = os.path.join(self.device_files_folder, filename)


            if os.path.exists(full_path):
                os.remove(full_path)
                print(f'File removed: {full_path}')
            else:
                print(f'File not found: {full_path}')
        


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
    def preview_file(self,filename,path):
        
        if(path == '/'):
            path = ''
        
        
        filename = os.path.join(path,filename)
        
        filename = filename.replace("/mnt/nvme/data/","")
        valid_application_types = ['pdf','pdf']
        filename =(filename)
        
        filetype,encoding = mimetypes.guess_type(filename)
        
        #unsupported mimetype
        if(filetype == None and encoding == None):
            return f"Unable to preview file, {filename}."
        
        if(filetype.split("/")[0] == 'application' and encoding == None):
            if(filetype.split("/")[1] not in valid_application_types):
                return f"Unable to preview file, {filename}."
        

        split_dir = os.path.join(self.device_files_folder,filename).rsplit(os.path.sep,1)
        


        return send_from_directory(directory=split_dir[0], path=split_dir[1],as_attachment=False)
    