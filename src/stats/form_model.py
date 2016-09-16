from sklearn.metrics import f1_score
from sklearn import mixture
import numpy as np
from sklearn.svm import SVC
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn import grid_search
from sklearn import cross_validation
from sklearn import linear_model
from sklearn.metrics import roc_auc_score
from sklearn.cross_validation import train_test_split
from sklearn.cross_validation import StratifiedKFold
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier


def train_classifier(clf, X_train, y_train):
    clf.fit(X_train, y_train)


def predict_labels(clf, features, target):
    y_pred = clf.predict(features)
    return f1_score(target.values, y_pred, average="macro", pos_label=0)


def train_predict(clf, X_train, y_train, X_test, y_test):
    train_classifier(clf, X_train, y_train)
    train_f1_score = predict_labels(clf, X_train, y_train)
    test_f1_score = predict_labels(clf, X_test, y_test)

    return train_f1_score, test_f1_score


def build_model(X, y, model_type):

    if model_type == 'log':
        print('Training LOG REG Model')
        logreg = linear_model.LogisticRegression(C=1e5)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        logreg.fit(X_train, y_train)
        train_scores = logreg.score(X_train, y_train)
        print('Score on Training Set :: {}'.format(train_scores))
        test_scores = logreg.score(X_test, y_test)
        print('Score on Test Set :: {}'.format(test_scores))
        print('Finished LOG REG Modeling')
        return logreg
    elif model_type == 'svc':
        print('-----------------------------------')
        print('Training SVC Model')
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
        print('-----------------------------------')
        print('Training GMM Modeling')
        sil_scores = []
        for i in range(2, 4):
            clf = mixture.GMM(n_components=i, covariance_type='full')
            clf.fit(X)
            preds = clf.predict(X)
            # centers = np.round(clf.means_, 2)
            score = silhouette_score(X, preds)
            sil_scores.append(score)
            print('Silhouette Score :: {} for {} Clusters'.format(score, i))
        print('Finished GMM Modeling')
        return clf
    elif model_type == 'knn':
        print('-----------------------------------')
        print('Training K Neighbors Classifier Model')
        neigh = KNeighborsClassifier(n_neighbors=2)
        neigh.fit(X, y)
        score = neigh.score(X, y)
        print('KNN Score :: {}'.format(score))
        print('Finished K-Means Modeling')
        return neigh
    elif model_type == 'gnb':
        print('-----------------------------------')
        print('Training Gaussian NB Model')
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
        scores = cross_validation.cross_val_score(clf, X_train, y_train, cv=2)
        print(scores)
        print("Accuracy: %0.2f (+/- %0.2f)" % (scores.mean(), scores.std() * 2))
        print('Finished SVC Modeling')
    elif model_type == 'gmm':
        print('-----------------------------------')
        print('Training and Tuning GMM Model')
        co_types = ['spherical', 'tied', 'diag', 'full']
        skf = StratifiedKFold(y, n_folds=5, random_state=22)
        for train_index, test_index in skf:
            X_train, X_test = X.loc[train_index], X.loc[test_index]
            y_train, y_test = y.loc[train_index], y.loc[test_index]
            for co_type in co_types:
                print("W/ Covariance Type :: {}".format(co_type))
                train_sils = []
                test_sils = []
                for i in range(2, 5):
                    print('# of Components :: {}'.format(i))
                    clf = mixture.GMM(n_components=i, covariance_type=co_type, random_state=34)
                    clf.fit(X_train)
                    train_preds = clf.predict(X_train)
                    train_score = silhouette_score(X_train, train_preds)
                    test_preds = clf.predict(X_test)
                    test_score = silhouette_score(X_test, test_preds)
                    train_sils.append(train_score)
                    test_sils.append(test_score)
                    print('Silhouette Score :: {} for Training'.format(train_score))
                    print('Silhouette Score :: {} for Testing'.format(test_score))

        print('Finished GMM Modeling')

    elif model_type == 'knn':
        print('-----------------------------------')
        print('Training K-Means Model')
        skf = StratifiedKFold(y, n_folds=5, random_state=22)
        for train_index, test_index in skf:
            X_train, X_test = X.loc[train_index], X.loc[test_index]
            y_train, y_test = y.loc[train_index], y.loc[test_index]
            neigh = KNeighborsClassifier(n_neighbors=3)
            neigh.fit(X_train, y_train)
            train_score = neigh.score(X_train, y_train)
            test_score = neigh.score(X_test, y_test)
            print('KNN Score :: {} for Training'.format(train_score))
            print('KNN Score :: {} for Testing'.format(test_score))
        print('Finished K-Means Modeling')

    elif model_type == 'gnb':
        print('-----------------------------------')
        print('Training Gaussian NB Model')
        clf = GaussianNB()
        X_train, X_test, y_train, y_test = cross_validation.train_test_split(X, y, test_size=0.2, random_state=28)
        scores = cross_validation.cross_val_score(clf, X_train, y_train, cv=5)
        print(scores)
        print("Accuracy: %0.2f (+/- %0.2f)" % (scores.mean(), scores.std() * 2))
        print('Finished Gaussian NB Modeling')
