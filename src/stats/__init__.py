import os
import sys
import pandas as pd
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
    power_rankings = pd.DataFrame()

    if league == 'mls':
        teams = pd.read_sql("SELECT id, full_name FROM teams WHERE id < 41", cnx)

    for i, team in teams.iterrows():

        cur_match = match_details.loc[
            ((match_details['home_id'] == team["id"]) | (match_details['away_id'] == team["id"])) &
            (match_details['round'] == round)]

        if not cur_match.empty:
            df = pd.DataFrame([]).append(cur_match, ignore_index=True)

            features, _ = match_stats.create_match(team["id"], df, match_details, round, True, False)
            s = pd.Series([team["id"], features["team_name"], features['sos']])
            power_rankings = power_rankings.append(s, ignore_index=True)
            power_rankings = power_rankings.sort_values(1, ascending=False)

    for i, power in power_rankings.iterrows():
        power_list.append(power)

    return render_template("rankings.html", rankings=power_list)


# Step 1 Get Data
# Step 2 Calculate Model
# Step 3 Predict upcoming matches
