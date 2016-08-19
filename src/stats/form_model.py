import datetime

from stats import match_stats
import mysql.connector
import pandas as pd
from pandas.tools.plotting import scatter_matrix
import numpy as np
from sklearn import grid_search
from sklearn.cross_validation import train_test_split
from sklearn import cross_validation
from sklearn.metrics import make_scorer, mean_squared_error
from sklearn.tree import DecisionTreeRegressor
from sklearn.svm import SVC
from sklearn.metrics import f1_score
from sklearn.decomposition import PCA
import matplotlib

from stats import model_libs

import sys
print(sys.path)

cnx = mysql.connector.connect(user='root', password='',
                              host='127.0.0.1',
                              database='mls')
cursor = cnx.cursor(dictionary=True, buffered=True)

match_details = pd.read_sql('SELECT * FROM home_away_coverage_2', cnx)
query = "SELECT id FROM teams"
cursor.execute(query)


round_number = 24
features = {}

upcoming_matches = pd.read_sql("SELECT matches.id as 'match_id', matches.scheduled, matches.home_id, matches.away_id, teams1.full_name AS 'home_team', teams2.full_name AS 'away_team' FROM matches LEFT JOIN teams teams1 ON matches.home_id = teams1.id LEFT JOIN teams teams2 ON matches.away_id = teams2.id WHERE status = 'scheduled'", cnx)
previous_matches = pd.read_sql("SELECT * FROM matches WHERE status = 'closed'", cnx)

training_list = []
for team in cursor:

    for i in range(2, round_number):

        print("ROUND {} :: TEAM ID {}".format(i, team["id"]))

        cur_matches = match_details.loc[
            ((match_details['home_id'] == team["id"]) | (match_details['away_id'] == team["id"])) &
            (match_details['round'] == i)]

        if not cur_matches.empty:
            for c, cur_match in cur_matches.iterrows():
                """ Better Solution for this?  Basically pulling out a Series but the create_match function is expecting a DF
                # have to convert it back to a DF in order to not pull the same entry if there are multiple games in the week """
                temp = pd.DataFrame([])
                df = temp.append(cur_match, ignore_index=True)
                match_result = match_stats.create_match(team["id"], df, match_details, i, False, True)

                if match_result is not None:
                    training_list.append(match_result)

columns = ['match_id', 'team_id', 'team_name', 'opp_id', 'opp_name', 'scheduled', 'games_played',
           # Non-Feature Columns
           'is_home', 'avg_points', 'goals_for', 'goals_against', 'avg_goals', 'margin', 'goal_diff',
           'win_percentage', 'sos', 'opp_is_home', 'opp_avg_points', 'opp_avg_goals', 'opp_margin',
           'opp_goal_diff', 'opp_win_percentage', 'opp_opp_record',
           # Extended Feature Columns
           'home_possession', 'away_possession', 'home_attacks', 'away_attacks', 'home_fouls', 'away_fouls',
           'home_yellow_card', 'away_yellow_card', 'home_corner_kicks', 'away_corner_kicks',
           'home_shots_on_target', 'away_shots_on_target', 'home_ball_safe', 'away_ball_safe',
           'home_shots_total', 'away_shots_total',
           'points']  # Target Columns - #'goals', 'opp_goals'

training_data = pd.DataFrame(training_list, columns=columns)

target_col = 'points'
ignore_cols = ['match_id', 'team_id', 'team_name', 'opp_id', 'opp_name', 'scheduled']


#This takes forever
#pd.scatter_matrix(X, alpha=0.3, figsize = (14,8), diagonal = 'kde');

td = model_libs._clone_and_drop(training_data, ignore_cols)

print("Describing the Data")
#print(td.describe)
# pd.set_option('display.max_columns', None)
# pd.set_option('display.max_rows', len(td))
# print(td)

#pd.scatter_matrix(td, alpha=0.3, diagonal='kde')
(y, X) = model_libs._extract_target(td, target_col)

#pca = PCA(n_components=30)
#pca.fit(X)
#print(pca)

#X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)

# Regression Model
"""regressor = DecisionTreeRegressor()
parameters = {'max_depth': (1, 2, 3, 4, 5, 6, 7, 8, 9, 10)}
regressor.fit(X_train, y_train)
reg = grid_search.GridSearchCV(regressor, parameters, scoring=make_scorer(mean_squared_error, greater_is_better=False))
reg.fit(X_train, y_train)"""

# SVM Model
#pm = SVC()
#predictor_model = pm.fit(X_train, y_train)

parameters = {'kernel': ('linear', 'rbf'), 'C': [1, 10]}
# parameters = [{'kernel': ['rbf'], 'gamma': [1e-3, 1e-4], 'C': [1, 10, 100, 1000]}, {'kernel': ['linear'], 'C': [1, 10, 100, 1000]}]

svr = SVC()
clf = grid_search.GridSearchCV(svr, parameters)


def train_classifier(clf, X_train, y_train):
    clf.fit(X_train, y_train)


def predict_labels(clf, features, target):
    y_pred = clf.predict(features)
    print(' ~~~~~~~~~~~~~~~~~~~~~~~ ')
    print(y_pred)
    print(target.values)
    print(' ~~~~~~~~~~~~~~~~~~~~~~~ ')
    return f1_score(target.values, y_pred, average="macro")


def train_predict(clf, X_train, y_train, X_test, y_test):
    train_classifier(clf, X_train, y_train)
    train_f1_score = predict_labels(clf, X_train, y_train)
    test_f1_score = predict_labels(clf, X_test, y_test)

    return train_f1_score, test_f1_score


# Need to iterate over a different PERCENTAGE of the data and make sure the train data isn't the same rows
# Also need to try different methods


# X_train, X_test, y_train, y_test = cross_validation.train_test_split(X, y, test_size=0.2, random_state=42)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
train_f1_score, test_f1_score = train_predict(clf, X_train, y_train, X_test, y_test)
print("F1 score for training set: {}".format(train_f1_score))
print("F1 score for test set: {}".format(test_f1_score))
# scores = cross_validation.cross_val_score(clf, X_train, y_train, cv=5)


def get_model():
    return predictor_model

# print(reg.predict(X_test))
# print(y_test)

upcoming_list = []
count = 0
query = "SELECT id FROM teams"
cursor.execute(query)
for team in cursor:
    upcoming_team_matches = upcoming_matches.loc[
                ((upcoming_matches['home_id'] == team["id"]) | (upcoming_matches['away_id'] == team["id"]))]

    print('Upcoming Team Matches')
    print(upcoming_team_matches)

    if not upcoming_team_matches.empty:
        for i, upcoming_team_match in upcoming_team_matches.iterrows():
            temp = pd.DataFrame([])
            df = temp.append(upcoming_team_match, ignore_index=True)
            upcoming_stats = match_stats.create_match(team["id"], df, match_details, round_number, True, False)

            if upcoming_stats is not None:
                upcoming_list.append(upcoming_stats)


upcoming_data = pd.DataFrame(upcoming_list, columns=columns)

ud = model_libs._clone_and_drop(upcoming_data, ignore_cols)
print(ud)
(ud_y, ud_X) = model_libs._extract_target(ud, target_col)

print(predictor_model.predict(ud_X))
