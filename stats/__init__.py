import os
import pandas as pd
import numpy as np
import mysql.connector
from flask import render_template, request, url_for, redirect

from flask import Flask, Response
import flask_login
from flask_login import UserMixin, login_required
import datetime

from flask_wtf import Form as FlaskForm
from wtforms import BooleanField, StringField, PasswordField, validators

from stats import model_libs, form_model, predict_matches
import settings

app = Flask(__name__)

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

STATIC_PATH = static_folder_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")

app.config.from_object('config')

cnx = mysql.connector.connect(user=settings.MYSQL_USER, password=settings.MYSQL_PASSWORD,
                              host=settings.MYSQL_HOST,
                              database=settings.MYSQL_DATABASE)
cursor = cnx.cursor(dictionary=True, buffered=True)

teams = pd.read_sql("SELECT id, name FROM teams", cnx)

leagues = ['NBA']

login_manager = flask_login.LoginManager()
login_manager.init_app(app)

login_manager.login_view = "login"
login_manager.login_message_category = "info"

todays_date = model_libs.tz2ntz(datetime.datetime.utcnow(), 'UTC', 'US/Pacific')
today = model_libs.tz2ntz(datetime.datetime.utcnow(), 'UTC', 'US/Pacific').strftime('%m_%d_%y')

#today = "12_01_16"
print('INITIALIZED...')
print('V 2.0')


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
            return redirect(url_for('home', _external=True))

    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    flask_login.logout_user()

    return redirect(url_for('login', _external=True))


@app.route('/')
@login_required
def home():

    prediction_csv = 'stats/csv/nba/' + str(today) + '/all_predictions.csv'
    prediction_data = pd.read_csv(prediction_csv)

    columns = ['is_home', 'linear_regression_total_pts_preds', 'opp_id', 'opp_name', 'team_id', 'team_name']

    prediction_data = prediction_data[columns]
    # Need to reorganize the data for visual display, will eventually do this when creating the 'all_predictions' CSV
    home_team = pd.DataFrame(prediction_data.iloc[::2].values, columns=columns)
    home_team = home_team.rename(index=str, columns={"team_name": "home_team", "team_id": "home_id",
                                                     "linear_regression_total_pts_preds": "home_pts_preds"})
    away_team = pd.DataFrame(prediction_data.iloc[1::2].values, columns=columns)
    away_team = away_team.rename(index=str, columns={"team_name": "away_team", "team_id": "away_id",
                                                     "linear_regression_total_pts_preds": "away_pts_preds"})
    home_team = home_team[['home_team', 'home_id', 'home_pts_preds']]
    away_team = away_team[['away_team', 'away_id', 'away_pts_preds']]

    pred_data = pd.concat([home_team, away_team], axis=1)

    return render_template("index.html", leagues=leagues, teams=teams, pred_data=pred_data,
                           today=todays_date.strftime("%B %d, %Y"))


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
    league_rounds = model_libs.get_leagues_rounds(leagues)
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
