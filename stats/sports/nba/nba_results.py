import pandas as pd
import os
from datetime import datetime, timedelta
from stats.sports.nba import nba_form_data
from stats import predict_matches, model_libs, form_model
from stats.classes.results import FormulatePredictions


class NBAPredictions(FormulatePredictions, object):

    def __init__(self, **kwrargs):
        super().__init__(**kwrargs)
        self.testing = kwrargs.get('testing') or False
        self.today_date = kwrargs.get('today_date')
        self.prev_day = kwrargs.get('prev_day')
        self.__data_frame = kwrargs.get('data_frame')
        self.sport = kwrargs.get('sport')
        self.targets = kwrargs.get('targets')
        self.to_drop = ignore_cols
        self.__extract_target = kwrargs.get('extract_target')
        self.td = kwrargs.get('today_date')
        self.all_models = kwrargs.get('all_models')

    def run(self):
        """ Pull in data and assign rankings """
        self.init_raw_data()
        # self.init_ranked_data()

        adjusted_data = self.raw_data.copy()
        self.adjusted_data = adjusted_data.drop(self.to_drop, 1)

        for b in basic_features:
            self.adjusted_data["diff_" + b] = self.adjusted_data.apply(
                lambda row: model_libs.diff_square(row["current_team_" + b], row["opp_team_" + b]), axis=1)

            self.adjusted_data = self.adjusted_data.drop('current_team_' + b, 1)
            self.adjusted_data = self.adjusted_data.drop('opp_team_' + b, 1)

        for p in points_features:
            self.adjusted_data = self.adjusted_data.drop('current_team_' + p, 1)
            self.adjusted_data = self.adjusted_data.drop('opp_team_' + p, 1)

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



    def target__total_pts(self):
        target_data = self.adjusted_data.copy()
        target_data = target_data.drop("opp_team_total_pts", 1)
        return self.__extract_target(target_data, 'current_team_total_pts')


ignore_cols = ['game_id', 'team_id', 'team_name', 'opp_id', 'opp_name', 'scheduled', 'games_played', 'rpi']

points_features = ['1st_qtr', '2nd_qtr', '3rd_qtr', '4th_qtr', 'FGM', 'FTM', '3PM',
                   'fast_break_points', 'points_in_paint', 'points_off_turnovers', 'second_chance_points']

basic_features = ['BLK', '3PA', 'AST', 'DREB', 'FGA', 'FTA', 'OREB', 'PF', 'STL', 'turnovers']

upcoming_matches, match_details = predict_matches.get_upcoming_matches()

""" this is designed to run once a day for new games that were pulled in """
today = "11_16_16"
sport_category = "nba"
today_date = datetime.strptime(today, '%m_%d_%y')
prev_day = (today_date - timedelta(days=1)).strftime('%m_%d_%y')

# Leagues skip a week at times so will not always be the previous week
while not os.path.isdir("../../csv/{}/".format(sport_category) + prev_day):
    prev_day = (datetime.strptime(prev_day, '%m_%d_%y') - timedelta(days=1)).strftime('%m_%d_%y')

# Creating this weeks folder
if not os.path.isdir('../../csv/{}/'.format(sport_category) + today + '/'):
    print('Making New Directory for the CSV')
    os.makedirs('../../csv/{}/'.format(sport_category) + today + '/')

r = nba_form_data.RunData(sport_category, today_date)

nba_params = dict(
    testing=True,
    today_date=today_date,
    prev_day=prev_day,
    get_data=nba_form_data.nba_run_data,
    data_frame=pd.DataFrame,
    data_csv='../../csv/nba/{}/raw_data.csv'.format(today),
    get_rankings=nba_form_data.get_rankings_NBA,
    sport='nba',
    targets=['total_pts'],
    extract_target=model_libs._extract_target,
    all_models=['linear_regression'],
    build_tuned_model=form_model.build_tuned_model,
    predictions_csv='../csv/nba/{}/all_predictions.csv'.format(today),
    predictions=predict_matches.predictions,
    load_models=form_model.load_models,
)

a = NBAPredictions(**nba_params)
a.run()
