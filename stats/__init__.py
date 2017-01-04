import os
import pandas as pd
import numpy as np
import mysql.connector
from flask import render_template, request, url_for, redirect, jsonify

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
print(todays_date)
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

    columns = ['is_home', 'linear_regression_total_pts_preds', 'opp_id', 'opp_name', 'team_id', 'team_name',
               'Probability 0', 'Probability 1', 'log_result_preds']

    prediction_data = prediction_data[columns]

    # Need to reorganize the data for visual display, will eventually do this when creating the 'all_predictions' CSV
    home_team = pd.DataFrame(prediction_data.iloc[::2].values, columns=columns)
    home_team = home_team.rename(index=str, columns={"team_name": "home_team", "team_id": "home_id",
                                                     "linear_regression_total_pts_preds": "home_pts_preds",
                                                     "log_result_preds": "home_result_preds",
                                                     'Probability 0': 'home_prob_0', 'Probability 1': 'home_prob_1'})
    away_team = pd.DataFrame(prediction_data.iloc[1::2].values, columns=columns)
    away_team = away_team.rename(index=str, columns={"team_name": "away_team", "team_id": "away_id",
                                                     "linear_regression_total_pts_preds": "away_pts_preds",
                                                     "log_result_preds": "away_result_preds",
                                                     'Probability 0': 'away_prob_0', 'Probability 1': 'away_prob_1'})

    home_team = home_team[['home_team', 'home_id', 'home_pts_preds', 'home_prob_0', 'home_prob_1', 'home_result_preds']]
    away_team = away_team[['away_team', 'away_id', 'away_pts_preds', 'away_prob_0', 'away_prob_1', 'away_result_preds']]

    pred_data = pd.concat([home_team, away_team], axis=1)

    line_csv = 'stats/csv/pinnacle/' + str(today) + '/pinnacle_lines.csv'
    line_data = pd.read_csv(line_csv)

    def lines_to_preds(home_team, line_data, type):
        for i, l in line_data.iterrows():
            if home_team in l['team_2']:
                if type == 'spread':
                    return l['spread']
                else:
                    return l['over_under']

    pred_data["spread"] = pred_data.apply(
        lambda row: lines_to_preds(row['home_team'], line_data, 'spread'), axis=1)

    pred_data["over_under"] = pred_data.apply(
        lambda row: lines_to_preds(row['home_team'], line_data, 'over_under'), axis=1)

    return render_template("index.html", leagues=leagues, teams=teams, pred_data=pred_data,
                           today=todays_date.strftime("%B %d, %Y"))


@app.route('/api', methods=['GET'])
def api():
    prediction_csv = 'stats/csv/nba/' + str(today) + '/all_predictions.csv'
    prediction_data = pd.read_csv(prediction_csv)

    columns = ['is_home', 'linear_regression_total_pts_preds', 'opp_id', 'opp_name', 'team_id', 'team_name',
               'Probability 0', 'Probability 1', 'log_result_preds']

    prediction_data = prediction_data[columns]

    # Need to reorganize the data for visual display, will eventually do this when creating the 'all_predictions' CSV
    home_team = pd.DataFrame(prediction_data.iloc[::2].values, columns=columns)
    home_team = home_team.rename(index=str, columns={"team_name": "home_team", "team_id": "home_id",
                                                     "linear_regression_total_pts_preds": "home_pts_preds",
                                                     "log_result_preds": "home_result_preds",
                                                     'Probability 0': 'home_prob_0', 'Probability 1': 'home_prob_1'})
    away_team = pd.DataFrame(prediction_data.iloc[1::2].values, columns=columns)
    away_team = away_team.rename(index=str, columns={"team_name": "away_team", "team_id": "away_id",
                                                     "linear_regression_total_pts_preds": "away_pts_preds",
                                                     "log_result_preds": "away_result_preds",
                                                     'Probability 0': 'away_prob_0', 'Probability 1': 'away_prob_1'})

    home_team = home_team[['home_team', 'home_id', 'home_pts_preds', 'home_prob_0', 'home_prob_1', 'home_result_preds']]
    away_team = away_team[['away_team', 'away_id', 'away_pts_preds', 'away_prob_0', 'away_prob_1', 'away_result_preds']]

    pred_data = pd.concat([home_team, away_team], axis=1)

    line_csv = 'stats/csv/pinnacle/' + str(today) + '/pinnacle_lines.csv'
    line_data = pd.read_csv(line_csv)

    def lines_to_preds(home_team, line_data, type):
        for i, l in line_data.iterrows():
            if home_team in l['team_2']:
                if type == 'spread':
                    return l['spread']
                else:
                    return l['over_under']

    pred_data["spread"] = pred_data.apply(
        lambda row: lines_to_preds(row['home_team'], line_data, 'spread'), axis=1)

    pred_data["over_under"] = pred_data.apply(
        lambda row: lines_to_preds(row['home_team'], line_data, 'over_under'), axis=1)

    list_data = pred_data.to_dict(orient='records')

    return jsonify({'data': list_data})
