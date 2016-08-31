from sklearn.metrics import f1_score
from sklearn import mixture
import numpy as np
from sklearn.svm import SVC
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn import grid_search
from sklearn import cross_validation
from sklearn.cross_validation import train_test_split
from stats import model_libs
from sklearn.cross_validation import StratifiedKFold
from sklearn.naive_bayes import GaussianNB


def train_classifier(clf, X_train, y_train):
    clf.fit(X_train, y_train)


def predict_labels(clf, features, target):
    y_pred = clf.predict(features)
    return f1_score(target.values, y_pred, average="binary", pos_label=0)


def train_predict(clf, X_train, y_train, X_test, y_test):
    train_classifier(clf, X_train, y_train)
    train_f1_score = predict_labels(clf, X_train, y_train)
    test_f1_score = predict_labels(clf, X_test, y_test)

    return train_f1_score, test_f1_score


def build_model(X, y, model_type):

    if model_type == 'svc':
        print('Training SVC Modeling')
        svr = SVC()
        parameters = {'kernel': ('linear', 'rbf'), 'C': [1, 10]}
        clf = grid_search.GridSearchCV(svr, parameters)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        train_f1_score, test_f1_score = train_predict(clf, X_train, y_train, X_test, y_test)
        print("F1 score for training set: {}".format(train_f1_score))
        print("F1 score for test set: {}".format(test_f1_score))
        print('Finished SVC Modeling')
        return clf
    elif model_type == 'gmm':
        print('Training GMM Modeling')
        sil_scores = []
        clf = mixture.GMM(n_components=3, covariance_type='full')
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        train_f1_score, test_f1_score = train_predict(clf, X_train, y_train, X_test, y_test)
        print("F1 score for training set: {}".format(train_f1_score))
        print("F1 score for test set: {}".format(test_f1_score))
        preds = clf.predict(X)
        # centers = np.round(clf.means_, 2)
        score = silhouette_score(X, preds)
        sil_scores.append(score)
        print('Scores :', sil_scores)
        print('Finished GMM Modeling')
        return clf
    elif model_type == 'kmeans':
        print('Training K-Means Modeling')
        clf = KMeans(init='k-means++', n_clusters=3, n_init=10)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        train_f1_score, test_f1_score = train_predict(clf, X_train, y_train, X_test, y_test)
        print("F1 score for training set: {}".format(train_f1_score))
        print("F1 score for test set: {}".format(test_f1_score))
        print('Finished SVC Modeling')
        print('Finished K-Means Modeling')
        return clf
    elif model_type == 'gnb':
        print('Training Gaussian NB Modeling')
        clf = GaussianNB()
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        train_f1_score, test_f1_score = train_predict(clf, X_train, y_train, X_test, y_test)
        print("F1 score for training set: {}".format(train_f1_score))
        print("F1 score for test set: {}".format(test_f1_score))
        print('Finished Gaussian NB Modeling')
        return clf


def build_tuned_model(X, y, model_type):

    if model_type == 'svc':
        print('Training and Tuning SVC Model')
        svr = SVC()
        gamma_range = np.logspace(-9, 3, 13)
        parameters = [{'kernel': ['rbf'], 'gamma': gamma_range, 'C': [1, 10, 100, 1000]}, {'kernel': ['linear'], 'C': [1, 10, 100,1000]}]
        clf = grid_search.GridSearchCV(svr, parameters)
        X_train, X_test, y_train, y_test = cross_validation.train_test_split(X, y, test_size=0.2, random_state=28)
        scores = cross_validation.cross_val_score(clf, X_train, y_train, cv=5)
        print(scores)
        print("Accuracy: %0.2f (+/- %0.2f)" % (scores.mean(), scores.std() * 2))
        print('Finished SVC Modeling')
    elif model_type == 'gmm':
        print('Training and Tuning GMM Model')
        co_types = ['spherical', 'tied', 'diag', 'full']
        skf = StratifiedKFold(y, n_folds=2, random_state=22)
        for train_index, test_index in skf:
            print("Shuffle")
            X_train, X_test = X.loc[train_index], X.loc[test_index]
            y_train, y_test = y.loc[train_index], y.loc[test_index]
            for co_type in co_types:
                print("W/ Covariance Type :: {}".format(co_type))
                sil_scores = []
                clf = mixture.GMM(n_components=3, covariance_type=co_type, random_state=34)
                clf.fit(X_train)
                preds = clf.predict(X_train)
                score = silhouette_score(X_train, preds)
                sil_scores.append(score)
                print('Scores :', sil_scores)
        print('Finished GMM Modeling')

    elif model_type == 'kmeans':
        print('Training K-Means Modeling')
        clf = KMeans(init='k-means++', n_clusters=3, n_init=10)
        X_train, X_test, y_train, y_test = cross_validation.train_test_split(X, y, test_size=0.2, random_state=28)
        scores = cross_validation.cross_val_score(clf, X_train, y_train, cv=5)
        print(scores)
        print("Accuracy: %0.2f (+/- %0.2f)" % (scores.mean(), scores.std() * 2))
        print('Finished K-Means Modeling')

    elif model_type == 'gnb':
        print('Training Gaussian NB Modeling')
        clf = GaussianNB()
        X_train, X_test, y_train, y_test = cross_validation.train_test_split(X, y, test_size=0.2, random_state=28)
        scores = cross_validation.cross_val_score(clf, X_train, y_train, cv=5)
        print(scores)
        print("Accuracy: %0.2f (+/- %0.2f)" % (scores.mean(), scores.std() * 2))
        print('Finished Gaussian NB Modeling')
