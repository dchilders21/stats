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
    goals_for = 0
    goals_against = 0
    goal_diff = 0
    total_points = 0
    count = 1

    # Home Away Features
    home_away_features = {'home_possession': [], 'away_possession': [], 'home_attacks':[], 'away_attacks':[],
                          'home_dangerous_attacks': [], 'away_dangerous_attacks': [], 'home_yellow_card': [], 'away_yellow_card': [],
                          'home_corner_kicks': [], 'away_corner_kicks': [], 'home_shots_on_target': [], 'away_shots_on_target': [],
                          'home_shots_total': [], 'away_shots_total': [], 'home_ball_safe': [], 'away_ball_safe': [],
                          'home_played': [], 'away_played': []}

    # Extended Features
    extended_features = {'possession': [], 'ball_safe': [], 'attacks': [], 'dangerous_attacks': [],
                         'shots_total': [], 'shots_on_target': []}
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
            goals_for = game['home_score']
            goals_against = game['away_score']
            goal_diff += game['home_score'] - game['away_score']
            total_points += game['home_points']

            first_half_goals += game['home_first_half_score']
            sec_half_goals += game['home_second_half_score']

            opp_first_half_goals += game['away_first_half_score']
            opp_sec_half_goals += game['away_second_half_score']

            goals_home += game['home_points']
            opp_goals_at_away += game['away_points']

            prev_opp.append(game['away_id'])

            # Home Away Features
            home_away_features['home_possession'].append(game['home_possession'])
            home_away_features['home_attacks'].append(game['home_attacks'])
            home_away_features['home_dangerous_attacks'].append(game['home_dangerous_attacks'])
            home_away_features['home_yellow_card'].append(game['home_yellow_card'])
            home_away_features['home_corner_kicks'].append(game['home_corner_kicks'])
            home_away_features['home_shots_on_target'].append(game['home_shots_on_target'])
            home_away_features['home_shots_total'].append(game['home_shots_total'])
            home_away_features['home_ball_safe'].append(game['home_ball_safe'])

            # Extended Home Features
            extended_features['possession'].append(game['home_possession'])
            extended_features['ball_safe'].append(game['home_ball_safe'])
            extended_features['attacks'].append(game['home_attacks'])
            extended_features['dangerous_attacks'].append(game['home_dangerous_attacks'])
            extended_features['shots_total'].append(game['home_shots_total'])
            extended_features['shots_on_target'].append(game['home_shots_on_target'])

        else:
            away_played += 1
            team_name = game["away_team"]

            if game['away_points'] == 3:
                if recent:
                    recent_wins += 1.2
                win += 1.2

            elif game['away_points'] == 1:
                if recent:
                    recent_wins += .5
                    recent_losses += .5
                win += .5
                loss += .5

            else:
                if recent:
                    recent_losses += .8
                loss += .8

            total_goals += game['away_score']
            goals_for = game['away_score']
            goals_against = game['home_score']
            goal_diff += game['away_score'] - game['home_score']
            total_points += game['away_points']

            first_half_goals += game['away_first_half_score']
            sec_half_goals += game['away_second_half_score']

            opp_first_half_goals += game['home_first_half_score']
            opp_sec_half_goals += game['home_second_half_score']

            goals_away += game['away_points']
            opp_goals_at_home += game['home_points']

            prev_opp.append(game['home_id'])

            # Home Away Features
            home_away_features['away_possession'].append(game['away_possession'])
            home_away_features['away_attacks'].append(game['away_attacks'])
            home_away_features['away_dangerous_attacks'].append(game['away_dangerous_attacks'])
            home_away_features['away_yellow_card'].append(game['away_yellow_card'])
            home_away_features['away_corner_kicks'].append(game['away_corner_kicks'])
            home_away_features['away_shots_on_target'].append(game['away_shots_on_target'])
            home_away_features['away_shots_total'].append(game['away_shots_total'])
            home_away_features['away_ball_safe'].append(game['away_ball_safe'])

            # Extended Away Features
            extended_features['possession'].append(game['away_possession'])
            extended_features['ball_safe'].append(game['away_ball_safe'])
            extended_features['attacks'].append(game['away_attacks'])
            extended_features['dangerous_attacks'].append(game['away_dangerous_attacks'])
            extended_features['shots_total'].append(game['away_shots_total'])
            extended_features['shots_on_target'].append(game['away_shots_on_target'])

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

    home_away_features['home_played'].append(home_played)
    home_away_features['away_played'].append(away_played)

    for k, v in home_away_features.items():
        if len(v) != 0:
            home_away_features[k] = np.nanmean(np.array(v))
        else:
            home_away_features[k] = np.nan

    for key, value in extended_features.items():
        extended_features[key] = np.nanmean(np.array(value))

    if stats:
        print(" ========================== ")
        print("Team Id : {} - Name : {}".format(team_id, team_name))
        print("Prev Opponent Ids : {}".format(prev_opp))
        print("FEATURES (Stats from * Previous Matches)")
        print("Total Goals : {}".format(total_goals))
        print("Total Points : {}".format(total_points))
        # print("Win Points : {}".format(win))
        # print("Loss Points : {}".format(loss))
        print("Played : {}".format(played))
        print("Recent Wins : {} out of {}".format(recent_wins, recent_performance))
        print("Goal Diff : {}".format(goal_diff))
        print("Margin : {}".format(np.divide(goal_diff, played)))
        print("")
        print("HOME AWAY FEATURES")
        print(home_away_features)
        print("EXTENDED FEATURES")
        print(extended_features)

        # Still can weight games more on most recent games
        print("\nTARGETS (RESULTS OF CURRENT MATCH)")
        print("Points : {}".format(points))
        print("Goals : {}".format(goals))
        print("Opp_Goals : {}".format(opp_goals))

    return match_id, team_id, team_name, scheduled, int(is_home == True), total_points, total_goals, \
           goals_for, goals_against, goal_diff, played, win, loss, recent_wins, recent_losses, prev_opp, \
           current_opp, points, goals, opp_goals, home_away_features, extended_features


