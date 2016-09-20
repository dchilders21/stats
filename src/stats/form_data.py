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

        features, _, _ = match_stats.create_match(team["id"], df, match_details, rd, False, False)
        sos = features["sos"]
        win_percentage = features["win_percentage"]
        rpi = (win_percentage * .25) + (sos * .75)
        s = pd.Series([team["id"], features["team_name"], rpi])
        power_rankings = power_rankings.append(s, ignore_index=True)
        power_rankings = power_rankings.sort_values(2, ascending=False)

    return power_rankings


def get_coverage():
    cnx = mysql.connector.connect(user='root', password='',
                                  host='127.0.0.1',
                                  database='mls')

    match_details = pd.read_sql('SELECT * FROM home_away_coverage_all', cnx)

    return match_details


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

        for i in range(4, round_number):

            cur_matches = match_details.loc[
                ((match_details['home_id'] == team["id"]) | (match_details['away_id'] == team["id"])) &
                (match_details['round'] == i)]

            """ Holding out on Bundesliga since they don't have enough rounds yet - minimum is 4"""
            if 61 > team["id"] or team["id"] > 80:

                if not cur_matches.empty:

                    print("ROUND {} :: TEAM ID {}".format(i, team["id"]))

                    for c, cur_match in cur_matches.iterrows():
                        df = pd.DataFrame([]).append(cur_match, ignore_index=True)
                        features, game_features, ratios = match_stats.create_match(team["id"], df, match_details, i, False, True)

                        if features is not None:
                            for key, value in game_features.items():
                                for k, v in value.items():
                                    new_key = key + '_' + k
                                    features[new_key] = v

                        for key, value in ratios.items():
                            features[key] = value

                        training_list.append(features)

    columns = ['match_id', 'team_id', 'team_name', 'opp_id', 'opp_name', 'scheduled', 'round', 'games_played',
               # Non-Feature Columns
               'is_home', 'current_formation', 'avg_points', 'avg_goals_for', 'avg_goals_against', 'margin', 'goal_diff',
               'goal_efficiency', 'win_percentage', 'sos', 'rpi', 'opp_is_home', 'opp_formation', 'opp_avg_points', 'opp_avg_goals', 'opp_margin',
               'opp_goal_diff', 'opp_goal_efficiency', 'opp_win_percentage', 'opp_sos', 'opp_rpi',
               # Ratios
               'goals_op_ratio', 'ball_safe_op_ratio', 'goal_attempts_op_ratio',
               # Game Feature Columns
               'current_team_possession', 'current_team_attacks',
               'current_team_dangerous_attacks', 'current_team_yellow_cards',
               'current_team_corner_kicks', 'current_team_shots_on_target', 'current_team_shots_total',
               'current_team_ball_safe', 'current_team_goal_attempts',
               'current_team_saves', 'current_team_first_half_goals',
               'current_team_sec_half_goals', 'current_team_goal_kicks',
               'opp_team_possession', 'opp_team_attacks', 'opp_team_dangerous_attacks', 'opp_team_yellow_cards',
               'opp_team_corner_kicks', 'opp_team_shots_on_target', 'opp_team_shots_total',
               'opp_team_ball_safe', 'opp_team_goal_attempts', 'opp_team_saves', 'opp_team_first_half_goals',
               'opp_team_sec_half_goals', 'opp_team_goal_kicks',
               'goals', 'points']  # Target Columns - #'goals', 'opp_goals'

    data = pd.DataFrame(training_list, columns=columns)

    # Replace NaN's with the average of the columns
    # data = data.fillna(data.mean(), inplace=True)
    # Above not working for some reason
    data = data.replace(np.nan, data.mean())

    return data
