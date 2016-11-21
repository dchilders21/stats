import numpy as np
import pandas as pd
import datetime
from abc import abstractmethod
from stats import form_data, match_stats, model_libs, form_model, predict_matches


class FormulatePredictions(object):
    def __init__(self, **kwrargs):
        self.testing = kwrargs.get('testing') or False
        self.__get_data = kwrargs.get('get_data')
        self.__read_data = kwrargs.get('read_data')
        self.data_csv = kwrargs.get('data_csv')
        self.ranked_data_csv = kwrargs.get('ranked_data_csv'),
        self.upcoming_data_csv = kwrargs.get('ranked_data_csv')
        self.targets = kwrargs.get('targets')
        self.dt = '11_15_16'
        self.__build_tuned_model = kwrargs.get('build_tuned_model')
        self.__load_models = kwrargs.get('load_models')

        self.prediction_models = {}
        self.all_preds = {}
        self.upcoming_matches = kwrargs.get('upcoming_matches')
        self.upcoming_matches_csv = kwrargs.get('upcoming_matches_csv')
        self.__predictions = kwrargs.get('predictions')
        self.__data_frame = kwrargs.get('data_frame')
        self.__concat_data = kwrargs.get('concat_data')




    def modeling(self, target_X, target_y, target):
        for each in self.all_models:
            args = (target_X, target_y, each, self.dt, target)
            r = self.__build_tuned_model(*args)

    def prediction(self):
        for target in self.targets:
            self.prediction_models[target] = self.__load_models(self.all_models, self.dt, target)

    def find_predictions(self):
        """ Find predictions """
        for target in self.targets:
            for index, method in enumerate(self.all_models):
                preds = str(method) + '_' + str(target) + '_preds'
                print(preds)
                self.all_preds[preds] = self.prediction_models[target][index].predict(self.adjusted_upcoming_data)
                print(self.all_preds[preds])

                if target == 'points' and method == 'log':
                    self.probs = self.__data_frame(self.prediction_models[target][index].predict_proba(self.adjusted_upcoming_data))
                    self.probs = self.probs.rename(columns={0: 'Probability 0', 1: 'Probability 1', 2: 'Probability 2'})

    def predictions_reorder(self):
        columns = ['team_name', 'opp_name', 'scheduled', 'is_home']
        # Remove all columns except the ones above
        upcoming_matches = self.upcoming_data[columns]

        # Add predictions to the end of that DF
        results = self.__data_frame.from_dict(self.all_preds)
        upcoming_matches = self.__concat_data([upcoming_matches, results, self.probs], axis=1)
        self.reordered_matches = self.__data_frame([])

        for rows in upcoming_matches.iterrows():
            for i in upcoming_matches['team_name']:
                if rows[1]['opp_name'] == i:
                    self.reordered_matches = self.reordered_matches.append(rows[1])
                    self.reordered_matches = self.reordered_matches.append(upcoming_matches[upcoming_matches['team_name'].isin([i])])

        self.reordered_matches = self.reordered_matches.drop_duplicates()

    def predictions_compare(self):
        """ To compare when we have actual results"""
        actual_results = self.__read_data('actual_results.csv')
        actual_results = actual_results.rename(columns = {'Unnamed: 0':'idx'})
        indexed_results = actual_results.set_index('idx')
        self.reordered_matches = self.__concat_data([self.reordered_matches, indexed_results], axis=1)

    def predictions_save(self):
        self.reordered_matches = self.reordered_matches.reset_index(drop=True)
        self.reordered_matches.to_csv(self.predictions_csv)
        print('Prediction CSV saved')

    def init_raw_data(self):
        if self.testing:
            self.raw_data = self.__get_data()
            self.raw_data.to_csv(self.data_csv)
        else:
            self.raw_data = self.__read_data(self.data_csv)
            self.raw_data = self.raw_data.drop(self.raw_data.columns[[0]], axis=1)
        print('Data Loaded...')
        print("Dataset size :: {}".format(self.raw_data.shape))

    def init_ranked_data(self):
        if self.testing:
            args = (self.leagues, self.teams, self.rounds, self.raw_data, False)
            self.ranked_data = self.__get_rankings(*args)
            self.ranked_data.to_csv(self.ranked_data_csv)
        else:
            self.ranked_data = self.__read_data(self.ranked_data_csv)
            self.ranked_data = self.ranked_data.drop(self.ranked_data.columns[[0]], axis=1)
        print('Ranked Data Loaded...')

    def init_upcoming_matches_data(self):
        self.upcoming_matches = self.upcoming_matches
        self.upcoming_matches.to_csv(self.upcoming_matches_csv)
        self.upcoming_data = self.__predictions(self.upcoming_matches)

    def init_ranked_upcoming_matches_data(self):
        if self.testing:
            args = (self.adjusted_leagues, self.teams, self.adjusted_league_rounds, self.upcoming_data, True)
            self.upcoming_ranked_data = self.__get_rankings(*args)
            self.upcoming_ranked_data.to_csv(self.ranked_upcoming_matches_csv)
        else:
            self.upcoming_ranked_data = self.__read_data(self.ranked_upcoming_matches_csv)
            self.upcoming_ranked_data = self.upcoming_ranked_data.drop(self.upcoming_ranked_data.columns[[0]], axis=1)
        print('Loaded Upcoming Data...')


class NBAPredictions(FormulatePredictions):
    testing = True


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

soccer_params = dict(
    testing=False,
    get_data=form_data.run_data,
    read_data=pd.read_csv,
    data_csv='../csv/11_15_16/raw_data.csv',
    ranked_data_csv='../csv/11_15_16/ranked_data.csv',
    upcoming_matches_csv='../csv/11_15_16/upcoming_matches.csv',
    ranked_upcoming_matches_csv='../csv/11_15_16/upcoming_ranked_data.csv',
    predictions_csv='../csv/11_15_16/all_predictions.csv',
    leagues=model_libs.get_leagues_country_codes,
    rounds=model_libs.get_leagues_rounds,
    teams=form_data.get_teams,
    convert_goal=lambda row: model_libs.set_group(row['goals']),
    adjust_features=model_libs.adjust_features,
    targets=["points", "converted_goals", "no_ties"],
    extract_target=model_libs._extract_target,
    build_tuned_model=form_model.build_tuned_model,
    all_models=['gnb', 'randomForest', 'log'],
    load_models=form_model.load_models,
    predictions=predict_matches.predictions,
    adjusted_leagues={"epl": 'ENG', "bundesliga": 'DEU', "primera_division": 'ESP', "ligue_1": 'FRA'},
    upcoming_matches=upcoming_matches,
    data_frame=pd.DataFrame,
    concat_data=pd.concat,
)

b = SoccerPredictions(**soccer_params)
b.run()

#a = NBAPredictions(**soccer_params)
#a.run()
