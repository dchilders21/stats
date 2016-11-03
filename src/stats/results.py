import numpy as np
import pandas as pd
import datetime
from stats import form_data, match_stats, model_libs, form_model, predict_matches
from sklearn.metrics import f1_score

ignore_cols = ['match_id', 'team_id', 'team_name', 'opp_id', 'opp_name', 'scheduled', 'games_played', 'round', 'current_formation']
all_models = ['knn', 'log', 'svc', 'gnb', 'randomForest']
leagues = model_libs.get_leagues_country_codes() # = { "epl": 'ENG' }
teams = form_data.get_teams()
league_rounds = model_libs.get_leagues_rounds()

target = "points"  # 'converted_goals' or 'points'
dt = datetime.date.today().strftime("%m_%d_%y")
data_csv = 'csv/' + str(dt) + '/raw_data.csv'

testing = False
if testing:
    raw_data = form_data.run_data()
    raw_data.to_csv(data_csv)
else:
    raw_data = pd.read_csv(data_csv)
    raw_data = raw_data.drop(raw_data.columns[[0]], axis=1)

print('Data Loaded...')
print("Dataset size :: {}".format(raw_data.shape))

testing = False
ranked_data_csv = 'csv/' + str(dt) + '/ranked_data.csv'
if testing:
    ranked_data = form_data.get_rankings(leagues, teams, league_rounds, raw_data, False)
    ranked_data.to_csv(ranked_data_csv)
else:
    ranked_data = pd.read_csv(ranked_data_csv)
    ranked_data = ranked_data.drop(ranked_data.columns[[0]], axis=1)

print('Ranked Data Loaded...')


def run_features(data, drop_data, target, models):
    new_data = data.drop(drop_data, axis=1)
    # display(new_data.head())
    (y, X) = model_libs._extract_target(new_data, target)
    models = form_model.train_models(dt, X, y, models)
    return models


inds = pd.isnull(ranked_data).any(1).nonzero()[0]
print(inds)

""" Formatting data to convert goals scored to the correct category"""
formatted_data = ranked_data.copy()

if target == "converted_goals":
    # Not using points as a target for this version, using goals
    formatted_data['converted_goals'] = formatted_data.apply(lambda row: model_libs.set_group(row['goals']), axis=1)
    formatted_data = formatted_data.drop(['points', 'goals'], 1)
else:
    formatted_data = formatted_data.drop(['goals'], 1)

    """ This is where you manipulate the features as desired """
""" //////////////////////////////////////////////////////////////////////////////////////////////////// """
""" Using diff_squared methods for features """
""" //////////////////////////////////////////////////////////////////////////////////////////////////// """
formatted_data["diff_goals_for"] = formatted_data.apply(
    lambda row: model_libs.diff_square(row["goals_for"], row["opp_goals_for"]), axis=1)
formatted_data["diff_goals_allowed"] = formatted_data.apply(
    lambda row: model_libs.diff_square(row["goals_against"], row["opp_goals_against"]), axis=1)
formatted_data["diff_attacks"] = formatted_data.apply(
    lambda row: model_libs.diff_square(row["current_team_attacks"], row["opp_team_attacks"]), axis=1)
formatted_data["diff_dangerous_attacks"] = formatted_data.apply(
    lambda row: model_libs.diff_square(row["current_team_dangerous_attacks"], row["opp_team_dangerous_attacks"]),
    axis=1)
formatted_data["diff_goal_attempts"] = formatted_data.apply(
    lambda row: model_libs.diff_square(row["current_team_goal_attempts"], row["opp_team_goal_attempts"]), axis=1)
formatted_data["diff_ball_safe"] = formatted_data.apply(
    lambda row: model_libs.diff_square(row["current_team_ball_safe"], row["opp_team_ball_safe"]), axis=1)
formatted_data["diff_possession"] = formatted_data.apply(
    lambda row: model_libs.diff_square(row["current_team_possession"], row["opp_team_possession"]), axis=1)
# formatted_data["diff_corner_kicks"] = formatted_data.apply(lambda row: model_libs.diff_square(row["current_team_corner_kicks"], row["opp_team_corner_kicks"]), axis=1)
# formatted_data["diff_goal_kicks"] = formatted_data.apply(lambda row: model_libs.diff_square(row["current_team_goal_kicks"], row["opp_team_goal_kicks"]), axis=1)
# formatted_data["diff_saves"] = formatted_data.apply(lambda row: model_libs.diff_square(row["current_team_saves"], row["opp_team_saves"]), axis=1)

