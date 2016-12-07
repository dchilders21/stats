import pandas as pd
import os
from datetime import datetime, timedelta
from stats.sports.nba import nba_form_data
from stats import predict_matches
from stats.classes.results import FormulatePredictions


class NBAPredictions(FormulatePredictions, object):

    def __init__(self, **kwrargs):
        super().__init__(**kwrargs)
        self.testing = kwrargs.get('testing') or False
        self.today_date = kwrargs.get('today_date')
        self.prev_day = kwrargs.get('prev_day')
        self.__data_frame = kwrargs.get('data_frame')

    def run(self):
        """ Pull in data and assign rankings """
        self.init_raw_data()
        self.init_ranked_data()


ignore_cols = ['match_id', 'team_id', 'team_name', 'opp_id', 'opp_name', 'scheduled', 'games_played', 'round', 'current_formation']
columns_to_drop = ['current_record', 'opp_record', 'goals_for', 'opp_goals_for', 'goals_against', 'opp_goals_against', 'rpi']

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
    sport='nba'
)

a = NBAPredictions(**nba_params)
a.run()
