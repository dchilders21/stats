import pandas as pd
import mysql.connector
import datetime
from datetime import timedelta

cnx = mysql.connector.connect(user='root', password='',
                              host='127.0.0.1',
                              database='mls')
cursor = cnx.cursor(dictionary=True, buffered=True)

match_details = pd.read_sql('SELECT * FROM home_away_coverage',  cnx)
query = "SELECT id FROM teams LIMIT 1"
cursor.execute(query)

recent_performance = 3
week = 4


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
    18: datetime.datetime(2016, 7, 10, 23)
}


def calculate_games(team_id, date):

    played = 0
    win = 0
    loss = 0
    recent_wins = 0
    recent_losses = 0
    opp = []
    count = 1

    # Sometimes the weeks are even so just subtract 7 days for now
    matches = match_details.loc[((match_details['home_id'] == team_id) | (match_details['away_id'] == team_id)) &
                                (match_details['scheduled'] < (date - timedelta(days=7)))]

    total_games = len(matches)
    recent = False

    for index, game in matches.iterrows():

        if (total_games - recent_performance) < count:
            recent = True

        played += 1

        # Home Wins and Road Losses are .8 while Road Wins and Home Losses are 1.2 / Draws remain the same
        if team_id == game['home_id']:
            if game['home_points'] == 3:
                if recent:
                    recent_wins += .8
                win += .8
                # print('Home Win .8')
            elif game['home_points'] == 1:
                if recent:
                    recent_wins += .5
                    recent_losses += .5
                win += .5
                loss += .5
                # print('Home Draw .5')
            else:
                if recent:
                    recent_losses += 1.2
                loss += 1.2
                # print('Home Loss 1.2')

            opp.append(game['away_id'])
        else:
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

            opp.append(game['home_id'])

        count += 1

    print(" ========================== ")
    print("Team Id : {}".format(team_id))
    print("Win : {}".format(win))
    print("Loss : {}".format(loss))
    print("Played : {}".format(played))
    print("Opp : {}".format(opp))
    print("Recent Wins : {}".format(recent_wins))
    print("Recent Losses : {}".format(recent_losses))

    return win, loss, played, opp, recent_wins, recent_losses

# Iterating through all the Teams in the DB
for team in cursor:
    print(team['id'])
    print('~~~~~~~~~~~~~~~~~~~')
    goal_diff = 0
    total_points = 0
    isHome = False

    # Need to find the current match(es) first
    current_match = match_details.loc[((match_details['home_id'] == team['id']) |
        (match_details['away_id'] == team['id'])) & ((match_details['scheduled'] < (schedule_2016[week]))
                                    & (match_details['scheduled'] > (schedule_2016[week] - timedelta(days=7))))]

    # Assuming a team only plays once a 'week'
    if len(current_match) == 1:
        for i, cur_match in current_match.iterrows():
            if team['id'] == cur_match['home_id']:
                opp_id = cur_match['away_id']
            else:
                opp_id = cur_match['home_id']

    # Need to find the previous matches
    matches = match_details.loc[((match_details['home_id'] == team['id']) |
        (match_details['away_id'] == team['id'])) & (match_details['scheduled'] <
                                                     (schedule_2016[week] - timedelta(days=7)))]
    # Individual Matches
    for index, match in matches.iterrows():

        if team['id'] == match['home_id']:
            isHome = True
            goal_diff += match['home_score'] - match['away_score']
            total_points += match['home_points']
        else:
            goal_diff += match['away_score'] - match['home_score']
            total_points += match['away_points']

    # For this Match of the the week, calculate the 'Chosen' teams winning percentage so far in the season
    games_won, games_lost, games_played, _, recent_games_won, recent_games_lost = calculate_games(team['id'], (schedule_2016[week]))
    print('Goal Diff - {} '.format(goal_diff))
    print('Total Points - {} '.format(total_points))
    print('Games Played = {} '.format(games_played))
    print("Games Won {0} : Games Lost {1} : Recent Wins {2} : Recent Losses {3}".format(
        games_won, games_lost, recent_games_won, recent_games_lost))

    # Calculate the Opponents Winning Percentage
    print('Current Opponent ID : {0}'.format(opp_id))

    opp_games_won, opp_games_lost, opp_games_played, opp_opp, opp_recent_wins, opp_recent_losses = calculate_games(
        opp_id, (schedule_2016[week]))
    print('Opp Won {0} : Opp Lost {1} : Opp Recent Wins {2} : Opp Recent Losses {3}'.format(
        opp_games_won, opp_games_lost, opp_recent_wins, opp_recent_wins))

    opp_opp_won_total = 0
    opp_opp_lost_total = 0
    for opp_opp_id in opp_opp:
        opp_opp_games_won, opp_opp_games_losses, _, _, _, _ = calculate_games(
            opp_opp_id, (schedule_2016[week]))
        opp_opp_won_total += opp_opp_games_won
        opp_opp_lost_total += opp_opp_games_losses

    print('Opp Opp Won {0} : Opp Opp Lost {1}'.format(opp_opp_won_total, opp_opp_lost_total))

    # strength_of_schedule
    # recent_performance
    # home_road performance
    # match_id
