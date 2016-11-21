import numpy as np
import pandas as pd
import datetime
from stats import form_data, match_stats, model_libs, form_model, predict_matches

ignore_cols = ['match_id', 'team_id', 'team_name', 'opp_id', 'opp_name', 'scheduled', 'games_played', 'round', 'current_formation']
all_models = ['gnb', 'randomForest', 'log'] # 'knn' - not working on no_ties for some reason #svc just isn't predicting correctly
leagues = model_libs.get_leagues_country_codes() # = { "epl": 'ENG' }
teams = form_data.get_teams()
league_rounds = model_libs.get_leagues_rounds(leagues)

targets = ["points", "converted_goals", "no_ties"]  # "points", "converted_goals",
dt = datetime.date.today().strftime("%m_%d_%y")
dt = '11_15_16' # This will be every previous Tuesday for Soccer unless they didn't have league games last week
data_csv = 'csv/' + str(dt) + '/raw_data.csv'

testing = False # True if you need to formulate all of the csv's
if testing:
    raw_data = form_data.run_data()
    raw_data.to_csv(data_csv)
else:
    raw_data = pd.read_csv(data_csv)
    raw_data = raw_data.drop(raw_data.columns[[0]], axis=1)

print('Data Loaded...')
print("Dataset size :: {}".format(raw_data.shape))

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

""" See if there are any 'inf' or 'nulls' in the data """
inds = pd.isnull(ranked_data).any(1).nonzero()[0]
print(inds)

""" Formatting data to convert goals scored to the correct category"""
formatted_data = ranked_data.copy()

formatted_data['converted_goals'] = formatted_data.apply(lambda row: model_libs.set_group(row['goals']), axis=1)

adjusted_data = model_libs.adjust_features(formatted_data)

columns_to_drop = ['current_record', 'opp_record', 'goals_for', 'opp_goals_for', 'goals_against', 'opp_goals_against',
                   'rpi']

_, stats_columns = form_data.get_columns()

adjusted_data = adjusted_data.drop(ignore_cols + columns_to_drop + stats_columns + ["goals"], 1)

if testing:
    ''' Start Modeling Targets'''
    for target in targets:
        print(' ================================= ')
        print("Target :: {}".format(target))
        target_data = adjusted_data.copy()
        if target == 'converted_goals':
            target_data = target_data.drop("points", 1)
            (target_y, target_X) = model_libs._extract_target(target_data, 'converted_goals')
        elif target == "points":
            target_data = target_data.drop("converted_goals", 1)
            (target_y, target_X) = model_libs._extract_target(target_data, 'points')
        elif target == "no_ties":
            target_data = target_data.drop("converted_goals", 1)
            train_data = target_data[target_data['points'] != 1]
            (target_y, target_X) = model_libs._extract_target(train_data, 'points')

        for m in all_models:
            r = form_model.build_tuned_model(target_X, target_y, m, dt, target)
            # print(r)
            # print('Accuracy :: ')
            # model_libs.check_accuracy(r, target_X, target_y)

prediction_models = {}

for t in targets:
    prediction_models[t] = form_model.load_models(all_models, dt, t)


print('Upcoming matches')
upcoming_matches, match_details = predict_matches.get_upcoming_matches()
upcoming_matches.to_csv('csv/' + str(dt) + '/upcoming_matches.csv')
upcoming_data = predict_matches.predictions(upcoming_matches)

upcoming_ranked_data_csv = 'csv/' + str(dt) + '/upcoming_ranked_data.csv'

adjusted_leagues = {"epl": 'ENG', "bundesliga": 'DEU', "primera_division": 'ESP', "ligue_1": 'FRA'}
adjusted_league_rounds = model_libs.get_leagues_rounds(adjusted_leagues)
testing = True
if testing:
    upcoming_ranked_data = form_data.get_rankings(adjusted_leagues, teams, adjusted_league_rounds, upcoming_data, True)
    upcoming_ranked_data.to_csv(upcoming_ranked_data_csv)
else:
    upcoming_ranked_data = pd.read_csv(upcoming_ranked_data_csv)
    upcoming_ranked_data = upcoming_ranked_data.drop(upcoming_ranked_data.columns[[0]], axis=1)

print('Loaded Upcoming Data...')

""" Formatting data to convert goals scored to the correct category"""
upcoming_formatted_data = upcoming_ranked_data.copy()

adjusted_upcoming_data = model_libs.adjust_features(upcoming_formatted_data)

columns_to_drop = ['current_record', 'opp_record', 'goals_for', 'opp_goals_for', 'goals_against', 'opp_goals_against', 'rpi']

adjusted_upcoming_data = adjusted_upcoming_data.drop(ignore_cols + columns_to_drop + stats_columns + ['points', 'goals'], 1)

# This are all the X values
adjusted_upcoming_data
inds = pd.isnull(adjusted_upcoming_data).any(1).nonzero()[0]
print(inds)

""" Find predictions """
all_preds = {}
for t in targets:
    for index, m in enumerate(all_models):
        print(str(m) + '_' + str(t) + '_preds')
        preds = str(m) + '_' + str(t) + '_preds'
        all_preds[preds] = prediction_models[t][index].predict(adjusted_upcoming_data)
        print(all_preds[preds])
        if t == 'points' and m == 'log':
            probs = pd.DataFrame(prediction_models[t][index].predict_proba(adjusted_upcoming_data))
            probs = probs.rename(columns={0: 'Probability 0', 1: 'Probability 1', 2: 'Probability 2'})

columns = ['team_name', 'opp_name', 'scheduled', 'is_home']
# Remove all columns except the ones above
upcoming_matches = upcoming_data[columns]

# Add predictions to the end of that DF
results = pd.DataFrame.from_dict(all_preds)
upcoming_matches = pd.concat([upcoming_matches, results, probs], axis=1)
reordered_matches = pd.DataFrame([])

for rows in upcoming_matches.iterrows():
    for i in upcoming_matches['team_name']:
        if rows[1]['opp_name'] == i:
            reordered_matches = reordered_matches.append(rows[1])
            reordered_matches = reordered_matches.append(upcoming_matches[upcoming_matches['team_name'].isin([i])])

reordered_matches = reordered_matches.drop_duplicates()

""" To compare when we have actual results"""
#actual_results = pd.read_csv('actual_results.csv')
#actual_results = actual_results.rename(columns = {'Unnamed: 0':'idx'})
#indexed_results = actual_results.set_index('idx')
#reordered_matches = pd.concat([reordered_matches, indexed_results], axis=1)

reordered_matches = reordered_matches.reset_index(drop=True)
predictions_csv = 'csv/' + str(dt) + '/all_predictions.csv'
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


