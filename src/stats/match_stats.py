import numpy as np


def calculate_stats(team_id, current_matches, prev_matches, stats, targets):
    """ Calculates the stats of the the current team in the current match
         and the opponent team in the current match.  Also calculates the
         previous matches for the current team"""


    recent_performance = 3

    # Features
    home_played = 0
    away_played = 0
    win = 0
    loss = 0
    recent_wins = 0
    recent_losses = 0
    prev_opp = []
    current_opp = 0
    total_goals = 0
    goal_diff = 0
    total_points = 0
    count = 1

    # Targets
    points = 0
    goals = 0
    opp_goals = 0

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

            prev_opp.append(game['away_id'])

            # home_possession += game['home_possession']

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

            prev_opp.append(game['home_id'])
            # away_possession += game['away_possession']

        count += 1

    # Pulling the data for the CURRENT MATCH
    for index, cur_game in current_matches.iterrows():
        match_id = cur_game["match_id"]
        scheduled = cur_game["scheduled"]
        if team_id == cur_game['home_id']:
            is_home = True
            team_name = cur_game["home_team"]
            current_opp = cur_game['away_id']

            if targets:
                # Targets
                points = cur_game['home_points']
                goals = cur_game['home_score']
                opp_goals = cur_game['away_score']

        else:

            is_home = False
            team_name = cur_game["away_team"]
            current_opp = cur_game['home_id']

            if targets:
                # Targets
                points = cur_game['away_points']
                goals = cur_game['away_score']
                opp_goals = cur_game['home_score']

    played = home_played + away_played

    if stats:
        print(" ========================== ")
        print("Team Id : {} - Name : {}".format(team_id, team_name))
        print("Prev Opponent Ids : {}".format(prev_opp))
        print("FEATURES (Stats from * Previous Matches)")
        print("Total Points : {}".format(total_points))
        # print("Win Points : {}".format(win))
        # print("Loss Points : {}".format(loss))
        print("Played : {}".format(played))
        # print("Home Played : {}".format(home_played))
        # print("Away Played : {}".format(away_played))
        print("Recent Wins : {} out of {}".format(recent_wins, recent_performance))
        print("Goal Diff : {}".format(goal_diff))
        print("Margin : {}".format(np.divide(goal_diff, played)))
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

    return match_id, team_id, team_name, scheduled, int(is_home == True), total_points, total_goals, goal_diff, played, win, loss, recent_wins, recent_losses, prev_opp, current_opp, points, goals, opp_goals


# Assuming a team only plays once in the previous 7 days
def create_match(team_id, current_matches, previous_matches, stats, targets):
    """Finds the matches needed for the given week, opponents and the previous weeks"""

    # For this Match of the the week, calculate the 'Chosen' teams winning percentage so far in the season
    match_id, team_id, team_name, scheduled, is_home, total_points, total_goals, goal_diff, played, win, loss, recent_wins, recent_losses, _, opp_id, points, goals, opp_goals = calculate_stats(team_id, current_matches, previous_matches, stats, targets)
    print("")

    # Calculate the Opponents Winning Percentage
    print('Current Opponent ID : {0}'.format(opp_id))

    opp_match_id, opp_team_id, opp_team_name, scheduled, opp_is_home, opp_total_points, opp_total_goals, opp_goal_diff, \
    opp_played, opp_win, opp_loss, opp_recent_wins, opp_recent_losses, opp_opp, _, _, _, _ = calculate_stats(opp_id, current_matches, previous_matches, stats, targets)
    # print('\nOpp Won {0} : Opp Lost {1} : Opp Recent Wins {2} : Opp Recent Losses {3}'.format(
        # opp_win, opp_loss, opp_recent_wins, opp_recent_wins))

    opp_opp_won_total = 0
    opp_opp_lost_total = 0

    for opp_opp_id in opp_opp:
        opp_opp_match_id, opp_opp_team_id, opp_opp_team_name, scheduled, opp_opp_is_home, opp_opp_total_points, opp_opp_total_goals, opp_opp_goal_diff, \
        opp_opp_played, opp_opp_win, opp_opp_loss, opp_opp_recent_wins, opp_opp_recent_losses,  _, _, _, _, _= calculate_stats(opp_opp_id, current_matches, previous_matches, False, targets)
        opp_opp_won_total += opp_opp_win
        opp_opp_lost_total += opp_opp_loss

    # print('Opp Opp Won {0} : Opp Opp Lost {1} \n'.format(opp_opp_won_total, opp_opp_lost_total))

    feature = {'match_id': match_id, 'team_id': team_id, 'team_name': team_name, 'opp_id': opp_team_id, 'opp_name': opp_team_name, 'scheduled': scheduled, 'is_home':
                is_home, 'avg_points': np.divide(total_points, played), 'avg_goals': np.divide(total_goals, played), 'margin': np.divide(goal_diff, played),
                'goal_diff': goal_diff, 'win_percentage': np.divide(win, (win+loss)), 'sos': (2*np.divide(opp_win, (opp_win+opp_loss))) + np.divide(opp_opp_won_total, (opp_opp_won_total+opp_opp_lost_total))/3,
                'opp_is_home': opp_is_home, 'opp_avg_points': np.divide(opp_total_points, opp_played), 'opp_avg_goals': np.divide(opp_total_goals, opp_played),
                'opp_margin': np.divide(opp_goal_diff, opp_played), 'opp_goal_diff': opp_goal_diff,
                'opp_win_percentage': np.divide(opp_win, (opp_win+opp_loss)), 'opp_opp_record': np.divide(opp_opp_win, (opp_opp_win+opp_opp_loss)), 'points': points } # 'goals': goals, 'opp_goals': opp_goals

    print("//////////////////////////////////////////////////")

    return feature





