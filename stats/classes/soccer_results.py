import pandas as pd
import os
from datetime import datetime, timedelta
from stats import form_data, match_stats, model_libs, form_model, predict_matches
from stats.classes.results import FormulatePredictions


class SoccerPredictions(FormulatePredictions, object):

    def __init__(self, **kwrargs):
        super().__init__(**kwrargs)
        self.testing = kwrargs.get('testing') or False
        self.__get_data = kwrargs.get('get_data')
        self.__read_data = kwrargs.get('read_data')
        self.data_csv = kwrargs.get('data_csv')
        self.ranked_data_csv = kwrargs.get('ranked_data_csv')
        self.ranked_upcoming_matches_csv = kwrargs.get('ranked_upcoming_matches_csv')
        self.predictions_csv = kwrargs.get('predictions_csv')

        self.to_drop = ignore_cols + columns_to_drop + stats_columns
        self.__convert_goal = kwrargs.get('convert_goal')
        self.__adjust_features = kwrargs.get('adjust_features')
        self.targets = kwrargs.get('targets')
        self.__extract_target = kwrargs.get('extract_target')
        self.all_models = kwrargs.get('all_models')
        self.__predictions = kwrargs.get('predictions')
        self.adjusted_leagues = kwrargs.get('adjusted_leagues')

        self.__get_rounds = kwrargs.get('rounds')
        self.__data_frame = kwrargs.get('data_frame')
        self.__get_leagues = kwrargs.get('leagues')
        self.leagues = self.__get_leagues()
        self.__get_teams = kwrargs.get('teams')
        self.teams = self.__get_teams()
        self.rounds = self.__get_rounds(self.leagues)

    def run(self):
        """ Pull in data and assign rankings """
        self.init_raw_data()
        self.init_ranked_data()

        """ Formatting data to convert goals scored to the correct category"""
        self.formatted_data = self.ranked_data.copy()
        self.formatted_data['converted_goals'] = self.formatted_data.apply(self.__convert_goal, axis=1)

        """ Squares the difference between a team's feature and the opponents feature
            e.g. (goals_for - opp_goals_for)^2 """
        adjusted_data = self.__adjust_features(self.formatted_data)
        self.adjusted_data = adjusted_data.drop(self.to_drop + ["goals"], 1)

        #######################

        ''' Start Modeling Targets '''
        for target in self.targets:
            print(' ================================= ')
            print("Target :: {}".format(target))
            method = getattr(self, "target__%s" % target)
            (target_y, target_X) = method()

            self.modeling(target_X, target_y, target)

        self.prediction()

        #######################

        print('Upcoming matches')

        """ Print a CSV for the previous weeks results """
        self.predictions_compare()

        self.adjusted_league_rounds = self.__get_rounds(self.adjusted_leagues)

        self.init_upcoming_matches_data()
        self.init_ranked_upcoming_matches_data()

        """ Formatting data to convert goals scored to the correct category"""
        self.upcoming_formatted_data = self.upcoming_ranked_data.copy()
        self.adjusted_upcoming_data = self.__adjust_features(self.upcoming_formatted_data)
        self.adjusted_upcoming_data = self.adjusted_upcoming_data.drop(self.to_drop + ['points', 'goals'], 1)

        self.find_predictions()
        self.predictions_reorder()
        self.predictions_save()

    def target__converted_goals(self):
        target_data = self.adjusted_data.copy()
        target_data = target_data.drop("points", 1)
        return self.__extract_target(target_data, 'converted_goals')

    def target__points(self):
        target_data = self.adjusted_data.copy()
        target_data = target_data.drop("converted_goals", 1)
        return self.__extract_target(target_data, 'points')

    def target__no_ties(self):
        target_data = self.adjusted_data.copy()
        target_data = target_data.drop("converted_goals", 1)
        train_data = target_data[target_data['points'] != 1]
        return self.__extract_target(train_data, 'points')


_, stats_columns = form_data.get_columns()
ignore_cols = ['match_id', 'team_id', 'team_name', 'opp_id', 'opp_name', 'scheduled', 'games_played', 'round', 'current_formation']
columns_to_drop = ['current_record', 'opp_record', 'goals_for', 'opp_goals_for', 'goals_against', 'opp_goals_against', 'rpi']

upcoming_matches, match_details = predict_matches.get_upcoming_matches()

""" this is designed to run once a week to pull in all leagues """
today = "11_22_16"

today_date = datetime.strptime(today, '%m_%d_%y')

prev_week = (today_date - timedelta(days=7)).strftime('%m_%d_%y')

# Leagues skip a week at times so will not always be the previous week
while not os.path.isdir("../csv/soccer/" + prev_week):
    prev_week = (datetime.strptime(prev_week, '%m_%d_%y') - timedelta(days=7)).strftime('%m_%d_%y')


# Creating this weeks folder
if not os.path.isdir('../csv/soccer/' + today + '/'):
    print('Making New Directory for the CSV')
    os.makedirs('../csv/soccer/' + today + '/')

soccer_params = dict(
    testing=True,
    td=today_date,
    prev_week=prev_week,
    get_data=form_data.run_data,
    read_data=pd.read_csv,
    data_csv='../csv/soccer/{}/raw_data.csv'.format(today),
    ranked_data_csv='../csv/soccer/{}/ranked_data.csv'.format(today),
    upcoming_matches_csv='../csv/soccer/{}/upcoming_matches.csv'.format(today),
    ranked_upcoming_matches_csv='../csv/soccer/{}/upcoming_ranked_data.csv'.format(today),
    predictions_csv='../csv/soccer/{}/all_predictions.csv'.format(today),
    leagues=model_libs.get_leagues_country_codes,
    rounds=model_libs.get_leagues_rounds,
    teams=form_data.get_teams,
    convert_goal=lambda row: model_libs.set_group(row['goals']),
    adjust_features=model_libs.adjust_features,
    targets=["points", "converted_goals", "no_ties"],
    extract_target=model_libs._extract_target,
    build_tuned_model=form_model.build_tuned_model,
    all_models=['gnb', 'randomForest', 'log'], #knn
    load_models=form_model.load_models,
    predictions=predict_matches.predictions,
    adjusted_leagues={"epl": 'ENG', "bundesliga": 'DEU', "primera_division": 'ESP', "ligue_1": 'FRA'},
    upcoming_matches=upcoming_matches,
    data_frame=pd.DataFrame,
    concat_data=pd.concat,
    get_rankings=form_data.get_rankings
)

b = SoccerPredictions(**soccer_params)
b.run()
