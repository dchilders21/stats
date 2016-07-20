import mysql.connector
import datetime
import pandas as pd
import match_stats
import model_libs
from sklearn import grid_search
from sklearn.tree import DecisionTreeRegressor
from sklearn.metrics import make_scorer, mean_absolute_error, mean_squared_error
from sklearn.cross_validation import train_test_split

cnx = mysql.connector.connect(user='root', password='',
                              host='127.0.0.1',
                              database='mls')
cursor = cnx.cursor(dictionary=True, buffered=True)

match_details = pd.read_sql('SELECT * FROM home_away_coverage', cnx)
query = "SELECT id FROM teams LIMIT 1"
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
for team in cursor:

    for i in range(2, week):

        print("WEEK {} :: TEAM ID {}".format(i, team["id"]))
        adjusted_time = (schedule_2016[i] + datetime.timedelta(hours=7))

        prev_week = (schedule_2016[i - 1] + datetime.timedelta(hours=7))

        cur_matches = match_details.loc[
            ((match_details['home_id'] == team["id"]) | (match_details['away_id'] == team["id"])) &
            ((match_details['scheduled'] < adjusted_time) & (match_details['scheduled'] > prev_week))]

        prev_matches = match_details.loc[
            ((match_details['home_id'] == team["id"]) | (match_details['away_id'] == team["id"])) &
            (match_details['scheduled'] < prev_week)]

        if not cur_matches.empty:
            for i, cur_match in cur_matches.iterrows():
                """ Better Solution for this?  Basically pulling out a Series but the create_match function is expecting a DF
                # have to convert it back to a DF in order to not pull the same entry if there are multiple games in the week """
                temp = pd.DataFrame([])
                df = temp.append(cur_match, ignore_index=True)
                match_result = match_stats.create_match(team["id"], df, prev_matches)

                if match_result is not None:
                    training_list.append(match_result)

columns = ['match_id', 'team_id', 'team_name', 'opp_id', 'opp_name', 'scheduled',
           # Non-Feature Columns
           'is_home', 'avg_points', 'avg_goals', 'margin', 'goal_diff',
           'win_percentage',
           'sos', 'opp_is_home', 'opp_avg_points', 'opp_avg_goals', 'opp_margin',
           'opp_goal_diff', 'opp_win_percentage',
           'points']  # Target Columns - #'goals', 'opp_goals'

training_data = pd.DataFrame(training_list, columns=columns)

target_col = 'points'
ignore_cols = ['match_id', 'team_id', 'team_name', 'opp_id', 'opp_name', 'scheduled']

td = model_libs._clone_and_drop(training_data, ignore_cols)
(y, X) = model_libs._extract_target(td, target_col)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=0)



""""(train, test) = model_libs.split(td)
(y_train, x_train) = model_libs._extract_target(test, target_col)
(y_test, x_test) = model_libs._extract_target(test, target_col)"""
# y_train = y_train.apply(standardizer)

# model = build_model_logistic(y_train, x_train, alpha=8.0)
# results = predict_model(model, test, ignore_cols, target_col)

regressor = DecisionTreeRegressor()
parameters = {'max_depth': (1, 2, 3, 4, 5, 6, 7, 8, 9, 10)}

regressor.fit(X_train, y_train)

reg = grid_search.GridSearchCV(regressor, parameters, scoring=make_scorer(mean_squared_error, greater_is_better=False))

reg.fit(X_train, y_train)

print(reg.predict(X_test))

print(y_test)