from stats import match_stats
import mysql.connector
import pandas as pd
import numpy as np
from stats import model_libs, predict_matches
import settings


def rank_teams(teams, rd, side_of_ball, upcoming):

    upcoming_matches, match_details = predict_matches.get_upcoming_matches()
    rankings = pd.DataFrame()
    print('Rankings :: {}'.format(side_of_ball))

    for i, team in teams.iterrows():
        cur_match = match_details.loc[
            ((match_details['home_id'] == team["id"]) | (match_details['away_id'] == team["id"])) &
            (match_details['round'] == rd)]

        ''' If current team not playing this round simply go to the next round '''
        while cur_match.empty:
            cur_match = match_details.loc[
                ((match_details['home_id'] == team["id"]) | (match_details['away_id'] == team["id"])) &
                (match_details['round'] == rd + 1)]

            if upcoming:
                    cur_match = upcoming_matches.loc[
                        ((upcoming_matches['home_id'] == team["id"]) | (upcoming_matches['away_id'] == team["id"]))]

        df = pd.DataFrame([]).append(cur_match, ignore_index=True)

        features, game_features = match_stats.create_match(team["id"], df, match_details, rd, False, False)

        if side_of_ball == "defensive":

            current_team_goal_attempts = game_features['current_team']['goal_attempts']

            if np.isnan(current_team_goal_attempts) or current_team_goal_attempts == 0:

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

                goal_attempts_allowed = current_team_goal_attempts

            goal_attempts_allowed_avg = np.divide(goal_attempts_allowed, features['games_played'])
            goals_allowed_avg = np.divide(features['goals_against'], features['games_played'])

            defensive_rank = (goal_attempts_allowed_avg * .30) + (goals_allowed_avg * .70)

            s = pd.Series([team["id"], features["team_name"], defensive_rank])
            rankings = rankings.append(s, ignore_index=True)
            rankings = rankings.sort_values(2, ascending=False)

        elif side_of_ball == "offensive":

            current_team_goal_attempts = game_features['current_team']['goal_attempts']

            if np.isnan(current_team_goal_attempts) or current_team_goal_attempts == 0:

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

                goal_attempts = current_team_goal_attempts

            goal_attempts_avg = np.divide(goal_attempts, features['games_played'])
            goals_for_avg = np.divide(features['goals_for'], features['games_played'])

            offensive_rank = (goal_attempts_avg * .30) + (goals_for_avg * .70)

            s = pd.Series([team["id"], features["team_name"], offensive_rank])
            rankings = rankings.append(s, ignore_index=True)
            rankings = rankings.sort_values(2, ascending=False)

        elif side_of_ball == "rpi":

            s = pd.Series([team["id"], features["team_name"], features["rpi"]])
            rankings = rankings.append(s, ignore_index=True)
            rankings = rankings.sort_values(2, ascending=False)

        elif side_of_ball == "records":
            s = pd.Series([team["id"], features["team_name"], features["current_record"]])
            rankings = rankings.append(s, ignore_index=True)
            rankings = rankings.sort_values(2, ascending=False)

    return rankings


def set_rank(team, data, rpi_rankings, offensive_rankings, defensive_rankings, round_num):
    """ Assigning RPI Rankings to the Current Team and the Opponent Team """
    rpi_rank = rpi_rankings.loc[rpi_rankings[0] == team['id'], "rpi_rankings_quartiled"]

    r_idx = data.loc[(data["team_id"] == team["id"]) & (data["round"] == round_num), "rpi_ranking"].index

    opp_r_idx = data.loc[(data["opp_id"] == team["id"]) & (data["round"] == round_num), "rpi_ranking"].index

    data.loc[r_idx, "rpi_ranking"] = rpi_rank.values[0]
    data.loc[opp_r_idx, "opp_rpi_ranking"] = rpi_rank.values[0]
    #data.set_value(r_idx, "rpi_ranking", 1)
    #data.set_value(opp_r_idx, "opp_rpi_ranking", 1)

    ''' If the team is the team_id then put in their offensive ranking for that game '''
    offensive_rank = offensive_rankings.loc[
        offensive_rankings[0] == team['id'], "offensive_rankings_quartiled"]
    idx = data.loc[(data["team_id"] == team["id"]) & (data["round"] == round_num), "offensive_ranking"].index

    data.loc[idx, "offensive_ranking"] = offensive_rank.values[0]
    #data.set_value(idx, "offensive_ranking", offensive_rank.values[0])

    ''' If the team is the opp then put in their defensive ranking for that game '''
    defensive_rank = defensive_rankings.loc[
        defensive_rankings[0] == team['id'], "defensive_rankings_quartiled"]
    opp_idx = data.loc[(data["opp_id"] == team["id"]) & (data["round"] == round_num)].index

    data.loc[opp_idx, "opp_defensive_ranking"] = defensive_rank.values[0]
    #data.set_value(opp_idx, "opp_defensive_ranking", defensive_rank.values[0])

    return data


