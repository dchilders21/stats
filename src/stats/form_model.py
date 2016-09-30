from sklearn.metrics import f1_score
from sklearn import mixture
import numpy as np
import os
from sklearn.svm import SVC
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn import grid_search
from sklearn import cross_validation
from sklearn import linear_model
from sklearn.metrics import roc_auc_score
from sklearn.externals import joblib
from sklearn.cross_validation import train_test_split
from sklearn.cross_validation import StratifiedKFold
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier


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


def train_models(round_num, X, y, models):
    if os.path.isdir("/models/" + str(round_num)):
        print('Making New Directory for the Round')
        os.chdir('/Users/senzari/Machine_Learning/stats/src/models')
        os.makedirs(str(round_num))
        os.chdir('/Users/senzari/Machine_Learning/stats/src')

    finished_models = []

    for i in models:

        model_round = 'models/' + str(round_num) + '/' + str(i) + '_round_' + str(round_num) + '.pk1'

        if i == 'log':
            log = build_model(X, y, i)
            joblib.dump(log, model_round)
            finished_models.append(log)
        elif i == 'svc':
            svc = build_model(X, y, i)
            joblib.dump(svc, model_round)
            finished_models.append(svc)
        elif i == 'gmm':
            gmm = build_model(X, y, i)
            joblib.dump(gmm, model_round)
            finished_models.append(gmm)
        elif i == 'knn':
            kmeans = build_model(X, y, i)
            joblib.dump(kmeans, model_round)
            finished_models.append(kmeans)
        elif i == 'gnb':
            gnb = build_model(X, y, i)
            joblib.dump(gnb, model_round)
            finished_models.append(gnb)
        elif i == 'randomForest':
            rF = build_model(X, y, i)
            joblib.dump(rF, model_round)
            finished_models.append(rF)

    return finished_models


def load_models(models):
    loaded_models = []

    for i in models:
        model_round = 'models/tuned/' + str(i)
        if i == 'log':
            log = joblib.load(model_round)
            loaded_models.append(log)
        if i == 'svc':
            svc = joblib.load(model_round)
            loaded_models.append(svc)
        elif i == 'gmm':
            gmm = joblib.load(model_round)
            loaded_models.append(gmm)
        elif i == 'knn':
            kmeans = joblib.load(model_round)
            loaded_models.append(kmeans)
        elif i == 'gnb':
            gnb = joblib.load(model_round)
            loaded_models.append(gnb)
        elif i == 'randomForest':
            rf = joblib.load(model_round)
            loaded_models.append(rf)

        print("Success :: Loaded - " + str(i))

    return loaded_models


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
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        neigh.fit(X_train, y_train)
        print('KNN Score on Training Set :: {}'.format(neigh.score(X_train, y_train)))
        print('KNN Score on Test Set:: {}'.format(neigh.score(X_test, y_test)))
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
    elif model_type == 'randomForest':
        print('-----------------------------------')
        print('Random Forest Classifier Model')
        clf = RandomForestClassifier(max_depth=5, n_estimators=10, max_features=1)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        train_f1_score, test_f1_score = train_predict(clf, X_train, y_train, X_test, y_test)
        print("Training set: {}".format(train_f1_score))
        print("Test set: {}".format(test_f1_score))
        print('Finished Random Forest Classifier Modeling')
        return clf


def build_tuned_model(X, y, model_type):

    finished_models = []

    tuned_folder = 'models/tuned/' + str(model_type)

    if model_type == 'svc':
        print('Training and Tuning SVC Model')
        svr = SVC(probability=True)
        parameters = [{'kernel': ['rbf'], 'C': [1, 10, 100]}]
        clf = grid_search.GridSearchCV(svr, parameters)
        X_train, X_test, y_train, y_test = cross_validation.train_test_split(X, y, test_size=0.2, random_state=28)
        scores = cross_validation.cross_val_score(clf, X_train, y_train, cv=2)
        print(scores)
        print("Accuracy: %0.2f (+/- %0.2f)" % (scores.mean(), scores.std() * 2))
        print('Finished SVC Modeling')
        clf.fit(X_train, y_train)
        joblib.dump(clf, tuned_folder)
        finished_models.append(clf)
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
        joblib.dump(clf, tuned_folder)
        finished_models.append(clf)

    elif model_type == 'knn':
        print('-----------------------------------')
        print('Training K-Means Model')
        skf = StratifiedKFold(y, n_folds=5, random_state=22)
        for train_index, test_index in skf:
            X_train, X_test = X.loc[train_index], X.loc[test_index]
            y_train, y_test = y.loc[train_index], y.loc[test_index]
            neigh = KNeighborsClassifier(n_neighbors=2)
            neigh.fit(X_train, y_train)
            train_score = neigh.score(X_train, y_train)
            test_score = neigh.score(X_test, y_test)
            print('KNN Score :: {} for Training'.format(train_score))
            print('KNN Score :: {} for Testing'.format(test_score))
        print('Finished K-Means Modeling')
        joblib.dump(neigh, tuned_folder)
        finished_models.append(neigh)

    elif model_type == 'gnb':
        print('-----------------------------------')
        print('Training Gaussian NB Model')
        clf = GaussianNB()
        X_train, X_test, y_train, y_test = cross_validation.train_test_split(X, y, test_size=0.2, random_state=28)
        scores = cross_validation.cross_val_score(clf, X_train, y_train, cv=5)
        print(scores)
        print("Accuracy: %0.2f (+/- %0.2f)" % (scores.mean(), scores.std() * 2))
        print('Finished Gaussian NB Modeling')
        clf.fit(X_train, y_train)
        joblib.dump(clf, tuned_folder)
        finished_models.append(clf)

    elif model_type == 'randomForest':
        print('-----------------------------------')
        print('Training Random Forest Model')
        #for i in range(1, 2):
        clf = RandomForestClassifier(max_depth=5, n_estimators=11, max_features=2, class_weight='balanced')
        X_train, X_test, y_train, y_test = cross_validation.train_test_split(X, y, test_size=0.2, random_state=28)
        scores = cross_validation.cross_val_score(clf, X_train, y_train, cv=5)
        print(scores)
        print("Accuracy: %0.2f (+/- %0.2f)" % (scores.mean(), scores.std() * 2))
        print('Finished Random Forest Modeling')
        clf.fit(X_train, y_train)
        joblib.dump(clf, tuned_folder)
        finished_models.append(clf)

    elif model_type == 'log':
        print('Training LOG REG Model')
        logreg = linear_model.LogisticRegression(C=1e5, class_weight='balanced')
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        logreg.fit(X_train, y_train)
        train_scores = logreg.score(X_train, y_train)
        print('Score on Training Set :: {}'.format(train_scores))
        test_scores = logreg.score(X_test, y_test)
        print('Score on Test Set :: {}'.format(test_scores))
        print('Finished LOG REG Modeling')
        joblib.dump(logreg, tuned_folder)
        finished_models.append(logreg)

    return finished_models
