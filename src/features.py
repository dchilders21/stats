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
query = "SELECT id FROM teams"
cursor.execute(query)

recent_performance = 3
week = 19


# MLS broken out WEEKLY even though teams don't always play a game the same week
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
    20: datetime.datetime(2016, 7, 16, 23)
}


def calculate_games(team_id, date, stats):

    isHome = False
    home_played = 0
    away_played = 0
    win = 0
    loss = 0
    recent_wins = 0
    recent_losses = 0
    opp = []
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

    home_possession = 0
    away_possession = 0

    # attacks
    # dangerous attacks
    # fouls
    # yellow_cards
    # corners
    # shots on target
    # saves
    # ball safe ?
    # goal_attempts

    # Sometimes the weeks are even so just subtract 7 days for now
    matches = match_details.loc[((match_details['home_id'] == team_id) | (match_details['away_id'] == team_id)) &
                                (match_details['scheduled'] < (schedule_2016[week-1]))]

    total_games = len(matches)
    recent = False

    for index, game in matches.iterrows():

        if (total_games - recent_performance) < count:
            recent = True

        # Home Wins and Road Losses are .8 while Road Wins and Home Losses are 1.2 / Draws remain the same
        if team_id == game['home_id']:
            isHome = True
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

    played = home_played + away_played
    print(" ========================== ")
    print("Team Id : {}".format(team_id))
    if stats:
        print("Prev Opponent Ids : {}".format(opp))
        print("Total Points : {}".format(total_points))
        print("Win Points : {}".format(win))
        print("Loss Points : {}".format(loss))
        print("Home Played : {}".format(home_played))
        print("Away Played : {}".format(away_played))
        print("Recent Wins : {} out of {}".format(recent_wins, recent_performance))
        print("Goal Diff : {}".format(goal_diff))
        print("Margin : {}".format(goal_diff/played))
        print("1st H Goals : {}".format(first_half_goals))
        print("2nd H Goals : {}".format(sec_half_goals))
        print("Opp 1st H Goals : {}".format(opp_first_half_goals))
        print("Opp 2nd H Goals : {}".format(opp_sec_half_goals))
        print("Goals Home: {}".format(goals_home))
        print("Goals Away: {}".format(goals_away))
        print("Opp Goals @ Home : {}".format(opp_goals_at_home))
        print("Opp Goals @ Away : {}".format(opp_goals_at_away))
        # print("Home Possession Avg : {}".format(numpy.float64(home_possession)/home_played))
        # print("Away Possession Avg : {}".format(numpy.float64(away_possession)/away_played))

    return win, loss, played, opp, recent_wins, recent_losses

# Iterating through all the Teams in the DB
for team in cursor:

    # Need to find the current match(es) first
    current_match = match_details.loc[((match_details['home_id'] == team['id']) |
        (match_details['away_id'] == team['id'])) & ((match_details['scheduled'] < (schedule_2016[week]))
                                    & (match_details['scheduled'] > (schedule_2016[week-1])))]

    # Assuming a team only plays once in the previous 7 days
    if len(current_match) > 0:
        for i, cur_match in current_match.iterrows():
            if team['id'] == cur_match['home_id']:
                opp_id = cur_match['away_id']
            else:
                opp_id = cur_match['home_id']

            # For this Match of the the week, calculate the 'Chosen' teams winning percentage so far in the season
            games_won, games_lost, games_played, _, recent_games_won, recent_games_lost = calculate_games(team['id'],
                                                                            week, True)

            # Calculate the Opponents Winning Percentage
            print('Current Opponent ID : {0}'.format(opp_id))

            opp_games_won, opp_games_lost, opp_games_played, opp_opp, opp_recent_wins, opp_recent_losses = calculate_games(
                opp_id, week, True)
            print('Opp Won {0} : Opp Lost {1} : Opp Recent Wins {2} : Opp Recent Losses {3}'.format(
                opp_games_won, opp_games_lost, opp_recent_wins, opp_recent_wins))

            opp_opp_won_total = 0
            opp_opp_lost_total = 0

            for opp_opp_id in opp_opp:
                opp_opp_games_won, opp_opp_games_losses, _, _, _, _ = calculate_games(
                    opp_opp_id, week, False)
                opp_opp_won_total += opp_opp_games_won
                opp_opp_lost_total += opp_opp_games_losses

            print("--------------------------------------------")

            print('Opp Opp Won {0} : Opp Opp Lost {1}'.format(opp_opp_won_total, opp_opp_lost_total))

            print("++++++++++++++++++++++++++++++++++++++++++++")
            print("++++++++++++++++++++++++++++++++++++++++++++")
            print("++++++++++++++++++++++++++++++++++++++++++++")
