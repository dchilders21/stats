import pandas as pd
import mysql.connector
import datetime
from datetime import timedelta
import numpy

cnx = mysql.connector.connect(user='root', password='',
                              host='127.0.0.1',
                              database='mls')
cursor = cnx.cursor(dictionary=True, buffered=True)

match_details = pd.read_sql('SELECT * FROM home_away_coverage',  cnx)
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

recent_performance = 3
week = 20
adjusted_time = (schedule_2016[week] + datetime.timedelta(hours=7))
prev_week = (schedule_2016[week-1] + datetime.timedelta(hours=7))
features = {}

def calculate_stats(team_id, current_matches, prev_matches, stats):


    # Features
    home_played = 0
    away_played = 0
    win = 0
    loss = 0
    recent_wins = 0
    recent_losses = 0
    opp = []
    total_goals = 0
    goal_diff = 0
    total_points = 0
    count = 1

    first_half_goals = 0
    sec_half_goals = 0
    opp_first_half_goals = 0
    opp_sec_half_goals = 0

    goals_home = 0
    goals_away = 0
    opp_goals_at_home = 0  # Opponent goals when CURRENT team is AT Home
    opp_goals_at_away = 0  # Opponent goals when CURRENT team is Away

    # home_possession = 0
    # away_possession = 0

    # attacks
    # dangerous attacks
    # fouls
    # yellow_cards
    # corners
    # shots on target
    # saves
    # ball safe ?
    # goal_attempts
    # opp_SOS
    total_games = len(prev_matches)
    recent = False

    # Pulling Data for PREVIOUS Matches
    for index, game in prev_matches.iterrows():
        if (total_games - recent_performance) < count:
            recent = False

        # Home Wins and Road Losses are .8 while Road Wins and Home Losses are 1.2 / Draws remain the same
        if team_id == game['home_id']:
            home_played += 1

            if game['home_points'] == 3:
                if recent:
                    recent_wins += .8
                win += .8

            elif game['home_points'] == 1:
                if recent:
                    recent_wins += .5
                    recent_losses += .5
                win += .5
                loss += .5

            else:
                if recent:
                    recent_losses += 1.2
                loss += 1.2

            total_goals += game['home_score']
            goal_diff += game['home_score'] - game['away_score']
            total_points += game['home_points']

            first_half_goals += game['home_first_half_score']
            sec_half_goals += game['home_second_half_score']

            opp_first_half_goals += game['away_first_half_score']
            opp_sec_half_goals += game['away_second_half_score']

            goals_home += game['home_points']
            opp_goals_at_away += game['away_points']

            # home_possession += game['home_possession']

            opp.append(game['away_id'])

        else:
            away_played += 1
            team_name = game["away_team"]

            if game['away_points'] == 3:
                if recent:
                    recent_wins += 1.2
                win += 1.2
                # print('Away Win 1.2')
            elif game['away_points'] == 1:
                if recent:
                    recent_wins += .5
                    recent_losses += .5
                win += .5
                loss += .5
                # print('Away Draw .5')
            else:
                if recent:
                    recent_losses += .8
                loss += .8
                # print('Away Loss .8')

            total_goals += game['away_score']
            goal_diff += game['away_score'] - game['home_score']
            total_points += game['away_points']

            first_half_goals += game['away_first_half_score']
            sec_half_goals += game['away_second_half_score']

            opp_first_half_goals += game['home_first_half_score']
            opp_sec_half_goals += game['home_second_half_score']

            goals_away += game['away_points']
            opp_goals_at_home += game['home_points']
            # away_possession += game['away_possession']

            opp.append(game['home_id'])

        count += 1

    # Pulling the data for the CURRENT MATCH
    for index, cur_game in current_matches.iterrows():
        match_id = cur_game["match_id"]
        scheduled = cur_game["scheduled"]
        if team_id == cur_game['home_id']:
            is_home = True
            team_name = cur_game["home_team"]

            # Targets
            points = cur_game['home_points']
            goals = cur_game['home_score']
            opp_goals = cur_game['away_score']

        else:

            is_home = False
            team_name = cur_game["away_team"]

            # Targets
            points = cur_game['away_points']
            goals = cur_game['away_score']
            opp_goals = cur_game['home_score']

    played = home_played + away_played

    if stats:
        print(" ========================== ")
        # print("Team Id : {} - Name : {}".format(team_id, team_name))
        print("Prev Opponent Ids : {}".format(opp))
        print("FEATURES (Stats from * Previous Matches)")
        print("Total Points : {}".format(total_points))
        # print("Win Points : {}".format(win))
        # print("Loss Points : {}".format(loss))
        print("Played : {}".format(played))
        # print("Home Played : {}".format(home_played))
        # print("Away Played : {}".format(away_played))
        print("Recent Wins : {} out of {}".format(recent_wins, recent_performance))
        print("Goal Diff : {}".format(goal_diff))
        print("Margin : {}".format(numpy.divide(goal_diff, played)))
        # Goals Allowed
        # print("1st H Goals : {}".format(first_half_goals))
        # print("2nd H Goals : {}".format(sec_half_goals))
        # print("Opp 1st H Goals : {}".format(opp_first_half_goals))
        # print("Opp 2nd H Goals : {}".format(opp_sec_half_goals))
        # print("Goals Home: {}".format(goals_home))
        # print("Goals Away: {}".format(goals_away))
        # print("Opp Goals @ Home : {}".format(opp_goals_at_home))
        # print("Opp Goals @ Away : {}".format(opp_goals_at_away))
        # print("Home Possession Avg : {}".format(numpy.float64(home_possession)/home_played))
        # print("Away Possession Avg : {}".format(numpy.float64(away_possession)/away_played))

        print("\nTARGETS (RESULTS OF CURRENT MATCH)")
        print("Points : {}".format(points))
        print("Goals : {}".format(goals))
        print("Opp_Goals : {}".format(opp_goals))


    return match_id, team_id, team_name, scheduled, int(is_home == True), total_points, total_goals, goal_diff, played, win, loss, recent_wins, recent_losses, opp, points, goals, opp_goals