def rank_tables(teams_in_league, i, upcoming):

    rpi_rankings = rank_teams(teams_in_league, i, "rpi", upcoming)
    r_rankings = model_libs.quartile_list(rpi_rankings, True)
    rpi_rankings["rpi_rankings_quartiled"] = r_rankings
    #print(rpi_rankings)
    print("Finished with RPI Rankings")

    offensive_rankings = rank_teams(teams_in_league, i, "offensive", upcoming)
    rankings = model_libs.quartile_list(offensive_rankings, True)
    offensive_rankings["offensive_rankings_quartiled"] = rankings
    print("Finished with Offensive Rankings")
    #print(offensive_rankings)

    defensive_rankings = rank_teams(teams_in_league, i, "defensive", upcoming)
    rankings = model_libs.quartile_list(defensive_rankings, False)
    defensive_rankings["defensive_rankings_quartiled"] = rankings
    print("Finished with Defensive Rankings")
    #print(defensive_rankings)

    return rpi_rankings, offensive_rankings, defensive_rankings


def get_rankings(leagues, teams, league_rounds, data, upcoming):

    data["offensive_ranking"] = pd.Series(None, index=data.index)
    data["opp_defensive_ranking"] = pd.Series(None, index=data.index)
    data["rpi_ranking"] = pd.Series(None, index=data.index)
    data["opp_rpi_ranking"] = pd.Series(None, index=data.index)

    """ Going through each League"""
    for key, value in leagues.items():
        country_code = leagues[key]
        round_num = league_rounds[key]
        teams_in_league = teams[teams["country_code"] == country_code]
        print("LEAGUE :: {}".format(country_code))

        if upcoming:

            print("ROUND :: {} ".format(round_num))

            rpi_rankings, offensive_rankings, defensive_rankings = rank_tables(teams_in_league, round_num, upcoming)

            """ Loop through each Team in the League for that round and assign an Offensive Rank """
            for k, team in teams_in_league.iterrows():
                ranked_data = set_rank(team, data, rpi_rankings, offensive_rankings, defensive_rankings, round_num)

        else:
            """ Looping through the Previous Rounds """
            for i in range(4, round_num):

                print("ROUND :: {} ".format(i))

                rpi_rankings, offensive_rankings, defensive_rankings = rank_tables(teams_in_league, i, upcoming)

                """ Loop through each Team in the League for that round and assign an Offensive Rank """
                for k, team in teams_in_league.iterrows():
                    ranked_data = set_rank(team, data, rpi_rankings, offensive_rankings, defensive_rankings, i)

    return ranked_data


def get_coverage():
    cnx = mysql.connector.connect(user=settings.MYSQL_USER, password=settings.MYSQL_PASSWORD,
                                  host=settings.MYSQL_HOST,
                                  database=settings.MYSQL_DATABASE)

    match_details = pd.read_sql('SELECT * FROM home_away_coverage_all', cnx)

    return match_details


def get_columns():

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

    return columns, stats_columns


def get_teams():
    cnx = mysql.connector.connect(user=settings.MYSQL_USER, password=settings.MYSQL_PASSWORD,
                                  host=settings.MYSQL_HOST,
                                  database=settings.MYSQL_DATABASE)

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
    cnx = mysql.connector.connect(user=settings.MYSQL_USER, password=settings.MYSQL_PASSWORD,
                                  host=settings.MYSQL_HOST,
                                  database=settings.MYSQL_DATABASE)
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

    columns, stats_columns = get_columns()
    data = pd.DataFrame(training_list, columns=columns + stats_columns)

    data = data.replace(np.nan, data.mean())

    return data
