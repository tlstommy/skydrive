from flask import Flask, render_template
import os,random,time,signal


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
    dataDict = {'name':file,'size':stat.st_size,'last_modified':stat.st_mtime}
    file_list.append(dataDict)



@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html", file_list=file_list)

if __name__ == '__main__':
    app.run(debug=True)
