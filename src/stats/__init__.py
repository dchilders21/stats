import os
import sys
import pandas as pd
import numpy as np
import mysql.connector
import datetime
from flask import render_template, request, url_for, redirect

from flask import Flask, Response
import flask_login
from flask_login import UserMixin, login_required

from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField, PasswordField, validators

from stats import model_libs, match_stats, form_model, form_data, predict_matches

app = Flask(__name__)

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

STATIC_PATH = static_folder_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")

app.config.from_object('config')

cnx = mysql.connector.connect(user='root', password='',
                              host='127.0.0.1',
                              database='mls')
cursor = cnx.cursor(dictionary=True, buffered=True)

match_details = pd.read_sql('SELECT * FROM home_away_coverage_all', cnx)

leagues = model_libs.get_leagues_country_codes()
rounds = model_libs.get_leagues_rounds()

login_manager = flask_login.LoginManager()
login_manager.init_app(app)

login_manager.login_view = "login"
login_manager.login_message_category = "info"

#dt = datetime.date.today().strftime("%m_%d_%y")
dt = "11_02_16"
print('INITIALIZED...')


class LoginForm(FlaskForm):
    username = StringField('Username', [validators.Length(min=4, max=25)])
    password = PasswordField('New Password', [
        validators.DataRequired()
    ])


class User(UserMixin):
    user_database = {
        1: {"user": "Guest", "username": "Guest", "password": "guest"},
        2: {"user": "Admin", "username": "admin", "password": "admin"}
    }

    def __init__(self, username, password):
        self.id = '1'
        self.username = username
        self.password = password

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id


@login_manager.user_loader
def load_user(user_id):

    for k, v in User.user_database.items():
        if int(user_id) == k:
            user = User(v["username"], v["password"])

    return user


@app.route('/login', methods=['GET', 'POST'])
def login():

    form = LoginForm(request.form)
    if form.validate_on_submit():
        # check if the user exists and if he/she provided correct password
        if form.username.data == "Guest" and form.password.data == "guest":
            user = User(form.username.data, form.password.data)
            flask_login.login_user(user)
            return redirect(url_for('home'))

    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    flask_login.logout_user()

    return redirect(url_for('login'))


def get_predictions(team, target, isHome):

    prediction_csv = 'stats/csv/' + str(dt) + '/all_predictions.csv'
    prediction_data = pd.read_csv(prediction_csv)

    if isHome:
        match = prediction_data.loc[((prediction_data["team_name"] == team) & (prediction_data["is_home"] == 1))]
    else:
        match = prediction_data.loc[((prediction_data["team_name"] == team) & (prediction_data["is_home"] == 0))]

    if target == "no_ties":
        predictions = [match.iloc[0]["Probability 0"], match.iloc[0]["Probability 1"], match.iloc[0]["Probability 2"]]
    else:
        predictions = match.iloc[0]["log_" + str(target) + "_preds"]

    return predictions


