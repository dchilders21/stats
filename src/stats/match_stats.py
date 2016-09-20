import numpy as np


def calculate_stats(team_id, current_matches, prev_matches, stats, targets):
    """ Calculates the stats of the the current team in the current match
         and the opponent team in the current match.  Also calculates the
         previous matches for the current team"""

    # Features
    current_formation = None
    opp_formation = None
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
    played = float(0)
    goal_efficiency = 0

    # Game Features
    game_features = {'possession': [], 'attacks': [], 'dangerous_attacks': [], 'yellow_cards': [],
                         'corner_kicks': [], 'shots_on_target': [], 'shots_total': [], 'ball_safe': [],
                        'goal_attempts': [], 'saves': [], 'first_half_goals': [], 'sec_half_goals': [], 'goal_kicks': []}

    # Targets
    points = 0
    goals = 0
    opp_goals = 0

    goals_home = 0
    goals_away = 0
    opp_goals_at_home = 0  # Opponent goals when CURRENT team is AT Home
    opp_goals_at_away = 0  # Opponent goals when CURRENT team is Away

    total_games = len(prev_matches)
    # Pulling Data for PREVIOUS Matches
    for index, game in prev_matches.iterrows():

        # Home Wins and Road Losses are .8 while Road Wins and Home Losses are 1.2 / Draws remain the same
        if team_id == game['home_id']:

            if game['home_points'] == 3:
                win += .8

            elif game['home_points'] == 1:
                win += .5
                loss += .5

            else:
                loss += 1.2

            total_goals += game['home_score']
            goals_for += game['home_score']
            goals_against += game['away_score']
            goal_diff += game['home_score'] - game['away_score']
            total_points += game['home_points']

            goals_home += game['home_points']
            opp_goals_at_away += game['away_points']

            prev_opp.append(game['away_id'])

            goal_efficiency = np.divide(game['home_score'], game['home_goal_attempts'])

            game_features['possession'].append(game['home_possession'])
            game_features['attacks'].append(game['home_attacks'])
            game_features['dangerous_attacks'].append(game['home_dangerous_attacks'])
            game_features['yellow_cards'].append(game['home_yellow_card'])
            game_features['corner_kicks'].append(game['home_corner_kicks'])
            game_features['shots_on_target'].append(game['home_shots_on_target'])
            game_features['shots_total'].append(game['home_shots_total'])
            game_features['ball_safe'].append(game['home_ball_safe'])
            game_features['goal_attempts'].append(game['home_goal_attempts'])
            game_features['saves'].append(game['home_saves'])
            game_features['first_half_goals'].append(game['home_first_half_score'])
            game_features['sec_half_goals'].append(game['home_second_half_score'])
            game_features['goal_kicks'].append(game['home_goal_kicks'])

        else:
            team_name = game["away_team"]

            if game['away_points'] == 3:
                win += 1.2

            elif game['away_points'] == 1:
                win += .5
                loss += .5

            else:
                loss += .8

            total_goals += game['away_score']
            goals_for += game['away_score']
            goals_against += game['home_score']
            goal_diff += game['away_score'] - game['home_score']
            total_points += game['away_points']

            goals_away += game['away_points']
            opp_goals_at_home += game['home_points']

            prev_opp.append(game['home_id'])

            goal_efficiency = np.divide(game['away_score'], game['away_goal_attempts'])

            game_features['possession'].append(game['away_possession'])
            game_features['attacks'].append(game['away_attacks'])
            game_features['dangerous_attacks'].append(game['away_dangerous_attacks'])
            game_features['yellow_cards'].append(game['away_yellow_card'])
            game_features['corner_kicks'].append(game['away_corner_kicks'])
            game_features['shots_on_target'].append(game['away_shots_on_target'])
            game_features['shots_total'].append(game['away_shots_total'])
            game_features['ball_safe'].append(game['away_ball_safe'])
            game_features['goal_attempts'].append(game['away_goal_attempts'])
            game_features['saves'].append(game['away_saves'])
            game_features['first_half_goals'].append(game['away_first_half_score'])
            game_features['sec_half_goals'].append(game['away_second_half_score'])
            game_features['goal_kicks'].append(game['away_goal_kicks'])

        played += 1
        count += 1

    # Pulling the data for the CURRENT MATCH
    for index, cur_game in current_matches.iterrows():

        match_id = cur_game["match_id"]
        scheduled = cur_game["scheduled"]
        if team_id == cur_game['home_id']:
            is_home = True
            team_name = cur_game["home_team"]
            current_opp = cur_game['away_id']
            current_formation = cur_game['home_formation']
            opp_formation = cur_game['away_formation']

            if targets:
                # Targets
                points = cur_game['home_points']
                goals = cur_game['home_score']
                opp_goals = cur_game['away_score']

        else:

            is_home = False
            team_name = cur_game["away_team"]
            current_opp = cur_game['home_id']
            current_formation = cur_game['away_formation']
            opp_formation = cur_game['home_formation']

            if targets:
                # Targets
                points = cur_game['away_points']
                goals = cur_game['away_score']
                opp_goals = cur_game['home_score']

    for k, v in game_features.items():
        if len(v) != 0:
            game_features[k] = np.nanmean(np.array(v))
        else:
            game_features[k] = np.nan


    if stats:
        print(" ========================== ")
        print("Team Id : {} - Name : {}".format(team_id, team_name))
        print("Prev Opponent Ids : {}".format(prev_opp))
        print("FEATURES (Stats from * 3 Previous Matches)")
        print("Total Goals : {}".format(total_goals))
        print("Total Points : {}".format(total_points))
        # print("Win Points : {}".format(win))
        # print("Loss Points : {}".format(loss))
        print("Played : {}".format(played))
        print("Goal Diff : {}".format(goal_diff))
        print("Margin : {}".format(np.divide(goal_diff, played)))
        print("")

        if targets:
            # Still can weight games more on most recent games
            print("\nTARGETS (RESULTS OF CURRENT MATCH)")
            print("Points : {}".format(points))
            print("Goals : {}".format(goals))
            print("Opp_Goals : {}".format(opp_goals))

    return match_id, team_id, team_name, scheduled, int(is_home == True), total_points, \
           goals_for, goals_against, goal_diff, goal_efficiency, played, win, loss, recent_wins, recent_losses, prev_opp, \
           current_opp, points, goals, opp_goals, current_formation, opp_formation, game_features


