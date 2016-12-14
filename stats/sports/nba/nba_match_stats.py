import numpy as np


def calculate_stats(team_id, teams, current_game, previous_games, team_totals, stats, targets):
    """ Calculates the stats of the the current team in the current game
         and the opponent team in the current game.  Also calculates the
         previous games for the current team"""

    # Features
    win = 0
    loss = 0
    prev_opp = []
    total_points = 0
    final_score = 0
    count = 1
    played = float(0)

    game_features = {"FGM": [], "FGA": [], "3PM": [], "3PA": [], "FTM": [], "FTA": [], "OREB": [], "DREB": [], "AST": [],
        "STL": [], "BLK": [], "turnovers": [], "PF": [], "1st_qtr": [], "2nd_qtr": [], "3rd_qtr": [], "4th_qtr": [],
        "total_pts": [], "fast_break_points": [], "points_in_paint": [], "points_off_turnovers": [],
        "second_chance_points": []}

    # Targets
    points = 0

    # Organizing Data for PREVIOUS Matches
    for index, game in previous_games.iterrows():

        game_totals = team_totals.loc[team_totals['game_id'] == game.loc['id']]
        current_team_stats = game_totals.loc[game_totals['team_id'] == team_id]

        winner = 0 if game_totals.iloc[0]['total_pts'] > game_totals.iloc[1]['total_pts'] else 1

        # Home Wins and Road Losses are .8 while Road Wins and Home Losses are 1.2 / Draws remain the same
        if current_team_stats.iloc[0]['is_home'] == 1:
            if winner == 0:
                win += .8
            else:
                loss += 1.2

            prev_opp.append(game_totals.iloc[1]['team_id'])

        else:

            if winner == 1:
                win += 1.2
            else:
                loss += .8

            prev_opp.append(game_totals.iloc[0]['team_id'])

        played += 1

        for key, value in game_features.items():
            game_features[key].append(current_team_stats.iloc[0][key])

    game_id = current_game.loc['id']
    scheduled = current_game.loc['scheduled_pst']
    team_name = teams['name'].loc[teams['id'] == team_id].iloc[0]
    # this is info for the current game
    if current_game['home_id'] == team_id:
        is_home = True
        home_id = current_game.loc["home_id"]
        current_opp = current_game.loc["away_id"]

        if targets:
            # Targets
            final_score = team_totals['total_pts'].loc[(team_totals['game_id'] == game_id) & (team_totals['team_id'] == home_id)].iloc[0]


    else:

        is_home = False
        away_id = current_game.loc["away_id"]
        current_opp = current_game.loc["home_id"]

        if targets:
            # Targets
            final_score = team_totals['total_pts'].loc[(team_totals['game_id'] == game_id) & (team_totals['team_id'] == away_id)].iloc[0]

    if stats:
        print(" ========================== ")
        print("Team Id : {}".format(team_id))
        print("Prev Opponent Ids : {}".format(prev_opp))
        print("FEATURES (Stats from * 3 Previous Matches)")
        print("Total Points : {}".format(total_points))

        if targets:
            # Still can weight games more on most recent games
            print("\nTARGETS (RESULTS OF CURRENT MATCH)")
            pass

    for k, v in game_features.items():
        game_features[k] = np.sum(np.array(v))

    return game_id, team_id, team_name, scheduled, int(is_home == True), played, win, loss, prev_opp, \
           current_opp, final_score, game_features


