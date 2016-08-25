import datetime
import os
import random


import pandas as pd
from flask import Flask
from flask import render_template

from stats import model_libs, match_stats, form_model, form_data


app = Flask(__name__)

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

STATIC_PATH = static_folder_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")




@app.route('/')
def init():
    return render_template("index.html", teams=list_of_teams)


@app.route('/<int:id>')
def matches(id):
    prev_matches = match_details.loc[
        ((match_details['home_id'] == id) | (match_details['away_id'] == id)) &
        (match_details['scheduled'] < prev_week)]

    # Reverses the prev_matches DF
    prev_matches = prev_matches.iloc[::-1]
    prev_matches = prev_matches.sort_index(ascending=True, axis=0)
    prev_matches = prev_matches.reindex(index=prev_matches.index[::-1])
    prev_matches.head()

    previous_list = list(iternamedtuples(prev_matches))

    upcoming_team_matches = upcoming_matches.loc[
        ((upcoming_matches['home_id'] == id) | (upcoming_matches['away_id'] == id))]

    upcoming_list = []
    current_list = []

    if not upcoming_team_matches.empty:
        for i, upcoming_team_match in upcoming_team_matches.iterrows():
            temp = pd.DataFrame([])
            df = temp.append(upcoming_team_match, ignore_index=True)

            upcoming_stats = match_stats.create_match(id, df, match_details, prev_week, True, False)

            if upcoming_stats is not None:
                upcoming_list.append(upcoming_stats)
                current_list.append(upcoming_team_match)


            reg_model = form_model.get_model()
            upcoming_data = pd.DataFrame(upcoming_list, columns=columns)
            ud = model_libs._clone_and_drop(upcoming_data, ignore_cols)
            (ud_y, ud_X) = model_libs._extract_target(ud, target_col)
            print(ud)
            print(reg_model.predict(ud_X))

    return render_template("index.html", teams=list_of_teams, previous_list=previous_list, current_list=current_list)


@app.route('/rankings/<int:week>')
def rankings(week):
    power_list = []
    power_rankings = pd.DataFrame()
    temp_list = []

    # Creating Fake Values for an Upcoming Match since we don't need for Ranking List
    temp_list.append([0, 0, 0, 0, 0, 0])
    temp_df = pd.DataFrame(temp_list, columns=['away_id', 'away_team', 'home_id', 'home_team', 'match_id', 'scheduled'])

    for i, team in teams.iterrows():

        temp_week = (schedule_2016[week - 1] + datetime.timedelta(hours=7))

        prev_matches = match_details.loc[
            ((match_details['home_id'] == team["id"]) | (match_details['away_id'] == team["id"])) &
            (match_details['scheduled'] < temp_week)]

        upcoming_stats = match_stats.create_match(team["id"], temp_df, match_details, prev_week, True, False)
        s = pd.Series([team["id"], upcoming_stats['sos']])
        power_rankings = power_rankings.append(s, ignore_index=True)
        power_rankings = power_rankings.sort_values(1, ascending=False)

    for i, power in power_rankings.iterrows():
        power_list.append(power)

    return render_template("rankings.html", rankings=power_list)

@app.route('/random')
def random_trials():
    """ For every team runs through every match they've played and randomly chooses the result
        Then we compare that with the actual result of the match """

    num_of_iterations = 100
    possible_results = (0, 1, 3)
    accuracy_average = []

    for x in range(num_of_iterations):
        prediction_list = []  # '0' equals wrong, '1' equals correct
        accuracy_list = []
        for i, team in teams.iterrows():
            prev_matches = match_details.loc[
                ((match_details['home_id'] == team["id"]) | (match_details['away_id'] == team["id"]))]
            accuracy_list.append(prev_matches.shape[0])
            predicted_result = random.choice(possible_results)
            for i, p in prev_matches.iterrows():
                if p["home_id"] == team["id"]:
                    if p["home_points"] == predicted_result:
                        prediction_list.append(1)
                    else:
                        prediction_list.append(0)
                else:
                    if p["away_points"] == predicted_result:
                        prediction_list.append(1)
                    else:
                        prediction_list.append(0)

        accuracy_average.append(sum(prediction_list)/sum(accuracy_list))

    accuracy = sum(accuracy_average)/num_of_iterations

    return render_template("random.html", accuracy=accuracy)
