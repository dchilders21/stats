import os
import mysql.connector
import datetime
import pandas as pd
import match_stats
import model_libs
from sklearn import grid_search
from sklearn.tree import DecisionTreeRegressor
from sklearn import svm
from sklearn.metrics import f1_score
from sklearn.metrics import make_scorer, mean_absolute_error, mean_squared_error
from sklearn.cross_validation import train_test_split
from flask import render_template
from flask import redirect, url_for

from flask import Flask
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

week = 20
adjusted_time = (schedule_2016[week] + datetime.timedelta(hours=7))
prev_week = (schedule_2016[week - 1] + datetime.timedelta(hours=7))
features = {}

upcoming_matches = pd.read_sql("SELECT * FROM matches WHERE status = 'scheduled'", cnx)
previous_matches = pd.read_sql("SELECT * FROM matches WHERE status = 'closed'", cnx)

training_list = []

target_col = 'points'
ignore_cols = ['match_id', 'team_id', 'team_name', 'opp_id', 'opp_name', 'scheduled']


"""for index, team in teams.iterrows():

    for i in range(2, week):

        print("WEEK {} :: TEAM ID {}".format(i, team[0]))
        adjusted_time = (schedule_2016[i] + datetime.timedelta(hours=7))

        prev_week = (schedule_2016[i - 1] + datetime.timedelta(hours=7))

        cur_matches = match_details.loc[
            ((match_details['home_id'] == team[0]) | (match_details['away_id'] == team[0])) &
            ((match_details['scheduled'] < adjusted_time) & (match_details['scheduled'] > prev_week))]

        prev_matches = match_details.loc[
            ((match_details['home_id'] == team[0]) | (match_details['away_id'] == team[0])) &
            (match_details['scheduled'] < prev_week)]

        if not cur_matches.empty:
            for i, cur_match in cur_matches.iterrows():
                # Better Solution for this?  Basically pulling out a Series but the create_match function is expecting a DF
                # have to convert it back to a DF in order to not pull the same entry if there are multiple games in the week
                temp = pd.DataFrame([])
                df = temp.append(cur_match, ignore_index=True)
                match_result = match_stats.create_match(team[0], df, prev_matches)

                if match_result is not None:
                    training_list.append(match_result)"""


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


#training_data = pd.DataFrame(training_list, columns=columns)

"""f1_training = [0]
f1_test = [0]
td = model_libs._clone_and_drop(training_data, ignore_cols)
(y, X) = model_libs._extract_target(td, target_col)

clf = svm.SVC()
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=0)
train_predict(clf, X_train, y_train, X_test, y_test)"""

cars = ["Volvo","Ferrari","Audi","BMW","Mercedes","Porche","Saab","Avanti"]


@app.route('/')
def hello_world():
    #redirect(url_for('static', filename='libs/angular.min.js'))
    return render_template("index.html", teams=teams.to_html())

if __name__ == "__main__":
    app.run()