from app import app,auth
from app.file_handler import FileHandler
from flask import render_template, jsonify, request, send_from_directory,make_response,flash,session, redirect, url_for
from flask_httpauth import HTTPBasicAuth
from functools import wraps
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

import urllib.parse
import os,subprocess,json,random,time

#routes for requests and such

file_handler = FileHandler(app.config['DEVICE_FILES_FOLDER'])

PATH = os.path.dirname(os.path.dirname(__file__))

with open(os.path.join(PATH,"config/pass")) as passfile:
    pw = str(passfile.readline().strip())
    
    
    app.secret_key = (pw+str(len(pw)))
    print(app.secret_key)
    hashed_password = generate_password_hash(pw)


print("PATH:  ",PATH)
def load_settings():
    
    with open(os.path.join(PATH,"config/settings.json")) as jf:
        settings_data = json.load(jf)

        print(settings_data.get("pcie_gen3_mode"))
        return [settings_data.get("pcie_gen3_mode"),settings_data.get("require_pass"),settings_data.get("apmode")]
        


def save_settings(use_gen3=None,reqPass=None,netmode=None):
    settings_file = os.path.join(PATH, "config/settings.json")
    # Load existing settings
    if os.path.exists(settings_file):
        with open(settings_file, "r") as f:
            settings_data = json.load(f)
    else:
        settings_data = {}

    # Update settings based on provided parameters
    if use_gen3 is not None:
        settings_data["pcie_gen3_mode"] = use_gen3
    if reqPass is not None:
        settings_data["require_pass"] = reqPass
    if netmode is not None:
        settings_data["apmode"] = netmode

    # Save updated settings
    with open(settings_file, "w") as f:
        json.dump(settings_data, f, indent=4)


def size(size):
    for unit in ("", "K", "M", "G", "T"):
        if abs(size) < 1024.0:
            return f"{size:3.1f}{unit}B"
        size /= 1024.0
    return "null"

@app.route('/secure-page')
def secure_page():
    if app.config['REQUIRE_AUTH']:
        if not session.get('authenticated'):
            return redirect(url_for('login'))
        return "This is a secure page."


#for login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password')
        if check_password_hash(hashed_password, password):
            session['authenticated'] = True 
            return redirect(url_for('index'))
        else:
            return render_template('login.html',login_status='Invalid Password!')
    return render_template('login.html')



#call to get file list
@app.route('/files', methods=['GET'])
def list_files():
    print("/files areg")
    print(request.args)

    if(request.args['path']):
        return jsonify(file_handler.get_file_list(request.args['path']))
    else:
        return jsonify(file_handler.get_file_list())

#call to get file details
@app.route('/get-file-details', methods=['GET'])
def get_file_info():
    inode = int(request.args['inode'])
    filename = request.args['name']
    filename_full = request.args['fullname']
    path = request.args['path']
    print("reqg args below")
    print(request.args)

    print(f"debug path: {urllib.parse.unquote(path)}/{filename_full}")
    try:
        file_info = file_handler.get_file_info(inode, filename,filename_full,urllib.parse.unquote(path))
        
        return jsonify(file_info)
    except Exception as e:
        print(f"Error: {e}")
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
    
#call to download multiple files
@app.route('/download-multi/', methods=['POST'])
def download_multiple_files():
    print("download multi call routes")
    fileList = request.get_json()["files"]
    if fileList:
        try:
            #call the download_multiple_files method from FileHandler
            return file_handler.download_multiple_files(fileList)
        except Exception as e:
            print(e)
            return jsonify({"error": str(e)}), 500
    else:
        return jsonify({"error": "No files provided"}), 400
#cleanup call for above
@app.route('/download-multi-cleanup/', methods=['POST'])
def download_multiple_files_cleanup():
    print('download multi cleanup call')
    try:
        #call the download_multiple_files method from FileHandler
        file_handler.download_multiple_files_cleanup()
        return jsonify({"success": True, "message": "File deleted successfully"})
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500


#call to upload file
@app.route('/upload', methods=['POST'])
def upload_to_device():
    files = request.files.getlist('file')
    return file_handler.upload_files(files)

#preview file call,figure out what to do for pdf/img/office docs
@app.route('/preview-file', methods=['GET'])
def preview_file():
    filename = request.args['name']
    path = request.args['path']
    print(f"pf: {request.args}")
    resp = make_response(file_handler.preview_file(filename,path))
    resp.headers['Content-Disposition'] = 'inline'
    return resp

