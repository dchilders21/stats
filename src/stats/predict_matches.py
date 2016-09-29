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
               'is_home', 'current_formation', 'diff_goal_for', 'diff_goal_allowed', 'diff_attacks', 'diff_dangerous_attacks',
               'diff_goal_attempts', 'diff_ball_safe',
               'goals_for', 'goals_allowed',
               'goals', 'points']  # Target Columns - #'goals', 'opp_goals'

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

    upcoming_data = pd.DataFrame(upcoming_list, columns=columns)

    return upcoming_data
