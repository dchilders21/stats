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

    # Extended Features
    home_possession = []
    away_possession = []
    home_attacks = []
    away_attacks = []
    home_dangerous_attacks = []
    away_dangerous_attacks = []
    home_fouls = []
    away_fouls = []
    home_yellow_card = []
    away_yellow_card = []
    home_corner_kicks = []
    away_corner_kicks = []
    home_shots_on_target = []
    away_shots_on_target = []
    home_shots_total = []
    away_shots_total = []
    # home_saves = 0
    # away_saves = 0
    home_ball_safe = []
    away_ball_safe = []
    # opp_SOS

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

            # Extended Home Features
            home_possession.append(game['home_possession'])
            home_attacks.append(game['home_attacks'])
            home_dangerous_attacks.append(game['home_dangerous_attacks'])
            home_fouls.append(game['home_fouls'])
            home_yellow_card.append(game['home_yellow_card'])
            home_corner_kicks.append(game['home_corner_kicks'])
            home_shots_on_target.append(game['home_shots_on_target'])
            home_shots_total.append(game['home_shots_total'])
            # home_saves.append(game['home_saves'])
            home_ball_safe.append(game['home_ball_safe'])


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

            # Extended Away Features
            away_possession.append(game['away_possession'])
            away_attacks.append(game['away_attacks'])
            away_dangerous_attacks.append(game['away_dangerous_attacks'])
            away_fouls.append(game['away_fouls'])
            away_yellow_card.append(game['away_yellow_card'])
            away_corner_kicks.append(game['away_corner_kicks'])
            away_shots_on_target.append(game['away_shots_on_target'])
            away_shots_total.append(game['away_shots_total'])
            # away_saves.append(game['away_saves'])
            away_ball_safe.append(game['away_ball_safe'])

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

    home_possession = np.array(home_possession)
    away_possession = np.array(away_possession)
    home_attacks = np.array(home_attacks)
    away_attacks = np.array(away_attacks)
    home_fouls = np.array(home_fouls)
    away_fouls = np.array(away_fouls)
    home_yellow_card = np.array(home_yellow_card)
    away_yellow_card = np.array(away_yellow_card)
    home_corner_kicks = np.array(home_corner_kicks)
    away_corner_kicks = np.array(away_corner_kicks)
    home_shots_on_target = np.array(home_shots_on_target)
    away_shots_on_target = np.array(away_shots_on_target)
    home_ball_safe = np.array(home_ball_safe)
    away_ball_safe = np.array(away_ball_safe)
    home_shots_total = np.array(home_shots_total)
    away_shots_total = np.array(away_shots_total)

    if home_possession.size != 0:
        home_possession = np.nanmean(home_possession)
    else:
        home_possession = 0

    if away_possession.size != 0:
        away_possession = np.nanmean(away_possession)
    else:
        away_possession = 0

    if home_attacks.size > 0:
        home_attacks = np.nanmean(home_attacks)
        if np.isnan(home_attacks):
            home_attacks = 0
    else:
        home_attacks = 0

    if away_attacks.size > 0:
        away_attacks = np.nanmean(away_attacks)
        if np.isnan(away_attacks):
            away_attacks = 0
    else:
        away_attacks = 0

    if home_fouls.size != 0:
        home_fouls = np.nanmean(home_fouls)
    else:
        home_fouls = 0

    if away_fouls.size != 0:
        away_fouls = np.nanmean(away_fouls)
    else:
        away_fouls = 0

    if home_yellow_card.size != 0:
        home_yellow_card = np.nanmean(home_yellow_card)
    else:
        home_yellow_card = 0

    if away_yellow_card.size != 0:
        away_yellow_card = np.nanmean(away_yellow_card)
    else:
        away_yellow_card = 0

    if home_corner_kicks.size != 0:
        home_corner_kicks = np.nanmean(home_corner_kicks)
    else:
        home_corner_kicks = 0

    if away_corner_kicks.size != 0:
        away_corner_kicks = np.nanmean(away_corner_kicks)
    else:
        away_corner_kicks = 0

    if home_shots_on_target.size != 0:
        home_shots_on_target = np.nanmean(home_shots_on_target)
    else:
        home_shots_on_target = 0

    if away_shots_on_target.size != 0:
        away_shots_on_target = np.nanmean(away_shots_on_target)
    else:
        away_shots_on_target = 0

    if home_ball_safe.size != 0:
        home_ball_safe = np.nanmean(home_ball_safe)
    else:
        home_ball_safe = 0

    if away_ball_safe.size != 0:
        away_ball_safe = np.nanmean(away_ball_safe)
    else:
        away_ball_safe = 0

    if home_shots_total.size != 0:
        home_shots_total = np.nanmean(home_shots_total)
    else:
        home_shots_total = 0

    if away_shots_total.size != 0:
        away_shots_total = np.nanmean(away_shots_total)
    else:
        away_shots_total = 0

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
        print("EXTENDED FEATURES")
        print("Home Possession Avg : {}".format(np.mean(home_possession)))
        print("Away Possession Avg : {}".format(np.mean(away_possession)))
        print("Home Attacks Avg : {}".format(np.mean(home_attacks)))
        print("Away Attacks Avg : {}".format(np.mean(away_attacks)))
        print("Home Fouls Avg : {}".format(np.mean(home_fouls)))
        print("Away Fouls Avg : {}".format(np.mean(away_fouls)))
        print("Home Yellow Cards Avg : {}".format(np.mean(home_yellow_card)))
        print("Away Yellow Cards Avg : {}".format(np.mean(away_yellow_card)))
        print("Home Corners Avg : {}".format(np.mean(home_corner_kicks)))
        print("Away Corners Avg : {}".format(np.mean(away_corner_kicks)))
        print("Home Shots On Target Avg : {}".format(np.mean(home_shots_on_target)))
        print("Away Shots On Target Avg : {}".format(np.mean(away_shots_on_target)))
        # print("Home Saves Avg : {}".format(np.float64(home_saves) / home_played))
        # print("Away Saves Avg : {}".format(np.float64(away_saves) / away_played))
        print("Home Ball Safe Avg : {}".format(np.mean(home_ball_safe)))
        print("Away Ball Safe Avg : {}".format(np.mean(away_ball_safe)))
        print("Home Goal Attempts Avg : {}".format(np.mean(home_shots_total)))
        print("Away Goal Attempts Avg : {}".format(np.mean(away_shots_total)))

        # Still can weight games more on most recent games

        print("\nTARGETS (RESULTS OF CURRENT MATCH)")
        print("Points : {}".format(points))
        print("Goals : {}".format(goals))
        print("Opp_Goals : {}".format(opp_goals))

    return match_id, team_id, team_name, scheduled, int(is_home == True), total_points, total_goals, \
           goals_for, goals_against, goal_diff, played, win, loss, recent_wins, recent_losses, prev_opp, \
           current_opp, points, goals, opp_goals, \
           home_possession, away_possession, home_attacks, away_attacks, home_fouls, away_fouls, \
           home_yellow_card, away_yellow_card, home_corner_kicks, away_corner_kicks, \
           home_shots_on_target, away_shots_on_target, home_ball_safe, away_ball_safe, \
           home_shots_total, away_shots_total


