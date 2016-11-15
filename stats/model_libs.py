import numpy as np
import pandas as pd
import random
from collections import namedtuple
import mysql.connector

L1_ALPHA = 16.0

def _clone_and_drop(data, drop_cols):
    """ Returns a copy of a dataframe that doesn't have certain columns. """
    clone = data.copy()
    for col in drop_cols:
        if col in clone.columns:
            del clone[col]
    return clone


def _coerce_types(vals):
    """ Makes sure all of the values in a list are floats. """
    return [1.0 * val for val in vals]


def _coerce(data):
    """ Coerces a dataframe to all floats, and standardizes the values. """
    return _standardize(data.apply(_coerce_types))


def _standardize_col(col):
    """ Standardizes a single column (subtracts mean and divides by std
        dev).
    """
    std = np.std(col)
    mean = np.mean(col)

    if abs(std) > 0.001:
        return col.apply(lambda val: (val - mean)/std)
    else:
        return col


def _standardize_target_col(col):
    max = np.amax(col)
    min = np.amin(col)

    return col.apply(lambda val: ((val - min)/(max - min)))


def _standardize(data):
    """ Standardizes a dataframe. All fields must be numeric. """
    return data.apply(_standardize_target_col)


def _extract_target(data, target_col):
    """ Removes the target column from a data frame, returns the target
        col and a new data frame minus the target. """
    target = data[target_col]
    train_df = data.copy()
    del train_df[target_col]
    return target, train_df


def split(data, test_proportion=0.4):
    """ Splits a dataframe into a training set and a test set.
        Must be careful because back-to-back rows are expected to
        represent the same game, so they both must go in the
        test set or both in the training set.
    """

    train_vec = []
    if len(data) % 2 != 0:
        raise Exception('Unexpected data length')
    while len(train_vec) < len(data):
        rnd = random.random()
        train_vec.append(rnd > test_proportion)
        train_vec.append(rnd > test_proportion)

    test_vec = [not val for val in train_vec]
    train = data[train_vec]
    test = data[test_vec]
    if len(train) % 2 != 0:
        raise Exception('Unexpected train length')
    if len(test) % 2 != 0:
        raise Exception('Unexpected test length')
    return (train, test)


def diff_square(a, b):

    return np.subtract(np.square(a), np.square(b))


def predict_model(model, test, ignore_cols, target_col):
    """ Runs a simple predictor that will predict if we expect a team to
        win.
    """

    x = _clone_and_drop(test, ignore_cols)
    (y_test, x_test) = _extract_target(x, target_col)
    predicted = model.predict(x_test)
    result = test.copy()
    result['predicted'] = predicted
    return result


def reformat_formation(data, current, opponent):
    """ Reads all the formations in the current_formation and then compares to opp_formation to see if any formation
        is missing.  Returns all unique formations.
    """

    formations = []

    for name in data.groupby('current_formation').groups:
        formations.append(name)

    nd = np.array(formations)

    for name in data.groupby('opp_formation').groups:
        if name not in nd:
            nd.append(name)

    return nd


def rename_column(label):
    if label.count('_home_') > 0:
        new_name = label.replace('_home_', '_')
    elif label.count('_away_') > 0:
        new_name = label.replace('_away_', '_')
    return new_name


def pick_column(home, away):
    if np.isnan(home):
        return away
    elif np.isnan(away):
        return home


def predictions_diff(pred, actual):
    """0 if No, 1 if Yes"""
    if (pred - actual) == 0:
        return 1
    else:
        return 0


def set_group(goals):
    if goals >= 2:
        return 1
    elif goals < 2:
        return 0


def set_points(points):
    if points != 1:
        return 0
    else:
        return 1


def check_category(pred, actual):
    """0 if No, 1 if Yes"""
    if pred >= 2:
        if actual >= 2:
            return 1
        else:
            return 0
    else:
        if actual < 2:
            return 1
        else:
            return 0


def get_leagues_rounds(leagues):
    """ Upcoming Rounds (closest round not played yet) """
    # leagues = {"mls": 32, "epl": 11, "bundesliga": 10, "primera_division": 11, "ligue_1": 12}

    ''' Finds the current round of a league '''
    cnx = mysql.connector.connect(user='admin', password='1Qaz@wsx',
                                  host='0.0.0.0',
                                  database='mls')

    league_rounds = {}

    for l, v in leagues.items():
        matches_table = 'matches_' + l
        q = "SELECT MIN(round_number) as round FROM " + matches_table + " WHERE status = 'scheduled'"

        matches = pd.read_sql(q, cnx)

        if matches.iloc[0]['round'] is None:
            rnd = 32
        else:
            rnd = matches.iloc[0]['round']

        league_rounds[l] = rnd

    return league_rounds


def get_leagues_country_codes():
    leagues = {"mls": 'USA', "epl": 'ENG', "bundesliga": 'DEU', "primera_division": 'ESP', "ligue_1": 'FRA'}
    return leagues


def get_league_from_country_code(code):

    if code == "USA":
        return "MLS"
    elif code == "ENG":
        return "English Premiere League"
    elif code == "DEU":
        return "Bundesliga"
    elif code == "ESP":
        return "Primera Divsion"
    elif code == "FRA":
        return "Ligue 1"