# Assuming a team only plays once in the previous 7 days
def create_match(team_id, current_matches, match_details, round_number, stats, targets):
    """Finds the matches needed for the given week, opponents and the previous rounds"""

    previous_matches = match_details.loc[
        ((match_details['home_id'] == team_id) | (match_details['away_id'] == team_id)) &
        (match_details['round'] < round_number)]

    # Only take the previous 3 matches and sum those stats together
    previous_matches = previous_matches.iloc[-3:]

    # Find CUR_TEAM's stats
    match_id, team_id, team_name, scheduled, is_home, total_points, goals_for, goals_against, goal_diff, goal_efficiency, \
        played, win, loss, recent_wins, recent_losses, prev_opp, opp_id, points, goals, opp_goals, \
    current_formation, opp_formation, game_features = \
        calculate_stats(team_id, current_matches, previous_matches, stats, targets)

    # Calculate the OPPONENTS stats
    if stats:
        print('Current Opponent ID : {0}'.format(opp_id))

    # Find OPP_TEAM's stats
    opp_previous_matches = match_details.loc[
        ((match_details['home_id'] == opp_id) | (match_details['away_id'] == opp_id)) &
        (match_details['round'] < round_number)]

    opp_previous_matches = opp_previous_matches.iloc[-3:]

    _, opp_team_id, opp_team_name, _, opp_is_home, opp_total_points, opp_goals_for, opp_goals_against, opp_goal_diff, opp_goal_efficiency, \
    opp_played, opp_win, opp_loss, opp_recent_wins, opp_recent_losses, opp_opp, _, _, _, _, _, _, opp_game_features = calculate_stats(opp_id, current_matches, opp_previous_matches, stats, False)

    if stats:
        print('Current Opponents of Current Team : {0}'.format(prev_opp))

    prev_opp_won_total = 0
    prev_opp_lost_total = 0

    for prev_opp_id in prev_opp:
        prev_opp_previous_matches = match_details.loc[
            ((match_details['home_id'] == prev_opp_id) | (match_details['away_id'] == prev_opp_id)) &
            (match_details['round'] < round_number)]

        _, _, _, _, _, _, _, _, _, _, _, prev_opp_win, prev_opp_loss, _, _, _, _, _, _, _, _, _, \
        prev_opp_game_features = calculate_stats(prev_opp_id, current_matches, prev_opp_previous_matches, stats, False)

        prev_opp_won_total += prev_opp_win
        prev_opp_lost_total += prev_opp_loss

    opp_opp_won_total = 0
    opp_opp_lost_total = 0

    if stats:
        print('Current Opponents of Opponent : {0}'.format(opp_opp))

    # Calculate OPPONENTS of the OPPONENTS stats
    for opp_opp_id in opp_opp:

        opp_opp_previous_matches = match_details.loc[
            ((match_details['home_id'] == opp_opp_id) | (match_details['away_id'] == opp_opp_id)) &
            (match_details['round'] < round_number)]

        opp_opp_match_id, opp_opp_team_id, opp_opp_team_name, scheduled, opp_opp_is_home, opp_opp_total_points, opp_opp_goals_for, opp_opp_goals_against, opp_opp_goal_diff, opp_opp_goal_efficiency, \
        opp_opp_played, opp_opp_win, opp_opp_loss, opp_opp_recent_wins, opp_opp_recent_losses, _, _, _, _, _, _, _, opp_opp_game_features = calculate_stats(opp_opp_id, current_matches, opp_opp_previous_matches, False, False)
        opp_opp_won_total += opp_opp_win
        opp_opp_lost_total += opp_opp_loss


    if stats:
        print("\nTeam")
        print(game_features)
        print("Opponent")
        print(opp_game_features)

        print("Current Win :: {}".format(win))
        print("Current Losses :: {}".format(loss))
        print("Current Opponents Win :: {}".format(prev_opp_won_total))
        print("Current Opponents Losses :: {}".format(prev_opp_lost_total))

        print("Opp Win :: {}".format(opp_win))
        print("Opp Loss :: {}".format(opp_loss))
        print("Opp Opp Win :: {}".format(opp_opp_win))
        print("Opp Opp Loss :: {}".format(opp_opp_loss))

    current_record = np.divide(win, (win + loss))
    current_opp_record = np.divide(prev_opp_won_total, (prev_opp_won_total + prev_opp_lost_total))
    opp_sos = np.divide((2 * current_record) + current_opp_record, 3)

    opp_record = np.divide(opp_win, (opp_win+opp_loss))
    opp_opp_record = np.divide(opp_opp_won_total, (opp_opp_won_total+opp_opp_lost_total))
    sos = np.divide((2 * opp_record) + opp_opp_record, 3)

    rpi = (current_record * .25) + (sos * .75)
    opp_rpi = (opp_record * .25) + (opp_sos * .75)

    if stats:
        print("OR :: {} ".format(opp_record))
        print("OOR :: {} ".format(opp_opp_record))
        print("SOS : {}".format(sos))

        print("CR :: {} ".format(current_record))
        print("COR :: {} ".format(current_opp_record))
        print("OPP SOS : {}".format(opp_sos))

    feature = {'match_id': match_id, 'team_id': team_id, 'team_name': team_name, 'opp_id': opp_team_id,
               'opp_name': opp_team_name, 'scheduled': scheduled, 'games_played': played, 'is_home':
                   is_home, 'current_formation': current_formation, 'avg_points': np.divide(total_points, played),
               'avg_goals_for': np.divide(goals_for, played), 'avg_goals_against': np.divide(goals_against, played),
               'margin': np.divide(goal_diff, played),
               'goal_diff': goal_diff, 'goal_efficiency': goal_efficiency,
               'win_percentage': np.divide(win, (win + loss)), 'sos': sos, 'rpi': rpi,
               'opp_is_home': opp_is_home, 'opp_formation': opp_formation,
               'opp_avg_points': np.divide(opp_total_points, opp_played),
               'opp_avg_goals': np.divide(opp_goals_for, opp_played),
               'opp_margin': np.divide(opp_goal_diff, opp_played), 'opp_goal_diff': opp_goal_diff, 'opp_goal_efficiency': opp_goal_efficiency,
               'opp_win_percentage': np.divide(opp_win, (opp_win + opp_loss)), 'opp_sos': opp_sos, 'opp_rpi': opp_rpi,
               'goals': goals, 'points': points}  # 'opp_goals': opp_goals

    """ If you set the denominator to zero the result will be infinite.  Might need another way to catch this..."""
    goals_op_ratio = 0
    if opp_goals_for > 0:
        goals_op_ratio = np.divide(goals_for, float(opp_goals_for))
    else:
        goals_op_ratio = goals_for

    ratios = {'goals_op_ratio': goals_op_ratio,
              'ball_safe_op_ratio': np.divide(game_features['ball_safe'], opp_game_features['ball_safe']),
              'goal_attempts_op_ratio': np.divide(game_features['goal_attempts'], opp_game_features['goal_attempts'])}

    game_features = {'current_team': game_features, 'opp_team': opp_game_features }

    if stats:
        print("//////////////////////////////////////////////////")

    return feature, game_features, ratios