columns_to_drop = ['current_record', 'opp_record', 'goals_for', 'opp_goals_for', 'goals_against', 'opp_goals_against',
                   'rpi']

_, stats = form_data.get_columns()

formatted_data = formatted_data.drop(ignore_cols + columns_to_drop + stats, 1)

#### Running ALL Features
if target == "converted_goals":
    models_test_1 = run_features(formatted_data, [], 'converted_goals', ["knn"])
    (formatted_y, formatted_X) = model_libs._extract_target(formatted_data, 'converted_goals')
else:
    models_test_1 = run_features(formatted_data, [], 'points', ["knn"])
    (formatted_y, formatted_X) = model_libs._extract_target(formatted_data, 'points')

print(formatted_X.columns)


# Simple Function to check the accuracy of the models.  Not the Final function
def check_accuracy(model, data_X, y):
    actual_y = pd.DataFrame(y.values, columns=['actual'])
    predictions = pd.concat([pd.DataFrame(model.predict(data_X), columns=['predictions']), actual_y], axis=1)
    predictions['accuracy'] = predictions.apply(lambda r: model_libs.predictions_diff(r['predictions'], r['actual']),
                                                axis=1)
    accuracy = np.divide(predictions['accuracy'].sum(), float(len(predictions['accuracy'])))
    print(accuracy)


for m in models_test_1:
    check_accuracy(m, formatted_X, formatted_y)


model_results = []
for m in all_models:
    r = form_model.build_tuned_model(formatted_X, formatted_y, m, dt)
    model_results.append(r)
    print('Accuracy :: ')
    check_accuracy(r[0], formatted_X, formatted_y)


prediction_models = form_model.load_models(all_models, dt)



print('Upcoming matches')
upcoming_matches, match_details = predict_matches.get_upcoming_matches()
upcoming_matches.to_csv('csv/' + str(dt) + '/upcoming_matches.csv')
upcoming_data = predict_matches.predictions(upcoming_matches)

upcoming_ranked_data_csv = 'csv/' + str(dt) + '/upcoming_ranked_data.csv'

adjusted_leagues = {"epl": 'ENG', "bundesliga": 'DEU', "primera_division": 'ESP', "ligue_1": 'FRA'}
testing = False
if testing:
    upcoming_ranked_data = form_data.get_rankings(adjusted_leagues, teams, league_rounds, upcoming_data, True)
    upcoming_ranked_data.to_csv(upcoming_ranked_data_csv)
else:
    upcoming_ranked_data = pd.read_csv(upcoming_ranked_data_csv)
    upcoming_ranked_data = upcoming_ranked_data.drop(upcoming_ranked_data.columns[[0]], axis=1)

print('Loaded Upcoming Data...')

""" Formatting data to convert goals scored to the correct category"""
upcoming_formatted_data = upcoming_ranked_data.copy()

""" //////////////////////////////////////////////////////////////////////////////////////////////////// """
""" Using diff_squared methods for features """
""" //////////////////////////////////////////////////////////////////////////////////////////////////// """
upcoming_formatted_data["diff_goals_for"] = upcoming_formatted_data.apply(lambda row: model_libs.diff_square(row["goals_for"], row["opp_goals_for"]), axis=1)
upcoming_formatted_data["diff_goals_allowed"] = upcoming_formatted_data.apply(lambda row: model_libs.diff_square(row["goals_against"], row["opp_goals_against"]), axis=1)
upcoming_formatted_data["diff_attacks"] = upcoming_formatted_data.apply(lambda row: model_libs.diff_square(row["current_team_attacks"], row["opp_team_attacks"]), axis=1)
upcoming_formatted_data["diff_dangerous_attacks"] = upcoming_formatted_data.apply(lambda row: model_libs.diff_square(row["current_team_dangerous_attacks"], row["opp_team_dangerous_attacks"]), axis=1)
upcoming_formatted_data["diff_goal_attempts"] = upcoming_formatted_data.apply(lambda row: model_libs.diff_square(row["current_team_goal_attempts"], row["opp_team_goal_attempts"]), axis=1)
upcoming_formatted_data["diff_ball_safe"] = upcoming_formatted_data.apply(lambda row: model_libs.diff_square(row["current_team_ball_safe"], row["opp_team_ball_safe"]), axis=1)
upcoming_formatted_data["diff_possession"] = upcoming_formatted_data.apply(lambda row: model_libs.diff_square(row["current_team_possession"], row["opp_team_possession"]), axis=1)
#upcoming_formatted_data["diff_corner_kicks"] = upcoming_formatted_data.apply(lambda row: model_libs.diff_square(row["current_team_corner_kicks"], row["opp_team_corner_kicks"]), axis=1)
#upcoming_formatted_data["diff_goal_kicks"] = upcoming_formatted_data.apply(lambda row: model_libs.diff_square(row["current_team_goal_kicks"], row["opp_team_goal_kicks"]), axis=1)
#upcoming_formatted_data["diff_saves"] = upcoming_formatted_data.apply(lambda row: model_libs.diff_square(row["current_team_saves"], row["opp_team_saves"]), axis=1)