def get_team_round(country_code):
    """ Calls in a Team Country Code and returns the current round that league is in"""
    # Last round 'closed' + 1
    country_codes = get_leagues_country_codes()

    league_rounds = get_leagues_rounds(country_codes)

    if country_code == 'USA':
        return league_rounds['mls']
    elif country_code == 'ENG':
        return league_rounds['epl']
    elif country_code == 'DEU':
        return league_rounds['bundesliga']
    elif country_code == 'ESP':
        return league_rounds['primera_division']
    elif country_code == 'FRA':
        return league_rounds['ligue_1']


def set_rpi_quartile(round_number, data, isCur):
    power_rankings = pd.DataFrame()
    power_list = []

    if isCur:
        rpi = 'rpi'
        team_id = 'team_id'
    else:
        rpi = 'opp_rpi'
        team_id = 'opp_id'

    td = data.loc[(data["round"] == round_number)]

    if not td.empty:
        s = td.loc[:, [team_id, rpi]]
        power_rankings = power_rankings.append(s, ignore_index=False)
        power_rankings = power_rankings.sort_values(rpi, ascending=False)

        for i, power in power_rankings.iterrows():
            power_list.append(power)

        pr = np.array(power_rankings.loc[:, rpi])
        qqs = np.percentile(pr, [25, 50, 75, 100])
        quartiles = [0, .3333, .6666, 1]
        idx = len(pr)
        for i in range(len(qqs)):
            a = np.where(pr[0:idx] <= qqs[i])
            pr[a] = quartiles[i]
            idx = a[0][0]

        return pr, power_rankings.index
    else:
        return None, None


def convert_sos_rpi(leagues, leagues_data, teams):

    all_leagues_data = pd.DataFrame([])

    for i in leagues:
        team_ids = teams.loc[teams["country_code"] == i]
        data = leagues_data[leagues_data["team_id"].isin(team_ids["id"])]
        data['rpi_quartiled'] = pd.Series(None, index=data.index)
        data_min = data['round'].min()
        data_max = data['round'].max() + 1

        for x in range(data_min, data_max):

            power_rankings, idx = set_rpi_quartile(x, data, True)
            opp_power_rankings, opp_idx = set_rpi_quartile(x, data, False)

            if idx is not None:
                data.loc[idx, "rpi_quartiled"] = power_rankings

            if opp_idx is not None:
                data.loc[opp_idx, "opp_rpi_quartiled"] = opp_power_rankings

        all_leagues_data = all_leagues_data.append(data)

    return all_leagues_data


def quartile_list(ranking, high_best):
    """ Takes a sorted DF and returns an array with the ranking """

    r = np.array(ranking.loc[:, 2])
    qqs = np.percentile(r, [25, 50, 75, 100])

    if high_best:
        quartiles = [0, .33333, .66666, 1]
    else:
        quartiles = [1, .66666, .33333, 0]

    idx = len(r)

    for i in range(len(qqs)):

        a = np.where(r[0:idx] <= qqs[i])
        r[a] = quartiles[i]
        idx = a[0][0]
        for x in range(len(a[0])):
            a[0][x] -= (i * 5)

    return r


def iternamedtuples(df):
    Row = namedtuple('Row', df.columns)
    for row in df.itertuples():
        yield Row(*row[1:])


# Simple Function to check the accuracy of the models. Not the Final function
def check_accuracy(model, data_X, y):
    actual_y = pd.DataFrame(y.values, columns=['actual'])
    predictions = pd.concat([pd.DataFrame(model.predict(data_X), columns=['predictions']), actual_y], axis=1)
    predictions['accuracy'] = predictions.apply(lambda r: predictions_diff(r['predictions'], r['actual']),
                                                axis=1)
    accuracy = np.divide(predictions['accuracy'].sum(), float(len(predictions['accuracy'])))

    return accuracy


def adjust_features(data):
    data["diff_goals_for"] = data.apply(
        lambda row: diff_square(row["goals_for"], row["opp_goals_for"]), axis=1)
    data["diff_goals_allowed"] = data.apply(
        lambda row: diff_square(row["goals_against"], row["opp_goals_against"]), axis=1)
    data["diff_attacks"] = data.apply(
        lambda row: diff_square(row["current_team_attacks"], row["opp_team_attacks"]), axis=1)
    data["diff_dangerous_attacks"] = data.apply(
        lambda row: diff_square(row["current_team_dangerous_attacks"], row["opp_team_dangerous_attacks"]), axis=1)
    data["diff_goal_attempts"] = data.apply(
        lambda row: diff_square(row["current_team_goal_attempts"], row["opp_team_goal_attempts"]), axis=1)
    data["diff_ball_safe"] = data.apply(
        lambda row: diff_square(row["current_team_ball_safe"], row["opp_team_ball_safe"]), axis=1)
    data["diff_possession"] = data.apply(
        lambda row: diff_square(row["current_team_possession"], row["opp_team_possession"]), axis=1)
    # data["diff_corner_kicks"] = data.apply(lambda row: .diff_square(row["current_team_corner_kicks"], row["opp_team_corner_kicks"]), axis=1)
    # data["diff_goal_kicks"] = data.apply(lambda row: diff_square(row["current_team_goal_kicks"], row["opp_team_goal_kicks"]), axis=1)
    # data["diff_saves"] = data.apply(lambda row: diff_square(row["current_team_saves"], row["opp_team_saves"]), axis=1)

    return data