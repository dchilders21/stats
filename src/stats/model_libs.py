import statsmodels.api as sm
import numpy as np
import random

L1_ALPHA = 16.0


def build_model_logistic(target, data, acc=0.00000001, alpha=L1_ALPHA):
    """ Trains a logistic regresion model. target is the target.
        data is a dataframe of samples for training. The length of
        target must match the number of rows in data.
    """
    data = data.copy()
    logit = sm.Logit(target, data, disp=False)
    return logit.fit_regularized(maxiter=1024, alpha=alpha, acc=acc, disp=False)


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

def get_team_round(team_country):
    """ Calls in a Team ID and returns the current round that league is in"""
    if team_country == 'USA':
        return 27
    elif team_country == 'ENG':
        return 5
    elif team_country == 'DEU':
        return 3
    elif team_country == 'ESP':
        return 4
    elif team_country == 'FRA':
        return 4