#settings/help page
#home
@app.route("/settings", methods=['GET','POST'])
def settings():
    print(session.get('authenticated'))
    if app.config['REQUIRE_AUTH']:
        if not session.get('authenticated'):
            return redirect(url_for('login'))


    print("req ",request.form)




    #power settings pressed check

    if(request.form.get('settings-power-restart') == 'restart'):
        print('restarting')
        os.system("sudo reboot")
        

    if(request.form.get('settings-power-shutdown') == 'shutdown'):
        print('shutting down')
        os.system("sudo shutdown")
        
    cpu_temp = int(subprocess.check_output('cat /sys/class/thermal/thermal_zone0/temp', shell=True, text=True))/1000  
    gpu_temp = subprocess.check_output('vcgencmd measure_temp', shell=True, text=True).replace("temp=","").replace("'C","")
    storage_array = subprocess.check_output("df /mnt/nvme | awk -F ' ' '{print $3}{print $4}' | tail -n 2", shell=True, text=True).split("\n")

    #* 1000 for 1kb block size
    bytes_used = int(storage_array[0]) * 1000
    bytes_available = int(storage_array[1]) * 1000
    bytes_total = bytes_available + bytes_used

    print(bytes_total)
    
    print(storage_array)
        

    

    
    return render_template("settings.html",cpuTemp = cpu_temp, gpuTemp = gpu_temp, usedBytes=size(int(storage_array[0]) * 1000),totalBytes=size(int(bytes_total)),usagePercent=round((bytes_used/bytes_total)* 100,2))

@app.route("/get_settings", methods=['GET'])
def get_settings():
    # Ensure to return a boolean value
    return jsonify({"pcie-gen3-mode": load_settings()[0],"require-pass": load_settings()[1],"wifi-mode": load_settings()[2]})

@app.route("/set_settings", methods=['POST'])
def set_settings():
    print(request.form)
    
    # Check if 'pcieMode' is present in the request and handle it
    if 'pcieMode' in request.form:
        useGen3 = request.form.get('pcieMode') == 'true'
        print("PCIe Mode:", useGen3)
        save_settings(use_gen3=useGen3)

        if useGen3:
            print("Enabling Gen 3")
            subprocess.run(["sudo", "sed", "-i", "s/dtparam=pciex1/dtparam=pciex1_gen=3/", "/boot/firmware/config.txt"], check=True)
        else:
            print("Enabling Gen 1")
            subprocess.run(["sudo", "sed", "-i", "s/dtparam=pciex1_gen=3/dtparam=pciex1/", "/boot/firmware/config.txt"], check=True)

    # Check if 'passmode' is present in the request and handle it by changing settings file
    if 'passmode' in request.form:
        reqPass = request.form.get('passmode') == 'true'
        print("Require Password:", reqPass)
        save_settings(reqPass=reqPass)

    if 'netmode' in request.form:
        netmode = request.form.get('netmode') == 'true'
        print("net Mode:", netmode)
        save_settings(netmode=netmode)

        
        if netmode:
            print("Enabling ap")

            with open(os.path.join(PATH,"config/pass")) as passfile:
                password = str(passfile.readline().strip())
                
            subprocess.run(["sudo","nmcli","device","wifi","hotspot","ssid","SkyDrive","password",password], check=True)
        else:
            print("disconnecting ap and reconncecting to previous network at wlan0")
            subprocess.run(["sudo","nmcli","device","disconnect","wlan0","&","sudo","nmcli","device","up","wlan0",">","pythonouttext.txt"], check=True)

            

        
        
    response_data = {
        "pcie-gen3-mode": 'pcieMode' in request.form and request.form.get('pcieMode') == 'true',
        "require-pass": 'passMode' in request.form and request.form.get('passMode') == 'true',
        "wifi-mode": 'netmode' in request.form and request.form.get('netmode') == 'true'
    }
    return jsonify(response_data)
    


#home
@app.route("/", methods=['GET'])
def index():
    if app.config['REQUIRE_AUTH']:
        if not session.get('authenticated'):
            return redirect(url_for('login'))
        

    files = file_handler.get_file_list()
    return render_template("index.html", file_list=files)