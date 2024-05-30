from flask import render_template, request, jsonify
from flask_session import Session
from app import app
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import sys

from DataExtraction import *
from DataCleaning import *
from visualisation import *

matplotlib.use('Agg') # Non interactive backend mode

sys.stdin.reconfigure(encoding='utf-8')
sys.stdout.reconfigure(encoding='utf-8')

app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html',title='Home')
 
@app.route('/datamining')
def datamining():
    return render_template('datamining.html', title="DataMining")

@app.route("/data_cleaning", methods=['GET', 'POST'])
def datacleaning():
    global date
    global downloaded_files
    date = None
    # Was the form filled or skiped ?
    filled_form = request.form.get('filled_form', 'False') == 'True'
    if filled_form:
        # Retrieve form information
        date = request.form.get('month-year')
        n = request.form.get('number')
        # Compute datamining
        downloaded_files = data_extraction(m1=int(date[5:]), y1=int(date[:4]), n=int(n))
        return render_template("data_cleaning.html", title="DataCleaning", date=date, n=n)
    return render_template("data_cleaning.html", title="DataCleaning")

@app.route("/visualisation_board", methods=["GET", "POST"])
def visualisation_board():
    are_data_clean = False
    # Compute data_cleaning if files have just been downloaded
    if date is not None:
        for file_zip in downloaded_files:
            folder_path = f"extracted/{file_zip[5:-4]}"
            for file in os.listdir(folder_path):
                file_path = os.path.join(folder_path, file)
                if os.path.isfile(file_path):
                    cargar_y_procesar_archivo(file_path)
        are_data_clean = True
    return render_template("visualisation_board.html", title="Visualisation Board", are_data_clean=are_data_clean)

@app.route("/aggregated_curves_form")
def aggregated_curves_form():
    return render_template("aggregated_curves_form.html", title="Aggregated Curves")

@app.route('/check-file', methods=['POST'])
def check_file():
    day = request.json.get('date').replace("-", "")
    number = request.json.get("number")
    file_path = f"extracted/curva_pibc_uof_{day[:-2]}/curva_pibc_uof_{day}0{number}.csv"
    print(file_path)
    file_exists = os.path.isfile(file_path)
    return jsonify({"exists": file_exists})

@app.route("/aggregated_curves", methods=['GET', 'POST'])
def aggregated_curves():
    # Retrieve form data
    day = request.form.get("date").replace("-", "")
    number = request.form.get("number")
    hour = int(request.form.get('hour'))
    file_path = f"extracted/curva_pibc_uof_{day[:-2]}/curva_pibc_uof_{day}0{number}.csv"
    aggregated_curve(file_path, hour, day, number)
    quantity(file_path, day, number)
    price(file_path, day, number)
    return render_template("aggregated_curves.html", title="Aggregated Curves")