import pandas as pd
import os
from datetime import datetime, timedelta
from stats.sports.nba import nba_form_data
from stats import predict_matches, model_libs, form_model
from stats.classes.results import FormulatePredictions
from os.path import dirname, abspath


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
        self.__predictions = kwrargs.get('predictions')
        self.__adjust_features = kwrargs.get('adjust_features')
        self.predictions_csv = kwrargs.get('predictions_csv')

    def run(self):
        """ Pull in data and assign rankings """
        self.init_raw_data()
        # self.init_ranked_data()

        adjusted_data = self.raw_data.copy()
        self.adjusted_data = adjusted_data.drop(self.to_drop, 1)
        self.adjusted_data = self.adjust_features(self.adjusted_data)

        #######################

        ''' Start Modeling Targets '''
        for target in self.targets:
            print(' ================================= ')
            print("Target :: {}".format(target))
            method = getattr(self, "target__%s" % target)
            (target_y, target_X) = method()

            self.modeling(target_X, target_y, target)

        self.predictions()

        #######################

        print('Upcoming matches')

        """ Print a CSV for the previous weeks results """
        # Will use this when we have previous predictions from the previous games
        #columns = ['team_name', 'opp_name', 'scheduled', 'is_home', 'match_id', 'points', 'goals']
        #self.predictions_compare()

        self.init_upcoming_data()
        #self.init_ranked_upcoming_matches_data()

        """ Makes sure there are games for the day """
        if not self.upcoming_data.empty:

            """ Formatting data specific to the sport """
            self.upcoming_formatted_data = self.upcoming_data.copy()
            self.upcoming_formatted_data = self.upcoming_formatted_data.drop(self.to_drop, 1)

            self.upcoming_formatted_data = self.adjust_features(self.upcoming_formatted_data)

            self.upcoming_formatted_data_X = self.upcoming_formatted_data.drop(['final_score', 'result'], 1)

            self.find_predictions()
            self.predictions_reorder(['team_name', 'opp_name', 'scheduled_pst', 'is_home', 'game_id', 'team_id', 'opp_id'])
            self.post_predictions()
            self.predictions_save()

    def target__total_pts(self):
        target_data = self.adjusted_data.copy()
        target_data = target_data.drop("result", 1)
        return self.__extract_target(target_data, 'final_score')

    def target__result(self):
        target_data = self.adjusted_data.copy()
        target_data = target_data.drop("final_score", 1)
        return self.__extract_target(target_data, 'result')

    def adjust_features(self, data):
        for b in basic_features:

            data["diff_" + b] = data.apply(
                lambda row: model_libs.diff_square(row["current_team_" + b], row["opp_team_" + b]), axis=1)

            data = data.drop('current_team_' + b, 1)
            data = data.drop('opp_team_' + b, 1)

        for p in points_features:
            data = data.drop('current_team_' + p, 1)
            data = data.drop('opp_team_' + p, 1)

        return data


ignore_cols = ['game_id', 'team_id', 'team_name', 'opp_id', 'opp_name', 'scheduled_pst', 'games_played',
               'rpi', 'opp_final_score']

points_features = ['1st_qtr', '2nd_qtr', '3rd_qtr', '4th_qtr', 'FGM', 'FTM', '3PM',
                   'fast_break_points', 'points_in_paint', 'points_off_turnovers', 'second_chance_points', 'total_pts']

basic_features = ['BLK', '3PA', 'AST', 'DREB', 'FGA', 'FTA', 'OREB', 'PF', 'STL', 'turnovers']

""" this is designed to run once a day for updated games that were pulled in """
#today = "01_01_17"
today = model_libs.tz2ntz(datetime.utcnow(), 'UTC', 'US/Pacific').strftime("%m_%d_%y")
sport_category = "nba"
today_date = datetime.strptime(today, '%m_%d_%y')
prev_day = (today_date - timedelta(days=1)).strftime('%m_%d_%y')

upcoming_games = predict_matches.get_upcoming_games(today_date)
current_path = dirname(dirname(dirname(abspath(__file__))))

# Games skip days at times so will not always be the previous game day
while not os.path.isdir(current_path + "/csv/{}/".format(sport_category) + prev_day):
    prev_day = (datetime.strptime(prev_day, '%m_%d_%y') - timedelta(days=1)).strftime('%m_%d_%y')

# Creating todays folder
if not os.path.isdir(current_path + '/csv/{}/'.format(sport_category) + today + '/'):
    print('Making New Directory {} for the CSV'.format(today))
    os.makedirs(current_path + '/csv/{}/'.format(sport_category) + today + '/')

nba_params = dict(
    testing=True,
    today_date=today_date,
    prev_day=prev_day,
    get_data=nba_form_data.nba_run_single_data, #nba_run_data
    data_frame=pd.DataFrame,
    data_csv=current_path + '/csv/nba/{}/raw_data.csv'.format(today),
    get_rankings=nba_form_data.get_rankings_NBA,
    sport='nba',
    targets=['total_pts', 'result'],
    extract_target=model_libs._extract_target,
    all_models=['linear_regression', 'log'],
    build_tuned_model=form_model.build_tuned_model,
    predictions_csv=current_path + '/csv/nba/{}/all_predictions.csv'.format(today),
    predictions=predict_matches.predictions_nba,
    load_models=form_model.load_models,
    upcoming_matches=upcoming_games,
    upcoming_matches_csv=current_path + '/csv/nba/{}/upcoming_matches.csv'.format(today),
    adjust_features=model_libs.adjust_features,
    concat_data=pd.concat,
    read_data=pd.read_csv,
    post_preds=nba_form_data.nba_add_market
)

a = NBAPredictions(**nba_params)
a.run()
