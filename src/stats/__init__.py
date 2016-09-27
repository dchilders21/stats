import os
import sys
import pandas as pd
import numpy as np
import mysql.connector
from flask import render_template, request, url_for

from flask import Flask

from stats import model_libs, match_stats, form_model, form_data, predict_matches

app = Flask(__name__)

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

STATIC_PATH = static_folder_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")

cnx = mysql.connector.connect(user='root', password='',
                              host='127.0.0.1',
                              database='mls')
cursor = cnx.cursor(dictionary=True, buffered=True)

match_details = pd.read_sql('SELECT * FROM home_away_coverage_all', cnx)

print('INITIALIZED...')


@app.route('/rankings/<league>/<int:round>')
def rankings(league, round):
    power_list = []

    if league == 'mls':
        teams = pd.read_sql("SELECT id, full_name FROM teams WHERE id < 41", cnx)

    power_rankings = form_data.get_power_rankings(teams, round)

    for i, power in power_rankings.iterrows():
        power_list.append(power)

    pr = np.array(power_rankings.loc[:, 2])
    qqs = np.percentile(pr, [20, 40, 60, 80])

    return render_template("rankings.html", rankings=power_list)


@app.route('/<league>/<int:team_id>/<int:round_num>')
def team_stats(league, team_id, round_num):
    teams_list = []
    leagues = model_libs.get_leagues_country_codes()
    all_teams = form_data.get_teams()
    teams = all_teams.loc[all_teams["country_code"] == leagues[league]]

    for key, value in teams.iterrows():
        teams_list.append(value)

    # current_team = teams.loc[teams["id"] == team_id]
    league_round = model_libs.get_leagues_rounds()

    previous_matches = match_details.loc[
        ((match_details['home_id'] == team_id) | (match_details['away_id'] == team_id)) &
        (match_details['round'] < round_num)]

    previous_matches = previous_matches.iloc[-3:]

    upcoming_matches, _ = predict_matches.get_upcoming_matches()

    # print(previous_matches)
    upcoming_matches = upcoming_matches.loc[
        ((upcoming_matches['home_id'] == team_id) | (upcoming_matches['away_id'] == team_id))]

    previous_matches = previous_matches.drop(['scheduled', 'home_formation', 'home_first_half_score',
                                              'home_second_half_score', 'home_offsides', 'home_yellow_card', 'away_formation', 'away_first_half_score',
                                              'away_second_half_score', 'away_offsides', 'away_yellow_card'], axis=1)

    features_breakdown = {'score': [], 'opp_score': [], 'points': [], 'attacks': [], 'ball_safe': [], 'corner_kicks': [], 'dangerous_attacks': [], 'fouls': [],
               'shots_on_target': [], 'shots_total': [], 'possession': [], 'goal_attempts': [], 'saves': [], 'goal_kicks': []}

    for index, game in previous_matches.iterrows():
        if team_id == game['home_id']:
            features_breakdown["score"].append(game["home_score"])
            features_breakdown["opp_score"].append(game["away_score"])
            features_breakdown["points"].append(game["home_points"])
            features_breakdown["attacks"].append(game["home_attacks"])
            features_breakdown["ball_safe"].append(game["home_ball_safe"])
            features_breakdown["corner_kicks"].append(game["home_corner_kicks"])
            features_breakdown["dangerous_attacks"].append(game["home_dangerous_attacks"])
            features_breakdown["fouls"].append(game["home_fouls"])
            features_breakdown["shots_on_target"].append(game["home_shots_on_target"])
            features_breakdown["shots_total"].append(game["home_shots_total"])
            features_breakdown["possession"].append(game["home_possession"])
            features_breakdown["goal_attempts"].append(game["home_goal_attempts"])
            features_breakdown["saves"].append(game["home_saves"])
            features_breakdown["goal_kicks"].append(game["home_goal_kicks"])
        elif team_id == game["away_id"]:
            features_breakdown["score"].append(game["away_score"])
            features_breakdown["opp_score"].append(game["home_score"])
            features_breakdown["points"].append(game["away_points"])
            features_breakdown["attacks"].append(game["away_attacks"])
            features_breakdown["ball_safe"].append(game["away_ball_safe"])
            features_breakdown["corner_kicks"].append(game["away_corner_kicks"])
            features_breakdown["dangerous_attacks"].append(game["away_dangerous_attacks"])
            features_breakdown["fouls"].append(game["away_fouls"])
            features_breakdown["shots_on_target"].append(game["away_shots_on_target"])
            features_breakdown["shots_total"].append(game["away_shots_total"])
            features_breakdown["possession"].append(game["away_possession"])
            features_breakdown["goal_attempts"].append(game["away_goal_attempts"])
            features_breakdown["saves"].append(game["away_saves"])
            features_breakdown["goal_kicks"].append(game["away_goal_kicks"])

    training_list = form_data.create_match(team_id, upcoming_matches, match_details, league_round[league])
    columns = form_data.get_columns()
    upcoming_data = pd.DataFrame(training_list, columns=columns)
    upcoming_data = upcoming_data.replace(np.nan, upcoming_data.mean())

    return render_template("team_stats.html", leagues=leagues, teams=teams_list,
                           previous_matches=previous_matches.to_html(), upcoming_matches=upcoming_data.to_html(),
                           features_breakdown=features_breakdown)

