from stats import match_stats
import mysql.connector
import pandas as pd
import numpy as np
from stats import model_libs


def get_power_rankings(teams, rd):

    match_details = get_coverage()
    power_rankings = pd.DataFrame()

    for i, team in teams.iterrows():
        cur_match = match_details.loc[
            ((match_details['home_id'] == team["id"]) | (match_details['away_id'] == team["id"])) &
            (match_details['round'] == rd)]

        ''' If current team not playing this round simply go to the next round '''
        if cur_match.empty:
            cur_match = match_details.loc[
                ((match_details['home_id'] == team["id"]) | (match_details['away_id'] == team["id"])) &
                (match_details['round'] == rd + 1)]

        df = pd.DataFrame([]).append(cur_match, ignore_index=True)

        features, _ = match_stats.create_match(team["id"], df, match_details, rd, False, False)
        sos = features["sos"]
        win_percentage = features["win_percentage"]
        rpi = (win_percentage * .25) + (sos * .75)
        s = pd.Series([team["id"], features["team_name"], rpi])
        power_rankings = power_rankings.append(s, ignore_index=True)
        power_rankings = power_rankings.sort_values(2, ascending=False)

    return power_rankings


def get_rankings(teams, rd, side_of_ball):

    match_details = get_coverage()
    rankings = pd.DataFrame()
    print('Rankings :: {}'.format(side_of_ball))
    for i, team in teams.iterrows():
        cur_match = match_details.loc[
            ((match_details['home_id'] == team["id"]) | (match_details['away_id'] == team["id"])) &
            (match_details['round'] == rd)]

        ''' If current team not playing this round simply go to the next round '''
        while cur_match.empty:
            rd += 1
            cur_match = match_details.loc[
                ((match_details['home_id'] == team["id"]) | (match_details['away_id'] == team["id"])) &
                (match_details['round'] == rd)]

        df = pd.DataFrame([]).append(cur_match, ignore_index=True)

        features, game_features = match_stats.create_match(team["id"], df, match_details, rd, False, False)

        if side_of_ball == "defensive":

            if np.isnan(game_features['current_team']['goal_attempts_allowed']) or game_features['current_team'][
                    'goal_attempts_allowed'] == 0:

                current_previous_matches = match_details.loc[
                    ((match_details['home_id'] == team["id"]) | (match_details['away_id'] == team["id"])) &
                    (match_details['round'] < rd)]

                season_goal_attempts_allowed = []

                for c, match in current_previous_matches.iterrows():
                    if team["id"] == match['home_id']:
                        season_goal_attempts_allowed.append(match["away_goal_attempts"])
                    else:
                        season_goal_attempts_allowed.append(match["home_goal_attempts"])

                goal_attempts_allowed = np.nanmean(np.array(season_goal_attempts_allowed))

            else:

                goal_attempts_allowed = game_features['current_team']['goal_attempts_allowed']

            goals_allowed_avg = np.divide(features['goals_allowed'], features['games_played'])

            defensive_rank = (goal_attempts_allowed * .30) + (goals_allowed_avg * .70)

            s = pd.Series([team["id"], features["team_name"], defensive_rank])
            rankings = rankings.append(s, ignore_index=True)
            rankings = rankings.sort_values(2, ascending=True)

        elif side_of_ball == "offensive":

            if np.isnan(game_features['current_team']['goal_attempts']) or game_features['current_team']['goal_attempts'] == 0:

                current_previous_matches = match_details.loc[
                    ((match_details['home_id'] == team["id"]) | (match_details['away_id'] == team["id"])) &
                    (match_details['round'] < rd)]

                season_goal_attempts = []

                for c, match in current_previous_matches.iterrows():
                    if team["id"] == match['home_id']:
                        season_goal_attempts.append(match["home_goal_attempts"])
                    else:
                        season_goal_attempts.append(match["away_goal_attempts"])

                goal_attempts = np.nanmean(np.array(season_goal_attempts))

            else:

                goal_attempts = game_features['current_team']['goal_attempts']

            goals_for_avg = np.divide(features['goals_for'], features['games_played'])

            offensive_rank = (goal_attempts * .30) + (goals_for_avg * .70)

            s = pd.Series([team["id"], features["team_name"], offensive_rank])
            rankings = rankings.append(s, ignore_index=True)
            rankings = rankings.sort_values(2, ascending=False)

    return rankings


def get_coverage():
    cnx = mysql.connector.connect(user='root', password='',
                                  host='127.0.0.1',
                                  database='mls')

    match_details = pd.read_sql('SELECT * FROM home_away_coverage_all', cnx)

    return match_details


def get_columns():

    columns = ['match_id', 'team_id', 'team_name', 'opp_id', 'opp_name', 'scheduled', 'round', 'games_played',
               # Non-Feature Columns
               'is_home', 'current_formation', 'goals_for', 'goals_allowed', 'opp_goals_allowed', 'goal_efficiency', 'opp_defensive_goal_efficiency',
               'ratio_of_attacks', 'opp_ratio_of_attacks', 'ratio_ball_safe_to_dangerous_attacks', 'opp_ratio_ball_safe_to_dangerous_attacks',
               'goals', 'points']  # Target Columns - #'goals', 'opp_goals'

    return columns


def get_teams():
    cnx = mysql.connector.connect(user='root', password='',
                                  host='127.0.0.1',
                                  database='mls')

    teams = pd.read_sql('SELECT id, country_code, full_name FROM teams', cnx)

    return teams


def create_match(team_id, current_matches, match_details, round_number):

    print("ROUND {} :: TEAM ID {}".format(round_number, team_id))

    training_list = []

    for c, current_match in current_matches.iterrows():
        df = pd.DataFrame([]).append(current_match, ignore_index=True)
        features, game_features = match_stats.create_match(team_id, df, match_details, round_number, False, False)

        if features is not None:
            for key, value in game_features.items():
                for k, v in value.items():
                    new_key = key + '_' + k
                    features[new_key] = v

        training_list.append(features)

    return training_list


def run_data():

    cnx = mysql.connector.connect(user='root', password='',
                                  host='127.0.0.1',
                                  database='mls')
    cursor = cnx.cursor(dictionary=True, buffered=True)

    match_details = get_coverage()

    query = "SELECT id, country_code FROM teams"
    cursor.execute(query)

    training_list = []

    for team in cursor:

        round_number = model_libs.get_team_round(team["country_code"])

        for i in range(4, round_number+1):

            cur_matches = match_details.loc[
                ((match_details['home_id'] == team["id"]) | (match_details['away_id'] == team["id"])) &
                (match_details['round'] == i)]

            if not cur_matches.empty:

                print("ROUND {} :: TEAM ID {}".format(i, team["id"]))

                for c, cur_match in cur_matches.iterrows():
                    df = pd.DataFrame([]).append(cur_match, ignore_index=True)
                    features, game_features = match_stats.create_match(team["id"], df, match_details, i, False, True)

                    if features is not None:
                        for key, value in game_features.items():
                            for k, v in value.items():
                                new_key = key + '_' + k
                                features[new_key] = v

                    training_list.append(features)

    columns = get_columns()
    data = pd.DataFrame(training_list, columns=columns)

    # Replace NaN's with the average of the columns
    # data = data.fillna(data.mean(), inplace=True)
    # Above not working for some reason
    data = data.replace(np.nan, data.mean())

    return data
