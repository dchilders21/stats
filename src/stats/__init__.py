import datetime
import os
from collections import namedtuple

import mysql.connector
import pandas as pd
from flask import Flask
from flask import render_template
from sklearn.metrics import f1_score

from stats import form_model
from stats import match_stats
from stats import model_libs

app = Flask(__name__)

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

STATIC_PATH = static_folder_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")

cnx = mysql.connector.connect(user='root', password='',
                              host='127.0.0.1',
                              database='mls')
cursor = cnx.cursor(dictionary=True, buffered=True)

match_details = pd.read_sql('SELECT * FROM home_away_coverage', cnx)
query = "SELECT id FROM teams"
teams = pd.read_sql("SELECT id, full_name FROM teams", cnx)
cursor.execute(query)

# MLS broken out WEEKLY even though teams don't always play a game the same week
# Off of the schedule from Google
schedule_2016 = {
    1: datetime.datetime(2016, 3, 6, 23),
    2: datetime.datetime(2016, 3, 13, 23),
    3: datetime.datetime(2016, 3, 20, 23),
    4: datetime.datetime(2016, 4, 3, 23),
    5: datetime.datetime(2016, 4, 10, 23),
    6: datetime.datetime(2016, 4, 17, 23),
    7: datetime.datetime(2016, 4, 24, 23),
    8: datetime.datetime(2016, 5, 1, 23),
    9: datetime.datetime(2016, 5, 8, 23),
    10: datetime.datetime(2016, 5, 15, 23),
    11: datetime.datetime(2016, 5, 22, 23),
    12: datetime.datetime(2016, 5, 29, 23),
    13: datetime.datetime(2016, 6, 2, 23),
    14: datetime.datetime(2016, 6, 19, 23),
    15: datetime.datetime(2016, 6, 26, 23),
    16: datetime.datetime(2016, 7, 3, 23),
    17: datetime.datetime(2016, 7, 6, 23),
    18: datetime.datetime(2016, 7, 10, 23),
    19: datetime.datetime(2016, 7, 13, 23),
    20: datetime.datetime(2016, 7, 17, 23),
    21: datetime.datetime(2016, 7, 24, 23),
}

week = 21
adjusted_time = (schedule_2016[week] + datetime.timedelta(hours=7))
prev_week = (schedule_2016[week - 1] + datetime.timedelta(hours=7))
features = {}

upcoming_matches = pd.read_sql("SELECT matches.id as 'match_id', matches.scheduled, matches.home_id, matches.away_id, teams1.full_name AS 'home_team', teams2.full_name AS 'away_team' FROM matches LEFT JOIN teams teams1 ON matches.home_id = teams1.id LEFT JOIN teams teams2 ON matches.away_id = teams2.id WHERE status = 'scheduled'", cnx)
previous_matches = pd.read_sql("SELECT * FROM matches WHERE status = 'closed'", cnx)

target_col = 'points'
ignore_cols = ['match_id', 'team_id', 'team_name', 'opp_id', 'opp_name', 'scheduled']


def train_classifier(clf, X_train, y_train):
    clf.fit(X_train, y_train)


def predict_labels(clf, features, target):
    y_pred = clf.predict(features)
    return f1_score(target.values, y_pred, average=None, pos_label=1), y_pred


def train_predict(clf, X_train, y_train, X_test, y_test):
    train_classifier(clf, X_train, y_train)
    train_f1_score = predict_labels(clf, X_train, y_train)
    print(train_f1_score)
    f1_training[0] += train_f1_score[0]
    print("F1 score for training set: {}".format(train_f1_score))

    test_f1_score, yPred = predict_labels(clf, X_test, y_test)
    f1_test[0] += test_f1_score[0]
    print("F1 score for test set: {}".format(test_f1_score))

columns = ['match_id', 'team_id', 'team_name', 'opp_id', 'opp_name', 'scheduled',
           # Non-Feature Columns
           'is_home', 'avg_points', 'avg_goals', 'margin', 'goal_diff',
           'win_percentage',
           'sos', 'opp_is_home', 'opp_avg_points', 'opp_avg_goals', 'opp_margin',
           'opp_goal_diff', 'opp_win_percentage',
           'points']  # Target Columns - #'goals', 'opp_goals'


def iternamedtuples(df):
    Row = namedtuple('Row', df.columns)
    for row in df.itertuples():
        yield Row(*row[1:])

list_of_teams = list(iternamedtuples(teams))


@app.route('/')
def init():
    return render_template("index.html", teams=list_of_teams)


@app.route('/<int:id>')
def matches(id):
    prev_matches = match_details.loc[
        ((match_details['home_id'] == id) | (match_details['away_id'] == id)) &
        (match_details['scheduled'] < prev_week)]

    # Reverses the DF
    prev_matches = prev_matches.iloc[::-1]
    prev_matches = prev_matches.sort_index(ascending=True, axis=0)
    prev_matches = prev_matches.reindex(index=prev_matches.index[::-1])
    prev_matches.head()

    previous_list = list(iternamedtuples(prev_matches))

    upcoming_team_matches = upcoming_matches.loc[
        ((upcoming_matches['home_id'] == id) | (upcoming_matches['away_id'] == id))]

    upcoming_list = []
    current_list = []

    if not upcoming_team_matches.empty:
        for i, upcoming_team_match in upcoming_team_matches.iterrows():
            prev_matches = match_details.loc[
                ((match_details['home_id'] == id) | (match_details['away_id'] == id)) &
                (match_details['scheduled'] < prev_week)]
            temp = pd.DataFrame([])
            df = temp.append(upcoming_team_match, ignore_index=True)

            upcoming_stats = match_stats.create_match(id, df, prev_matches, True, False)

            if upcoming_stats is not None:
                upcoming_list.append(upcoming_stats)
                current_list.append(upcoming_team_match)


            reg_model = form_model.get_model()

            upcoming_data = pd.DataFrame(upcoming_list, columns=columns)

            ud = model_libs._clone_and_drop(upcoming_data, ignore_cols)
            (ud_y, ud_X) = model_libs._extract_target(ud, target_col)
            print(ud)
            print(reg_model.predict(ud_X))

    return render_template("index.html", teams=list_of_teams, previous_list=previous_list, current_list=current_list)

# if __name__ == "__main__":
    # app.run()