# Assuming a team only plays once in the previous 7 days
def create_match(team_id, current_matches, match_details, round_number, stats, targets):
    """Finds the matches needed for the given week, opponents and the previous rounds"""
    print(round_number)
    print(" ++++++++++++ ")
    previous_matches = match_details.loc[
        ((match_details['home_id'] == team_id) | (match_details['away_id'] == team_id)) &
        (match_details['round'] < round_number)]

    # For this Match of the the week, calculate the 'Chosen' teams STATS so far in the season
    match_id, team_id, team_name, scheduled, is_home, total_points, total_goals, goals_for, goals_against, goal_diff, played, win, loss, recent_wins, recent_losses, _, opp_id, points, goals, opp_goals, home_possession, away_possession, home_attacks, away_attacks, home_fouls, away_fouls, home_yellow_card, away_yellow_card, home_corner_kicks, away_corner_kicks, home_shots_on_target, away_shots_on_target, home_ball_safe, away_ball_safe, home_shots_total, away_shots_total = calculate_stats(team_id, current_matches, previous_matches, stats, targets)
    print("")

    # Calculate the Opponents STATS
    print('Current Opponent ID : {0}'.format(opp_id))

    opp_previous_matches = match_details.loc[
        ((match_details['home_id'] == opp_id) | (match_details['away_id'] == opp_id)) &
        (match_details['round'] < round_number)]


    opp_match_id, opp_team_id, opp_team_name, scheduled, opp_is_home, opp_total_points, opp_total_goals, opp_goals_for, opp_goals_against, opp_goal_diff, \
    opp_played, opp_win, opp_loss, opp_recent_wins, opp_recent_losses, opp_opp, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _ = calculate_stats(opp_id, current_matches, opp_previous_matches, stats, targets)

    print('Current Opponents of Opponent ID : {0}'.format(opp_opp))

    # print('\nOpp Won {0} : Opp Lost {1} : Opp Recent Wins {2} : Opp Recent Losses {3}'.format(
        # opp_win, opp_loss, opp_recent_wins, opp_recent_wins))

    opp_opp_won_total = 0
    opp_opp_lost_total = 0

    # Calculate Opponents of the Opponents STATS
    for opp_opp_id in opp_opp:

        opp_opp_previous_matches = match_details.loc[
            ((match_details['home_id'] == opp_opp_id) | (match_details['away_id'] == opp_opp_id)) &
            (match_details['round'] < round_number)]

        opp_opp_match_id, opp_opp_team_id, opp_opp_team_name, scheduled, opp_opp_is_home, opp_opp_total_points, opp_opp_total_goals, opp_opp_goals_for, opp_opp_goals_against, opp_opp_goal_diff, \
        opp_opp_played, opp_opp_win, opp_opp_loss, opp_opp_recent_wins, opp_opp_recent_losses, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _ = calculate_stats(opp_opp_id, current_matches, opp_opp_previous_matches, False, targets)
        opp_opp_won_total += opp_opp_win
        opp_opp_lost_total += opp_opp_loss

    # print('Opp Opp Won {0} : Opp Opp Lost {1} \n'.format(opp_opp_won_total, opp_opp_lost_total))
    feature = {'match_id': match_id, 'team_id': team_id, 'team_name': team_name, 'opp_id': opp_team_id, 'opp_name': opp_team_name, 'scheduled': scheduled, 'games_played': played, 'is_home':
                is_home, 'avg_points': np.divide(total_points, played), 'goals_for': goals_for, 'goals_against': goals_against, 'avg_goals': np.divide(total_goals, played), 'margin': np.divide(goal_diff, played),
                'goal_diff': goal_diff, 'win_percentage': np.divide(win, (win+loss)), 'sos': (2*np.divide(opp_win, (opp_win+opp_loss))) + np.divide(opp_opp_won_total, (opp_opp_won_total+opp_opp_lost_total))/3,
                'opp_is_home': opp_is_home, 'opp_avg_points': np.divide(opp_total_points, opp_played), 'opp_avg_goals': np.divide(opp_total_goals, opp_played),
                'opp_margin': np.divide(opp_goal_diff, opp_played), 'opp_goal_diff': opp_goal_diff,
                'opp_win_percentage': np.divide(opp_win, (opp_win+opp_loss)), 'opp_opp_record': np.divide(opp_opp_win, (opp_opp_win+opp_opp_loss)), 'home_possession': home_possession, 'away_possession': away_possession, \
                'home_attacks': home_attacks, 'away_attacks': away_attacks, 'home_fouls': home_fouls, 'away_fouls': away_fouls, 'home_yellow_card': home_yellow_card, \
                'away_yellow_card': away_yellow_card, 'home_corner_kicks': home_corner_kicks, 'away_corner_kicks': away_corner_kicks, 'home_shots_on_target': home_shots_on_target, 'away_shots_on_target': away_shots_on_target, \
                'home_ball_safe': home_ball_safe, 'away_ball_safe': away_ball_safe, 'home_shots_total': home_shots_total, 'away_shots_total': away_shots_total,
                'points': points } # 'goals': goals, 'opp_goals': opp_goals

    print("//////////////////////////////////////////////////")

    return feature





