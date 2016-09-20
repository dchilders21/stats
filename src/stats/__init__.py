import os
import sys
import pandas as pd
import numpy as np
import mysql.connector
from flask import render_template

from flask import Flask

from stats import model_libs, match_stats, form_model, form_data

app = Flask(__name__)

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

STATIC_PATH = static_folder_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")

cnx = mysql.connector.connect(user='root', password='',
                              host='127.0.0.1',
                              database='mls')
cursor = cnx.cursor(dictionary=True, buffered=True)

match_details = pd.read_sql('SELECT * FROM home_away_coverage_all', cnx)

print('INITIALIZED...')

@app.route('/rankings/<league>/<int:round>')
def rankings(league, round):
    power_list = []

    if league == 'mls':
        teams = pd.read_sql("SELECT id, full_name FROM teams WHERE id < 41", cnx)

    power_rankings = form_data.get_power_rankings(teams, round)

    for i, power in power_rankings.iterrows():
        power_list.append(power)

    pr = np.array(power_rankings.loc[:, 2])
    qqs = np.percentile(pr, [20, 40, 60, 80])

    return render_template("rankings.html", rankings=power_list)


# Step 1 Get Data
# Step 2 Calculate Model
# Step 3 Predict upcoming matches