columns_to_drop = ['current_record', 'opp_record', 'goals_for', 'opp_goals_for', 'goals_against', 'opp_goals_against', 'rpi']
_, stats = form_data.get_columns()

upcoming_formatted_data = upcoming_formatted_data.drop(ignore_cols + columns_to_drop + stats + ['points', 'goals'], 1)

print(upcoming_formatted_data.columns)

""" Models we'll use to predict on upcoming matches """

# This is all the X values
upcoming_formatted_data

rf_preds = prediction_models[4].predict(upcoming_formatted_data)
print(rf_preds)

knn_preds = prediction_models[0].predict(upcoming_formatted_data)
print(knn_preds)

svc_preds = prediction_models[2].predict(upcoming_formatted_data)
print(svc_preds)

log_preds = prediction_models[1].predict(upcoming_formatted_data)
print(log_preds)

log_prob = prediction_models[1].predict_proba(upcoming_formatted_data)
probs = pd.DataFrame(log_prob)
probs = probs.rename(columns={0: 'Probability 0', 1: 'Probability 1', 2: 'Probability 2'})
#display(probs)
#probs.to_csv('probs.csv')

gnb_preds = prediction_models[3].predict(upcoming_formatted_data)
print(gnb_preds)

columns = ['team_name', 'opp_name', 'scheduled', 'is_home']
# Remove all columns except the ones above
upcoming_matches = upcoming_data[columns]

if target == 'converted_goals':
    random_preds = pd.Series(np.random.randint(2, size=len(upcoming_matches.index)), upcoming_matches.index)
else:
    random_preds = pd.Series(np.random.randint(3, size=len(upcoming_matches.index)), upcoming_matches.index)
    random_preds[random_preds == 2] = 3

# Add predictions to the end of that DF
results = pd.DataFrame({'KNN': knn_preds, 'RandomForest': rf_preds, 'SVC': svc_preds, 'GNB': gnb_preds, 'log': log_preds, 'random': random_preds})
upcoming_matches = pd.concat([upcoming_matches, results, probs], axis = 1)
reordered_matches = pd.DataFrame([])

for rows in upcoming_matches.iterrows():
    for i in upcoming_matches['team_name']:
        if rows[1]['opp_name'] == i:
            reordered_matches = reordered_matches.append(rows[1])
            reordered_matches = reordered_matches.append(upcoming_matches[upcoming_matches['team_name'].isin([i])])

reordered_matches = reordered_matches.drop_duplicates()
if target == 'points':
    columns = ['scheduled', 'team_name', 'opp_name', 'is_home', 'KNN', 'RandomForest', 'SVC', 'GNB', 'log', 'random', 'Probability 0', 'Probability 1', 'Probability 2']
else:
    columns = ['scheduled', 'team_name', 'opp_name', 'is_home', 'KNN', 'RandomForest', 'SVC', 'GNB', 'log', 'random', 'Probability 0', 'Probability 1']

reordered_matches = reordered_matches[columns]
""" To compare when we have actual results"""
#actual_results = pd.read_csv('actual_results.csv')
#actual_results = actual_results.rename(columns = {'Unnamed: 0':'idx'})
#indexed_results = actual_results.set_index('idx')
#reordered_matches = pd.concat([reordered_matches, indexed_results], axis=1)

reordered_matches = reordered_matches.reset_index(drop=True)
predictions_csv = 'csv/' + str(dt) + '/predictions_' + target + '.csv'
reordered_matches.to_csv(predictions_csv)


print('Prediction CSV saved')

""" Below is all for POST SCORING """
"""column_model = "GNB"  #'KNN', 'RandomForest', 'SVC', 'GNB', 'log', 'random'

y_pred = reordered_matches[column_model]

if target == 'converted_goals':
    y_true = reordered_matches["actual_converted_goals"]
else:
    y_true = reordered_matches["actual"]


print(f1_score(y_true, y_pred, average='weighted'))
#import seaborn as sns
cnf_matrix = confusion_matrix(y_true, y_pred)
#_ = sns.heatmap(cnf_matrix, annot=True, cmap='YlGnBu')
print(cnf_matrix)"""