def create_game(team_id, teams, current_game, closed_games, team_totals, stats, targets):

    """Finds the matches needed for the given week, opponents and the previous rounds"""
    previous_games = closed_games.loc[((closed_games['home_id'] == team_id) | (closed_games['away_id'] == team_id))
                                      & (closed_games['scheduled_pst'] < current_game['scheduled_pst'])]

    # Only take the previous 3 matches and sum those stats together
    previous_games = previous_games.iloc[-3:]

    # Find CUR_TEAM's stats
    game_id, team_id, team_name, scheduled, is_home, \
        played, win, loss, prev_opp, opp_id, final_score, game_features = \
        calculate_stats(team_id, teams, current_game, previous_games, team_totals, stats, targets)

    # Calculate the OPPONENTS stats
    if stats:
        print('Current Opponent ID : {0}'.format(opp_id))

    opp_previous_games = closed_games.loc[
        ((closed_games['home_id'] == opp_id) | (closed_games['away_id'] == opp_id))
            & (closed_games['scheduled_pst'] < current_game['scheduled_pst'])]

    # Only take the previous 3 matches and sum those stats together
    opp_previous_games = opp_previous_games.iloc[-3:]

    _, _, opp_team_name, _, _, played, opp_win, opp_loss, opp_opp, _, _, opp_game_features = \
        calculate_stats(opp_id, teams, current_game, opp_previous_games, team_totals, stats, targets)

    if stats:
        print('Previous Opponents of Current Team : {0}'.format(prev_opp))

    prev_opp_won_total = 0
    prev_opp_lost_total = 0

    opp_prev_opps = []

    for prev_opp_id in prev_opp:
        prev_opp_previous_matches = closed_games.loc[
            ((closed_games['home_id'] == prev_opp_id) | (closed_games['away_id'] == prev_opp_id))
            & (closed_games['scheduled_pst'] < current_game['scheduled_pst'])]

        # Only take the previous 3 matches and sum those stats together
        prev_opp_previous_matches = prev_opp_previous_matches.iloc[-3:]

        _, _, _, _, _, prev_opp_played, prev_opp_win, prev_opp_loss, opp_prev_opp, _, _, prev_opp_game_features = \
            calculate_stats(prev_opp_id, teams, current_game, prev_opp_previous_matches, team_totals, False, False)

        prev_opp_won_total += prev_opp_win
        prev_opp_lost_total += prev_opp_loss

        opp_prev_opps += opp_prev_opp


    if stats:
        print('Previous Opponents of Opponent : {0}'.format(opp_opp))

    opp_opp_won_total = 0
    opp_opp_lost_total = 0

    opp_opp_opps = []

    # Calculate OPPONENTS of the OPPONENTS stats
    for opp_opp_id in opp_opp:
        opp_opp_previous_matches = closed_games.loc[
            ((closed_games['home_id'] == opp_opp_id) | (closed_games['away_id'] == opp_opp_id))
            & (closed_games['scheduled_pst'] < current_game['scheduled_pst'])]

        # Only take the previous 3 matches and sum those stats together
        opp_opp_previous_matches = opp_opp_previous_matches.iloc[-3:]

        _, _, _, _, _, opp_opp_played, opp_opp_win, opp_opp_loss, opp_opp_opp, _, _, opp_opp_game_features = \
            calculate_stats(opp_opp_id, teams, current_game, opp_opp_previous_matches, team_totals, False, False)

        opp_opp_won_total += opp_opp_win
        opp_opp_lost_total += opp_opp_loss

        opp_opp_opps += opp_opp_opp

    if stats:
        print('Opponents of Previous Opponents : {0}'.format(opp_prev_opps))

    opp_prev_opp_won_total = 0
    opp_prev_opp_lost_total = 0

    # Calculate OPPONENTS of the PREVIOUS OPPONENTS stats
    for opp_prev_opp_id in opp_prev_opps:

        opp_prev_opp_previous_matches = closed_games.loc[
            ((closed_games['home_id'] == opp_prev_opp_id) | (closed_games['away_id'] == opp_prev_opp_id))
            & (closed_games['scheduled_pst'] < current_game['scheduled_pst'])]

        # Only take the previous 3 matches and sum those stats together
        opp_prev_opp_previous_matches = opp_prev_opp_previous_matches.iloc[-3:]

        _, _, _, _, _, opp_prev_opp_played, opp_prev_opp_win, opp_prev_opp_loss, _, _, _, opp_prev_opp_game_features = \
            calculate_stats(opp_prev_opp_id, teams, current_game, opp_prev_opp_previous_matches, team_totals, False, False)

        opp_prev_opp_won_total += opp_prev_opp_win
        opp_prev_opp_lost_total += opp_prev_opp_loss

    if stats:
        print('Opponents of Opponents Previous Opponents : {0}'.format(opp_opp_opps))

    opp_opp_opp_won_total = 0
    opp_opp_opp_lost_total = 0

    # Calculate OPPONENTS of the OPPONENTS' OPPONENTS' stats
    for opp_opp_opp_id in opp_opp_opps:
        opp_opp_opp_previous_matches = closed_games.loc[
            ((closed_games['home_id'] == opp_opp_opp_id) | (closed_games['away_id'] == opp_opp_opp_id))
            & (closed_games['scheduled_pst'] < current_game['scheduled_pst'])]

        _, _, _, _, _, opp_opp_opp_played, opp_opp_opp_win, opp_opp_opp_loss, _, _, _, opp_opp_opp_game_features = \
            calculate_stats(opp_opp_opp_id, teams, current_game, opp_opp_opp_previous_matches, team_totals, False, False)

        opp_opp_opp_won_total += opp_opp_opp_win
        opp_opp_opp_lost_total += opp_opp_opp_loss

    """ //////////////////////////////////////////////////////////////////////////////////////////////////// """
    """ Collected all the information from relevant matches.  Now send through all what we have. """
    """ //////////////////////////////////////////////////////////////////////////////////////////////////// """
    # Only calculate SOS + RPI here since they include previous matches
    current_record = np.divide(win, (win + loss))
    opp_record = np.divide(opp_win, (opp_win + opp_loss))
    prev_opp_record = np.divide(prev_opp_win, (prev_opp_win + prev_opp_loss))
    opp_prev_opp_record = np.divide(opp_prev_opp_won_total, (opp_prev_opp_won_total + opp_prev_opp_lost_total))
    sos = np.divide((2 * prev_opp_record) + opp_prev_opp_record, 3)
    rpi = (current_record * .25) + (sos * .75)

    feature = {'game_id': game_id, 'team_id': team_id, 'team_name': team_name, 'opp_id': opp_id,
               'opp_name': opp_team_name, 'scheduled_pst': scheduled, 'games_played': played,
               'is_home': is_home, 'current_record': current_record, 'rpi': rpi,
               'opp_record': opp_record, 'final_score': final_score}

    game_features = {'current_team': game_features, 'opp_team': opp_game_features }

    if stats:
        print("//////////////////////////////////////////////////")

    return feature, game_features





