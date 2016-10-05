def get_upcoming_matches():
    import mysql.connector
    import pandas as pd
    from stats import match_stats, model_libs
    cnx = mysql.connector.connect(user='root', password='',
                                  host='127.0.0.1',
                                  database='mls')

    leagues = model_libs.get_leagues_rounds()

    upcoming_matches = pd.DataFrame([])

    for key in leagues:
        table = str('matches_' + key)
        round_number = leagues[key]
        query = str("SELECT " + table + ".id as 'match_id', " + table + ".scheduled, " + table + ".home_id, " + table + ".away_id, teams1.full_name AS 'home_team', teams2.full_name AS 'away_team' FROM " + table + " LEFT JOIN teams teams1 ON " + table + ".home_id = teams1.id LEFT JOIN teams teams2 ON " + table + ".away_id = teams2.id WHERE status = 'scheduled' AND round_number = '" + str(round_number) + "'")
        upcoming_matches = upcoming_matches.append(pd.read_sql(query, cnx))

    match_details = pd.read_sql('SELECT * FROM home_away_coverage_all', cnx)

    return upcoming_matches, match_details


def predictions(upcoming_matches):

    import mysql.connector
    import pandas as pd
    from stats import match_stats, model_libs, form_data

    cnx = mysql.connector.connect(user='root', password='',
                                  host='127.0.0.1',
                                  database='mls')

    cursor = cnx.cursor(dictionary=True, buffered=True)

    columns = ['match_id', 'team_id', 'team_name', 'opp_id', 'opp_name', 'scheduled', 'round', 'games_played',
               # Non-Feature Columns
               'is_home', 'current_formation', 'current_record', 'opp_record', 'goals_for', 'opp_goals_for',
               'goals_against', 'opp_goals_against', 'rpi',
               'goals', 'points']

    stats_columns = ['current_team_possession', 'current_team_yellow_cards', 'current_team_goal_attempts',
             'current_team_dangerous_attacks', 'current_team_sec_half_goals', 'current_team_saves',
             'current_team_corner_kicks', 'current_team_ball_safe', 'current_team_first_half_goals',
             'current_team_shots_on_target', 'current_team_attacks', 'current_team_goal_attempts_allowed',
             'current_team_goal_kicks', 'current_team_shots_total',
             'opp_team_possession', 'opp_team_yellow_cards', 'opp_team_goal_attempts',
             'opp_team_dangerous_attacks', 'opp_team_sec_half_goals', 'opp_team_saves',
             'opp_team_corner_kicks', 'opp_team_ball_safe', 'opp_team_first_half_goals',
             'opp_team_shots_on_target', 'opp_team_attacks', 'opp_team_goal_attempts_allowed',
             'opp_team_goal_kicks', 'opp_team_shots_total']

    query = "SELECT id, country_code FROM teams"
    cursor.execute(query)

    upcoming_list = []

    match_details = form_data.get_coverage()

    for team in cursor:

        round_number = model_libs.get_team_round(team["country_code"])

        upcoming_team_matches = upcoming_matches.loc[
                    ((upcoming_matches['home_id'] == team["id"]) | (upcoming_matches['away_id'] == team["id"]))]

        if not upcoming_team_matches.empty:

            for i, upcoming_team_match in upcoming_team_matches.iterrows():
                df = pd.DataFrame([]).append(upcoming_team_match, ignore_index=True)
                features, game_features = match_stats.create_match(team["id"], df, match_details, round_number, False, False)

                if features is not None:
                    for key, value in game_features.items():
                        for k, v in value.items():
                            new_key = key + '_' + k
                            features[new_key] = v

                upcoming_list.append(features)

    upcoming_data = pd.DataFrame(upcoming_list, columns=columns + stats_columns)

    return upcoming_data
