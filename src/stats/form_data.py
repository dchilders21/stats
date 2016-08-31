from stats import match_stats
import mysql.connector
import pandas as pd
import numpy as np


def run_data():

    cnx = mysql.connector.connect(user='root', password='',
                                  host='127.0.0.1',
                                  database='mls')
    cursor = cnx.cursor(dictionary=True, buffered=True)

    match_details = pd.read_sql('SELECT * FROM home_away_coverage_2', cnx)
    query = "SELECT id FROM teams"
    cursor.execute(query)

    round_number = 26
    training_list = []

    for team in cursor:

        for i in range(2, round_number):

            print("ROUND {} :: TEAM ID {}".format(i, team["id"]))

            cur_matches = match_details.loc[
                ((match_details['home_id'] == team["id"]) | (match_details['away_id'] == team["id"])) &
                (match_details['round'] == i)]

            if not cur_matches.empty:
                for c, cur_match in cur_matches.iterrows():
                    """ Better Solution for this?  Basically pulling out a Series but the create_match function is expecting a DF
                    # have to convert it back to a DF in order to not pull the same entry if there are multiple games in the week """
                    temp = pd.DataFrame([])
                    df = temp.append(cur_match, ignore_index=True)
                    features, home_away_features, extended_features = match_stats.create_match(team["id"], df, match_details, i, False, True)

                    if features is not None:
                        for key, value in extended_features.items():
                            for k, v in value.items():
                                new_key = key + '_' + k
                                features[new_key] = v

                        for key, value in home_away_features.items():
                            for k, v in value.items():
                                new_key = key + '_' + k
                                features[new_key] = v

                    training_list.append(features)

    columns = ['match_id', 'team_id', 'team_name', 'opp_id', 'opp_name', 'scheduled', 'games_played',
               # Non-Feature Columns
               'is_home', 'avg_points', 'goals_for', 'goals_against', 'avg_goals', 'margin', 'goal_diff',
               'win_percentage', 'sos', 'opp_is_home', 'opp_avg_points', 'opp_avg_goals', 'opp_margin',
               'opp_goal_diff', 'opp_win_percentage', 'opp_opp_record',
               # Home Away Feature Columns
               'current_team_home_possession', 'current_team_away_possession', 'current_team_home_attacks', 'current_team_away_attacks', 'current_team_home_dangerous_attacks',
               'current_team_away_dangerous_attacks', 'current_team_home_yellow_card', 'current_team_away_yellow_card', 'current_team_home_corner_kicks', 'current_team_away_corner_kicks',
               'current_team_home_shots_on_target', 'current_team_away_shots_on_target', 'current_team_home_shots_total', 'current_team_away_shots_total', 'current_team_home_ball_safe',
               'current_team_away_ball_safe', 'current_team_home_played', 'current_team_away_played',
               'current_opp_home_attacks', 'current_opp_away_attacks', 'current_opp_home_dangerous_attacks',
               'current_opp_away_dangerous_attacks', 'current_opp_home_yellow_card',
               'current_opp_away_yellow_card', 'current_opp_home_corner_kicks', 'current_opp_away_corner_kicks',
               'current_opp_home_shots_on_target', 'current_opp_away_shots_on_target',
               'current_opp_home_shots_total', 'current_opp_away_shots_total', 'current_opp_home_ball_safe',
               'current_opp_away_ball_safe', 'current_opp_home_played', 'current_opp_away_played',
               # Extended Feature Columns
               'e_f_dangerous_attacks', 'e_f_shots_total', 'e_f_shots_on_target', 'e_f_ball_safe', 'e_f_possession', 'e_f_attacks',
               'opp_e_f_dangerous_attacks', 'opp_e_f_shots_total', 'opp_e_f_shots_on_target', 'opp_e_f_ball_safe', 'opp_e_f_possession', 'opp_e_f_attacks',
               'prev_opp_e_f_dangerous_attacks', 'prev_opp_e_f_shots_total', 'prev_opp_e_f_shots_on_target', 'prev_opp_e_f_ball_safe', 'prev_opp_e_f_possession', 'prev_opp_e_f_attacks',
               'opp_opp_e_f_dangerous_attacks', 'opp_opp_e_f_shots_total', 'opp_opp_e_f_shots_on_target', 'opp_opp_e_f_ball_safe', 'opp_opp_e_f_possession', 'opp_opp_e_f_attacks',
               'points']  # Target Columns - #'goals', 'opp_goals'

    data = pd.DataFrame(training_list, columns=columns)

    # Replace Nan's with the average of the columns
    # data = data.fillna(data.mean(), inplace=True)
    # Above not working for some reason
    data = data.replace(np.nan, data.mean())

    return data
