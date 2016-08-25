from sklearn.metrics import f1_score
from sklearn import mixture
import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

def train_classifier(clf, X_train, y_train):
    clf.fit(X_train, y_train)


def predict_labels(clf, features, target):
    y_pred = clf.predict(features)
    """print(' ~~~~~~~~~~~~~~~~~~~~~~~ ')
    print(y_pred)
    print(target.values)
    print(' ~~~~~~~~~~~~~~~~~~~~~~~ ')"""
    return f1_score(target.values, y_pred, average="macro")


def train_predict(clf, X_train, y_train, X_test, y_test):
    train_classifier(clf, X_train, y_train)
    train_f1_score = predict_labels(clf, X_train, y_train)
    test_f1_score = predict_labels(clf, X_test, y_test)

    return train_f1_score, test_f1_score

def get_split(data):
    from stats import model_libs
    target_col = 'points'
    ignore_cols = ['match_id', 'team_id', 'team_name', 'opp_id', 'opp_name', 'scheduled']

    td = model_libs._clone_and_drop(data, ignore_cols)
    (y, X) = model_libs._extract_target(td, target_col)

    return X, y

def build_model(data, type):

    from sklearn import grid_search
    from sklearn.cross_validation import train_test_split
    from sklearn.svm import SVC
    from stats import model_libs

    target_col = 'points'
    ignore_cols = ['match_id', 'team_id', 'team_name', 'opp_id', 'opp_name', 'scheduled']

    td = model_libs._clone_and_drop(data, ignore_cols)
    (y, X) = model_libs._extract_target(td, target_col)

    parameters = {'kernel': ('linear', 'rbf'), 'C': [1, 10]}
    #parameters = [{'kernel': ['rbf'], 'gamma': [1e-3, 1e-4], 'C': [1, 10, 100, 1000]}, {'kernel': ['linear'], 'C': [1, 10, 100, 1000]}]

    if type == 'svc':
        svr = SVC()
        clf = grid_search.GridSearchCV(svr, parameters)
        # X_train, X_test, y_train, y_test = cross_validation.train_test_split(X, y, test_size=0.2, random_state=42)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        train_f1_score, test_f1_score = train_predict(clf, X_train, y_train, X_test, y_test)
        # scores = cross_validation.cross_val_score(clf, X_train, y_train, cv=5)
        print("F1 score for training set: {}".format(train_f1_score))
        print("F1 score for test set: {}".format(test_f1_score))
        return clf
    elif type == 'gmm':
        sil_scores = []
        clusterer = mixture.GMM(n_components=3, covariance_type='full')
        clusterer.fit(X)
        preds = clusterer.predict(X)
        centers = np.round(clusterer.means_, 2)
        score = silhouette_score(X, preds)
        sil_scores.append(score)
        print(3, 'clusters:', score)

        return sil_scores, clusterer