# Assuming a team only plays once in the previous 7 days
def create_match(team_id, current_matches, match_details, round_number, stats, targets):
    """Finds the matches needed for the given week, opponents and the previous rounds"""

    previous_matches = match_details.loc[
        ((match_details['home_id'] == team_id) | (match_details['away_id'] == team_id)) &
        (match_details['round'] < round_number)]

    # Find CUR_TEAM's stats
    match_id, team_id, team_name, scheduled, is_home, total_points, total_goals, goals_for, goals_against, goal_diff, \
        played, win, loss, recent_wins, recent_losses, prev_opp, opp_id, points, goals, opp_goals, \
        home_away_features, extended_features = calculate_stats(team_id, current_matches, previous_matches, stats, targets)

    # Calculate the OPPONENTS stats
    if stats:
        print('Current Opponent ID : {0}'.format(opp_id))

    # Find OPP_TEAM's stats
    opp_previous_matches = match_details.loc[
        ((match_details['home_id'] == opp_id) | (match_details['away_id'] == opp_id)) &
        (match_details['round'] < round_number)]

    _, opp_team_id, opp_team_name, _, opp_is_home, opp_total_points, opp_total_goals, opp_goals_for, opp_goals_against, opp_goal_diff, \
    opp_played, opp_win, opp_loss, opp_recent_wins, opp_recent_losses, opp_opp, _, _, _, _, opp_home_away_features, opp_extended_features = calculate_stats(opp_id, current_matches, opp_previous_matches, stats, targets)

    if stats:
        print('Current Opponents of Current Team : {0}'.format(prev_opp))

    for prev_opp_id in prev_opp:
        prev_opp_previous_matches = match_details.loc[
            ((match_details['home_id'] == prev_opp_id) | (match_details['away_id'] == prev_opp_id)) &
            (match_details['round'] < round_number)]

        _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, \
        prev_opp_extended_features = calculate_stats(prev_opp_id, current_matches, prev_opp_previous_matches, False, targets)

    opp_opp_won_total = 0
    opp_opp_lost_total = 0

    if stats:
        print('Current Opponents of Opponent : {0}'.format(opp_opp))

    # Calculate OPPONENTS of the OPPONENTS stats
    for opp_opp_id in opp_opp:

        opp_opp_previous_matches = match_details.loc[
            ((match_details['home_id'] == opp_opp_id) | (match_details['away_id'] == opp_opp_id)) &
            (match_details['round'] < round_number)]

        opp_opp_match_id, opp_opp_team_id, opp_opp_team_name, scheduled, opp_opp_is_home, opp_opp_total_points, opp_opp_total_goals, opp_opp_goals_for, opp_opp_goals_against, opp_opp_goal_diff, \
        opp_opp_played, opp_opp_win, opp_opp_loss, opp_opp_recent_wins, opp_opp_recent_losses, _, _, _, _, _, _, opp_opp_extended_features = calculate_stats(opp_opp_id, current_matches, opp_opp_previous_matches, False, targets)
        opp_opp_won_total += opp_opp_win
        opp_opp_lost_total += opp_opp_loss

    if stats:
        print("\nTeam")
        print(extended_features)
        print(home_away_features)
        print("Opponent")
        print(opp_extended_features)
        print(opp_home_away_features)
        print("Previous Opponent of Current Team")
        print(prev_opp_extended_features)
        print("Opponent Opponents")
        print(opp_opp_extended_features)

    feature = {'match_id': match_id, 'team_id': team_id, 'team_name': team_name, 'opp_id': opp_team_id, 'opp_name': opp_team_name, 'scheduled': scheduled, 'games_played': played, 'is_home':
                is_home, 'avg_points': np.divide(total_points, played), 'goals_for': goals_for, 'goals_against': goals_against, 'avg_goals': np.divide(total_goals, played), 'margin': np.divide(goal_diff, played),
                'goal_diff': goal_diff, 'win_percentage': np.divide(win, (win+loss)), 'sos': (2*np.divide(opp_win, (opp_win+opp_loss))) + np.divide(opp_opp_won_total, (opp_opp_won_total+opp_opp_lost_total))/3,
                'opp_is_home': opp_is_home, 'opp_avg_points': np.divide(opp_total_points, opp_played), 'opp_avg_goals': np.divide(opp_total_goals, opp_played),
                'opp_margin': np.divide(opp_goal_diff, opp_played), 'opp_goal_diff': opp_goal_diff,
                'opp_win_percentage': np.divide(opp_win, (opp_win+opp_loss)), 'opp_opp_record': np.divide(opp_opp_win, (opp_opp_win+opp_opp_loss)),
                'points': points} # 'goals': goals, 'opp_goals': opp_goals

    home_away_features = {'current_team': home_away_features, 'current_opp': opp_home_away_features}

    extended_features = {'e_f': extended_features, 'opp_e_f': opp_extended_features,
                        'prev_opp_e_f': prev_opp_extended_features,
                        'opp_opp_e_f': opp_opp_extended_features}

    if stats:
        print("//////////////////////////////////////////////////")

    return feature, home_away_features, extended_features





