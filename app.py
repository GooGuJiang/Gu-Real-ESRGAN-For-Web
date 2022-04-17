# -*- coding: utf-8 -*-
import os

from flask import Flask, render_template, request,jsonify,send_file
import hashlib
from PIL import Image
import base64
import subprocess
from threading import Thread
import platform


app = Flask(__name__)
app.config['UPLOADED_PATH'] = os.path.join(app.root_path, 'upload')

def UsePlatform():
  sysstr = platform.system()
  if(sysstr =="Windows"):
    return "win"
  elif(sysstr == "Linux"):
    return "linux"
  else:
    return "unknow"

def getdile(name):
    outt = name.rfind(".")
    name = name[outt:len(name)]
    return name

def getname(intext):
    return intext[:len(intext)-len(getdile(intext))]

def md5(message_inp):
    message = str(message_inp)
    m = hashlib.md5()
    m.update(message.encode('utf-8'))
    message = m.hexdigest()
    return message


def stmd(inpu_img): #调用图片放大程序
    if UsePlatform() == "win":
        path_cx = os.path.join("file/", "real-win")
        path_img = os.path.join("upload/", inpu_img)
        path_out = os.path.join("out/", str("gubig_")+str(inpu_img))
    else:
        path_cx = os.path.join("file/", "real-linux")
        path_img = os.path.join("./upload/", inpu_img)
        path_out = os.path.join("./out/", str("gubig_")+str(inpu_img))
    command=path_cx+' -i "'+path_img+'" -o "'+path_out+'"'
    print(command)
    p=subprocess.Popen(command, shell=False, stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    file_in = getdile(inpu_img)
    filenlog = inpu_img[:len(inpu_img)-len(file_in)]
    while p.poll() is None:
        line=p.stdout.readline().decode("utf8")
        line=line.replace('\n', '')
        f = open("./tmp/"+filenlog+".txt", "w")
        f.write(line)
        f.close()
        #print(line)
    f = open("./tmp/"+filenlog+".txt", "w")
    f.write("end")
    f.close()

@app.route('/', methods=['GET', 'POST'])
def gumain():
    return render_template('index.html')


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    #try:
        thread_list =[]
        if request.method == 'POST':
            for f in request.files.getlist('file'):
                fil_name = str(md5(f.stream))+str(getdile(f.filename))
                fil_dir = os.path.join(app.config['UPLOADED_PATH'])
                f.save(os.path.join(app.config['UPLOADED_PATH'], fil_name))
        im = Image.open(fil_dir+"/"+fil_name)
        im = im.resize((50, 50), Image.LANCZOS)
        im.save(fil_dir+"/min/"+fil_name)  # 保存缩略
        up_load_date={
            "img_name":fil_name,
            "code":200
        }
        
        
        teas = Thread(target=stmd, args=(fil_name,)) 
        thread_list.append(teas)
        for t in thread_list:
            t.setDaemon(True)
            t.start()

        return jsonify(up_load_date)
    #except:
    #    up_load_date={
    #                "img_name":None,
    #                "code":100
    #            }
    #    return jsonify(up_load_date)

@app.route('/getinfo', methods=['GET'])
def get_min_file():
    fil_dir = "./upload"
    img_name = request.args.get('img_name')
    filename = request.args.get('filename')
    with open("./tmp/"+getname(img_name)+".txt", 'r') as how:
        out_how_do = how.read()
    out_how_do_out = out_how_do[:len(out_how_do)-2]

    if "%" in out_how_do:
            imgload_tex = str(out_how_do_out)+str("%")
            imgload = out_how_do_out
            buut="disabled"
    else:
        if "end" in out_how_do:
            imgload_tex = "完成"
            imgload = "100"
            buut=""

    with open(fil_dir+"/min/"+img_name, 'rb') as f:
        img_min = base64.b64encode(f.read()).decode()
    return render_template('crad.html',card_name=filename,imgdata="data:image/png;base64,"+img_min,imgload=imgload,imgload_text=imgload_tex,buut=buut,dl_url="/download/"+img_name)

@app.route('/download/<filename>')
def download_file (filename):
    folder = "out/"
    # 构造供下载文件的完整路径
    path = os.path.join(folder, "gubig_"+filename)
    try:
        os.remove("./tmp/"+getname(filename)+".txt")
        os.remove("./upload/"+filename)
        os.remove("./upload/min/"+filename)
        return send_file(path, as_attachment=True)
    except:
        return send_file(path, as_attachment=True)
    


@app.route('/get_start', methods=['GET'])
def get_filegugngoo():
    img_name = request.args.get('img_name')
    with open("./tmp/"+getname(img_name)+".txt", 'r') as how:
        out_how_do = how.read()

    if "%" in out_how_do:
            data_json ={
                "img_st":"no"
            }
            return jsonify(data_json)
    else:
        if "end" in out_how_do:
            data_json ={
                "img_st":"ok"
            }
            return jsonify(data_json)



if __name__ == '__main__':
    app.run(host="0.0.0.0",port=16678)