def calculate_stats(team_id):

    previous_matches = match_details.loc[
        ((match_details['home_id'] == team_id) | (match_details['away_id'] == team_id))]

    win = 0
    loss = 0
    draw = 0

    games_played = 0

    season_stats = {'possession': [], 'attacks': [], 'dangerous_attacks': [], 'yellow_cards': [],
                    'corner_kicks': [], 'shots_on_target': [], 'shots_total': [], 'ball_safe': [],
                    'goal_attempts': [], 'goal_attempts_allowed': [], 'saves': [], 'first_half_goals': [],
                    'sec_half_goals': [], 'goal_kicks': [], 'goals_for': [], 'goals_allowed': []}

    for index, game in previous_matches.iterrows():

        games_played += 1

        if team_id == game['home_id']:
            if game['home_points'] == 3:
                win += 1
            elif game['home_points'] == 1:
                draw += 1
            else:
                loss += 1

            season_stats['possession'].append(game['home_possession'])
            season_stats['attacks'].append(game['home_attacks'])
            season_stats['dangerous_attacks'].append(game['home_dangerous_attacks'])
            season_stats['yellow_cards'].append(game['home_yellow_card'])
            season_stats['corner_kicks'].append(game['home_corner_kicks'])
            season_stats['shots_on_target'].append(game['home_shots_on_target'])
            season_stats['shots_total'].append(game['home_shots_total'])
            season_stats['ball_safe'].append(game['home_ball_safe'])
            season_stats['goal_attempts'].append(game['home_goal_attempts'])
            season_stats['goal_attempts_allowed'].append(game['away_goal_attempts'])
            season_stats['saves'].append(game['home_saves'])
            season_stats['first_half_goals'].append(game['home_first_half_score'])
            season_stats['sec_half_goals'].append(game['home_second_half_score'])
            season_stats['goal_kicks'].append(game['home_goal_kicks'])
            season_stats['goals_for'].append(game['home_score'])
            season_stats['goals_allowed'].append(game['away_score'])
        else:

            if game['away_points'] == 3:
                win += 1
            elif game['away_points'] == 1:
                draw += 1
            else:
                loss += 1

            season_stats['possession'].append(game['away_possession'])
            season_stats['attacks'].append(game['away_attacks'])
            season_stats['dangerous_attacks'].append(game['away_dangerous_attacks'])
            season_stats['yellow_cards'].append(game['away_yellow_card'])
            season_stats['corner_kicks'].append(game['away_corner_kicks'])
            season_stats['shots_on_target'].append(game['away_shots_on_target'])
            season_stats['shots_total'].append(game['away_shots_total'])
            season_stats['ball_safe'].append(game['away_ball_safe'])
            season_stats['goal_attempts'].append(game['away_goal_attempts'])
            season_stats['goal_attempts_allowed'].append(game['home_goal_attempts'])
            season_stats['saves'].append(game['away_saves'])
            season_stats['first_half_goals'].append(game['away_first_half_score'])
            season_stats['sec_half_goals'].append(game['away_second_half_score'])
            season_stats['goal_kicks'].append(game['away_goal_kicks'])
            season_stats['goals_for'].append(game['away_score'])
            season_stats['goals_allowed'].append(game['home_score'])

    for k, v in season_stats.items():
        season_stats[k] = np.nanmean(np.array(v))

    record = {"win": win, "loss": loss, "draw": draw}

    previous_matches = previous_matches[
        ["scheduled", "home_team", "home_id", "home_score", "home_first_half_score", "home_second_half_score",
         "away_team", "away_id", "away_score", "away_first_half_score",
         "away_second_half_score"]]
    previous_matches = previous_matches.iloc[::-1]
    previous_matches = previous_matches.to_dict(orient='records')

    return previous_matches, record, season_stats


@app.route('/')
def home():
    all_teams = form_data.get_teams()
    all_teams = all_teams.reset_index()
    all_teams = all_teams.to_json(orient='index')

    upcoming_matches, _ = predict_matches.get_upcoming_matches()
    upcoming_matches['league'] = upcoming_matches.apply(lambda row: model_libs.get_league_from_country_code(row["country_code"]), axis=1)
    upcoming_matches = upcoming_matches.reindex(columns=['league', 'home_team', 'away_team', 'scheduled',
                                                       'home_id', 'away_id'])
    upcoming_matches = upcoming_matches.to_dict(orient='records')

    return render_template("index.html", leagues=leagues, teams=all_teams, upcoming_matches=upcoming_matches)


@app.route('/league/<league>')
@login_required
def league(league):

    table = str('matches_' + league)
    round_number = rounds[league]
    query = str(
        "SELECT " + table + ".id as 'match_id', " + table + ".scheduled, " + table + ".home_id, " + table + ".away_id, teams1.full_name AS 'home_team', teams2.full_name AS 'away_team', teams1.country_code AS 'country_code' FROM " + table + " LEFT JOIN teams teams1 ON " + table + ".home_id = teams1.id LEFT JOIN teams teams2 ON " + table + ".away_id = teams2.id WHERE status = 'scheduled' AND round_number = '" + str(
            round_number) + "'")
    matches = pd.read_sql(query, cnx)

    matches = matches.reindex(columns=['home_team', 'away_team', 'scheduled', 'home_id', 'away_id'])

    print(matches)
    # Fix this
    matches["predicted_home_points"] = matches.apply(
        lambda row: get_predictions(row["home_team"], "points", True), axis=1)

    matches["predicted_home_goals"] = matches.apply(
        lambda row: get_predictions(row["home_team"], "converted_goals", True), axis=1)

    matches["predicted_away_points"] = matches.apply(
        lambda row: get_predictions(row["away_team"], "points", False), axis=1)

    matches["predicted_away_goals"] = matches.apply(
        lambda row: get_predictions(row["away_team"], "converted_goals", False), axis=1)

    print(matches)
    matches = matches.to_dict(orient='records')
    return render_template("league.html", leagues=leagues, league=league, matches=matches)


