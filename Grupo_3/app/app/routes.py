from flask import render_template
from flask_session import Session
from app import app
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import sys

matplotlib.use('Agg') # Non interactive backend mode

sys.stdin.reconfigure(encoding='utf-8')
sys.stdout.reconfigure(encoding='utf-8')

app.config['SESSION_TYPE'] = 'filesystem'
Session(app)


# INDEX

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html',title='Home')
 
@app.route('/datamining')
def datamining():
    return render_template('datamining.html', title="DataMining")