import os
from flask import Flask, render_template, flash, request, redirect, url_for, jsonify
from werkzeug.utils import secure_filename

from detect import run
import math

UPLOAD_FOLDER = 'upload'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.secret_key = 'kunci_rahasia_saya'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET'])
def home():
    return render_template('dashboard.jinja2')

@app.route('/upload', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            return jsonify({"status":"failed"})
        
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return detect(weights='weights/best.pt', source=os.path.join(app.config['UPLOAD_FOLDER'], filename), data= 'Chomp-chomp-detection-2/data.yaml')

# Fungsi untuk menghitung jarak Euclidean antara dua titik
def euclidean_distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    
def detect(weights, source, data):
    result = run(weights=weights, source=source, data=data)
    kirikanan = []
    kanankiri = []
    for res in result:
        x = round(res[0][0], 3) * 1000
        y = round(res[0][1], 3) * 1000
        res[0][0] = x
        res[0][1] = y
        c = res[1]
        selisih = x - y 
        if abs(selisih) < 200:
            kirikanan.append([x,y,c])
            # pasti kiri atas atau kanan bawah
        else:
            kanankiri.append([x,y,c])
            # pasti kanan atas atau kiri bawah
    
    if kanankiri[0][0] < kanankiri[0][1]:
        kanan_atas = kanankiri[1][2]
        kiri_bawah = kanankiri[0][2]
    else:
        kanan_atas = kanankiri[0][2]
        kiri_bawah = kanankiri[1][2]


    if kirikanan[0][0] + kirikanan[0][1] < kirikanan[1][0] + kirikanan[1][1]:

        kiri_atas = kirikanan[0][2]
        kanan_bawah = kirikanan[1][2]
    else:
        kiri_atas = kirikanan[1][2]
        kanan_bawah = kirikanan[0][2]
    
    return check_plano([kiri_atas, kanan_atas, kiri_bawah, kanan_bawah])

    


def check_plano(data_result):
    # - banana 0
    # - duck 1
    # - love 2
    # - watermelon 3

    plano_1 = [1,3,2,0]
    plano_2 = [2,3,0,1]

    if data_result == plano_1:
        return jsonify({"result": "Planogram 1"})
    elif data_result == plano_2:
        return jsonify({"result": "Planogram 2"})
    else:
        return jsonify({"result": "Tidak Ada Planogram"})

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000,)



