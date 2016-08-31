def get_upcoming_matches():
    import mysql.connector
    import pandas as pd

    cnx = mysql.connector.connect(user='root', password='',
                                  host='127.0.0.1',
                                  database='mls')

    upcoming_matches = pd.read_sql(
        "SELECT matches.id as 'match_id', matches.scheduled, matches.home_id, matches.away_id, teams1.full_name AS 'home_team', teams2.full_name AS 'away_team' FROM matches LEFT JOIN teams teams1 ON matches.home_id = teams1.id LEFT JOIN teams teams2 ON matches.away_id = teams2.id WHERE status = 'scheduled'",
        cnx)

    match_details = pd.read_sql('SELECT * FROM home_away_coverage_2', cnx)

    return upcoming_matches, match_details


def predictions(upcoming_matches, match_details, model):

    import mysql.connector
    import pandas as pd
    from stats import match_stats, model_libs

    cnx = mysql.connector.connect(user='root', password='',
                                  host='127.0.0.1',
                                  database='mls')
    cursor = cnx.cursor(dictionary=True, buffered=True)

    round_number = 26

    columns = ['match_id', 'team_id', 'team_name', 'opp_id', 'opp_name', 'scheduled', 'games_played',
               # Non-Feature Columns
               'is_home', 'avg_points', 'goals_for', 'goals_against', 'avg_goals', 'margin', 'goal_diff',
               'win_percentage', 'sos', 'opp_is_home', 'opp_avg_points', 'opp_avg_goals', 'opp_margin',
               'opp_goal_diff', 'opp_win_percentage', 'opp_opp_record',
               # Home Away Feature Columns
               'current_team_home_possession', 'current_team_away_possession', 'current_team_home_attacks',
               'current_team_away_attacks', 'current_team_home_dangerous_attacks',
               'current_team_away_dangerous_attacks', 'current_team_home_yellow_card', 'current_team_away_yellow_card',
               'current_team_home_corner_kicks', 'current_team_away_corner_kicks',
               'current_team_home_shots_on_target', 'current_team_away_shots_on_target',
               'current_team_home_shots_total', 'current_team_away_shots_total', 'current_team_home_ball_safe',
               'current_team_away_ball_safe', 'current_team_home_played', 'current_team_away_played',
               'current_team_home_possession', 'current_team_away_possession', 'current_team_home_attacks',
               'current_opp_away_attacks', 'current_opp_home_dangerous_attacks',
               'current_opp_away_dangerous_attacks', 'current_opp_home_yellow_card',
               'current_opp_away_yellow_card', 'current_opp_home_corner_kicks', 'current_opp_away_corner_kicks',
               'current_opp_home_shots_on_target', 'current_opp_away_shots_on_target',
               'current_opp_home_shots_total', 'current_opp_away_shots_total', 'current_opp_home_ball_safe',
               'current_opp_away_ball_safe', 'current_opp_home_played', 'current_opp_away_played',
               # Extended Feature Columns
               'e_f_dangerous_attacks', 'e_f_shots_total', 'e_f_shots_on_target', 'e_f_ball_safe', 'e_f_possession',
               'e_f_attacks',
               'opp_e_f_dangerous_attacks', 'opp_e_f_shots_total', 'opp_e_f_shots_on_target', 'opp_e_f_ball_safe',
               'opp_e_f_possession', 'opp_e_f_attacks',
               'prev_opp_e_f_dangerous_attacks', 'prev_opp_e_f_shots_total', 'prev_opp_e_f_shots_on_target',
               'prev_opp_e_f_ball_safe', 'prev_opp_e_f_possession', 'prev_opp_e_f_attacks',
               'opp_opp_e_f_dangerous_attacks', 'opp_opp_e_f_shots_total', 'opp_opp_e_f_shots_on_target',
               'opp_opp_e_f_ball_safe', 'opp_opp_e_f_possession', 'opp_opp_e_f_attacks',
               'points']  # Target Columns - #'goals', 'opp_goals'

    target_col = 'points'
    ignore_cols = ['match_id', 'team_id', 'team_name', 'opp_id', 'opp_name', 'scheduled']

    upcoming_list = []
    query = "SELECT id FROM teams"
    cursor.execute(query)

    for team in cursor:
        upcoming_team_matches = upcoming_matches.loc[
                    ((upcoming_matches['home_id'] == team["id"]) | (upcoming_matches['away_id'] == team["id"]))]

        if not upcoming_team_matches.empty:
            for i, upcoming_team_match in upcoming_team_matches.iterrows():
                #print(upcoming_team_match)
                temp = pd.DataFrame([])
                df = temp.append(upcoming_team_match, ignore_index=True)
                features, home_away_features, extended_features = match_stats.create_match(team["id"], df, match_details, round_number, False, False)

                if features is not None:

                    if features is not None:
                        for key, value in extended_features.items():
                            for k, v in value.items():
                                new_key = key + '_' + k
                                features[new_key] = v

                        for key, value in home_away_features.items():
                            for k, v in value.items():
                                new_key = key + '_' + k
                                features[new_key] = v

                    upcoming_list.append(features)

    upcoming_data = pd.DataFrame(upcoming_list, columns=columns)
    ud = model_libs._clone_and_drop(upcoming_data, ignore_cols)
    (ud_y, ud_X) = model_libs._extract_target(ud, target_col)
    results = model.predict(ud_X)

    return results, upcoming_data