upcoming_matches = pd.read_sql("SELECT * FROM matches WHERE status = 'scheduled'", cnx)
previous_matches = pd.read_sql("SELECT * FROM matches WHERE status = 'closed'", cnx)

# print("From {} to {} \n".format((schedule_2016[week-1] + datetime.timedelta(hours=7)), adjusted_time))

# Assuming a team only plays once in the previous 7 days

def create_match(team_id, week):

    print("WEEK {} :: TEAM {}".format(week, team_id))

    adjusted_time = (schedule_2016[week] + datetime.timedelta(hours=7))

    if week > 1:
        prev_week = (schedule_2016[week - 1] + datetime.timedelta(hours=7))
    else:
        prev_week = (schedule_2016[week] + datetime.timedelta(hours=7)) - datetime.timedelta(days=7)

    current_matches = match_details.loc[((match_details['home_id'] == team_id) | (match_details['away_id'] == team_id)) &
                                ((match_details['scheduled'] < adjusted_time) & (match_details['scheduled'] > prev_week))]

    previous_matches = match_details.loc[((match_details['home_id'] == team_id) | (match_details['away_id'] == team_id)) &
                                         (match_details['scheduled'] < prev_week)]

    if not current_matches.empty:
        for i, cur_match in current_matches.iterrows():
            team_id = cur_match['home_id']
            opp_id = cur_match['away_id']

            # For this Match of the the week, calculate the 'Chosen' teams winning percentage so far in the season
            match_id, team_id, team_name, scheduled, is_home, total_points, total_goals, goal_diff, played, win, loss, recent_wins, recent_losses, _, points, goals, opp_goals = calculate_stats(team_id, current_matches, previous_matches, True)
            print("")

            # Calculate the Opponents Winning Percentage
            print('Current Opponent ID : {0}'.format(opp_id))

            opp_match_id, opp_team_id, opp_team_name, scheduled, opp_is_home, opp_total_points, opp_total_goals, opp_goal_diff, \
            opp_played, opp_win, opp_loss, opp_recent_wins, opp_recent_losses, opp_opp, _, _, _ = calculate_stats(opp_id, current_matches, previous_matches, True)
            print('\nOpp Won {0} : Opp Lost {1} : Opp Recent Wins {2} : Opp Recent Losses {3}'.format(
                opp_win, opp_loss, opp_recent_wins, opp_recent_wins))

            opp_opp_won_total = 0
            opp_opp_lost_total = 0

            for opp_opp_id in opp_opp:
                opp_opp_match_id, opp_opp_team_id, opp_opp_team_name, scheduled, opp_opp_is_home, opp_opp_total_points, opp_opp_total_goals, opp_opp_goal_diff, \
                opp_opp_played, opp_opp_win, opp_opp_loss, opp_opp_recent_wins, opp_opp_recent_losses, _, _, _, _= calculate_stats(opp_opp_id, current_matches, previous_matches, False)
                opp_opp_won_total += opp_opp_win
                opp_opp_lost_total += opp_opp_loss

            print('Opp Opp Won {0} : Opp Opp Lost {1} \n'.format(opp_opp_won_total, opp_opp_lost_total))

            feature = {'match_id': match_id, 'team_id': team_id, 'team_name': team_name, 'opp_id': opp_team_id, 'opp_name': opp_team_name, 'scheduled': scheduled, 'is_home':
                        is_home, 'avg_points': numpy.divide(total_points, played), 'avg_goals': numpy.divide(total_goals, played), 'margin': numpy.divide(goal_diff, played),
                        'goal_diff': goal_diff, 'win_percentage': numpy.divide(win, (win+loss)), 'sos': (2*numpy.divide(opp_win, (opp_win+opp_loss))) + numpy.divide(opp_opp_won_total, (opp_opp_won_total+opp_opp_lost_total))/3,
                        'opp_is_home': opp_is_home, 'opp_avg_points': numpy.divide(opp_total_points, opp_played), 'opp_avg_goals': numpy.divide(opp_total_goals, opp_played),
                        'opp_margin': numpy.divide(opp_goal_diff, opp_played), 'opp_goal_diff': opp_goal_diff,
                        'opp_win_percentage': numpy.divide(opp_win, (opp_win+opp_loss)), 'points': points, 'goals': goals, 'opp_goals': opp_goals}

            print("//////////////////////////////////////////////////")

            return feature

training_list = []

for team in cursor:
    print("TEAM ID : {}".format(team["id"]))
    for i in range(week):
        match_result = create_match(team["id"], i+1)
        if match_result is not None:
            training_list.append(match_result)

columns = ['match_id', 'team_id', 'team_name', 'opp_id', 'opp_name', 'scheduled',
           # Non-Feature Columns
           'is_home', 'avg_points', 'avg_goals', 'margin', 'goal_diff',
           'win_percentage',
           'sos', 'opp_is_home', 'opp_avg_points', 'opp_avg_goals', 'opp_margin',
           'opp_goal_diff', 'opp_win_percentage',
           'points', 'goals', 'opp_goals']  # Target Columns)

training_data = pd.DataFrame(training_list, columns=columns)

print(training_data)