@app.route('/team/<int:team_id>')
@login_required
def team(team_id):

    q = "SELECT * FROM teams WHERE id = '" + str(team_id) + "'"
    team = pd.read_sql(q, cnx)

    previous_matches, record, season_stats = calculate_stats(team_id)

    upcoming_matches, _ = predict_matches.get_upcoming_matches()

    upcoming_matches = upcoming_matches.loc[
        ((upcoming_matches['home_id'] == team_id) | (upcoming_matches['away_id'] == team_id))]

    opp_id = upcoming_matches.iloc[0]['away_id'] if upcoming_matches.iloc[0]['home_id'] == team_id else upcoming_matches.iloc[0]['home_id']

    _, opp_record, _ = calculate_stats(opp_id)

    upcoming_matches['league'] = upcoming_matches.apply(lambda row: model_libs.get_league_from_country_code(row["country_code"]), axis=1)

    round_number = model_libs.get_team_round(upcoming_matches["country_code"].iloc[0])

    df = pd.DataFrame([]).append(upcoming_matches, ignore_index=True)
    features, game_features = match_stats.create_match(team_id, df, match_details, round_number, False, False)

    if features is not None:
        for key, value in game_features.items():
            for k, v in value.items():
                new_key = key + '_' + k
                features[new_key] = v

    current_team = {"name": features["team_name"], "goals_for": features["goals_for"], "goals_allowed": features["goals_against"],
                     "attacks": features["current_team_attacks"], "dangerous_attacks": features["current_team_dangerous_attacks"],
                     "goal_attempts": features["current_team_goal_attempts"], "ball_safe": features["current_team_ball_safe"], "possession": features["current_team_possession"]}

    opp_team = {"name": features["opp_name"], "goals_for": features["opp_goals_for"],
                    "goals_allowed": features["opp_goals_against"],
                    "attacks": features["opp_team_attacks"],
                    "dangerous_attacks": features["opp_team_dangerous_attacks"],
                    "goal_attempts": features["opp_team_goal_attempts"],
                    "ball_safe": features["opp_team_ball_safe"], "possession": features["opp_team_possession"]}

    if features["is_home"] == 1:
        home_features = current_team
        away_features = opp_team
        home_record = record
        away_record = opp_record
    else:
        home_features = opp_team
        away_features = current_team
        home_record = opp_record
        away_record = record

    upcoming_matches = upcoming_matches.to_dict(orient='records')

    home_predicted_probs = get_predictions(home_features["name"], "no_ties", True)
    print(home_predicted_probs)
    # Fix this also
    home_predicted_points = get_predictions(home_features["name"], "points", True)
    home_predicted_goals = get_predictions(home_features["name"], "converted_goals", True)
    away_predicted_points = get_predictions(away_features["name"], "points", False)
    away_predicted_goals = get_predictions(away_features["name"], "converted_goals", False)

    return render_template("team.html", leagues=leagues, team_name=team["full_name"].loc[0], home_record=home_record,
                           away_record=away_record, previous_matches=previous_matches, upcoming_matches=upcoming_matches,
                           season_stats=season_stats, home_features=home_features, away_features=away_features,
                           home_predicted_points=home_predicted_points, away_predicted_points=away_predicted_points,
                           home_predicted_goals=home_predicted_goals, away_predicted_goals=away_predicted_goals,
                           home_predicted_probs=home_predicted_probs)


@app.route('/league/<league>/rankings')
@login_required
def rankings(league):
    leagues = model_libs.get_leagues_country_codes()
    league_rounds = model_libs.get_leagues_rounds()
    teams = form_data.get_teams()
    country_code = leagues[league]
    round_num = league_rounds[league]
    teams_in_league = teams[teams["country_code"] == country_code]

    rpi_rankings, offensive_rankings, defensive_rankings = form_data.rank_tables(teams_in_league, round_num, True)

    rpi_rankings = rpi_rankings.to_dict(orient='records')
    offensive_rankings = offensive_rankings.to_dict(orient='records')
    defensive_rankings = defensive_rankings.to_dict(orient='records')

    return render_template("rankings.html", leagues=leagues, league=league, rpi_rankings=rpi_rankings,
                           offensive_rankings=offensive_rankings, defensive_rankings=defensive_rankings)
