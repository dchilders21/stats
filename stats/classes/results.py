class FormulatePredictions(object):
    def __init__(self, **kwrargs):
        self.testing = kwrargs.get('testing') or False
        self.__get_data = kwrargs.get('get_data')
        self.__read_data = kwrargs.get('read_data')
        self.data_csv = kwrargs.get('data_csv')
        self.ranked_data_csv = kwrargs.get('ranked_data_csv'),
        self.upcoming_data_csv = kwrargs.get('ranked_data_csv')
        self.targets = kwrargs.get('targets')
        self.__build_tuned_model = kwrargs.get('build_tuned_model')
        self.__load_models = kwrargs.get('load_models')

        self.prediction_models = {}
        self.all_preds = {}
        self.upcoming_matches = kwrargs.get('upcoming_matches')
        self.upcoming_matches_csv = kwrargs.get('upcoming_matches_csv')
        self.__predictions = kwrargs.get('predictions')
        self.__data_frame = kwrargs.get('data_frame')
        self.__concat_data = kwrargs.get('concat_data')

        self.__get_rankings = kwrargs.get('get_rankings')
        self.td = kwrargs.get('td')
        self.previous_week_predictions = self.__data_frame()
        self.prev_week = kwrargs.get('prev_week')

    def modeling(self, target_X, target_y, target):
        print("Begin modeling...")
        for each in self.all_models:
            args = (target_X, target_y, each, self.td.strftime('%m_%d_%y'), target)
            r = self.__build_tuned_model(*args)

    def prediction(self):
        for target in self.targets:
            self.prediction_models[target] = self.__load_models(self.all_models, self.td.strftime('%m_%d_%y'), target)

    def find_predictions(self):
        """ Find predictions """
        for target in self.targets:
            for index, method in enumerate(self.all_models):
                preds = str(method) + '_' + str(target) + '_preds'
                print(preds)
                self.all_preds[preds] = self.prediction_models[target][index].predict(self.adjusted_upcoming_data)
                print(self.all_preds[preds])

                if target == 'points' and method == 'log':
                    self.probs = self.__data_frame(self.prediction_models[target][index].predict_proba(self.adjusted_upcoming_data))
                    self.probs = self.probs.rename(columns={0: 'Probability 0', 1: 'Probability 1', 2: 'Probability 2'})

    def predictions_reorder(self):
        columns = ['team_name', 'opp_name', 'scheduled', 'is_home', 'match_id']
        upcoming_matches = self.upcoming_data[columns]

        # Add predictions to the end of that DF
        results = self.__data_frame.from_dict(self.all_preds)
        upcoming_matches = self.__concat_data([upcoming_matches, results, self.probs], axis=1)
        self.reordered_matches = self.__data_frame([])

        for rows in upcoming_matches.iterrows():
            for i in upcoming_matches['team_name']:
                if rows[1]['opp_name'] == i:
                    self.reordered_matches = self.reordered_matches.append(rows[1])
                    self.reordered_matches = self.reordered_matches.append(upcoming_matches[upcoming_matches['team_name'].isin([i])])

        self.reordered_matches = self.reordered_matches.drop_duplicates()

    def predictions_compare(self):
        """ To compare when we have actual results"""
        actual_results = self.__read_data(self.data_csv)
        actual_results = actual_results.rename(columns={'Unnamed: 0': 'idx'})
        indexed_results = actual_results.set_index('idx')
        columns = ['team_name', 'opp_name', 'scheduled', 'is_home', 'match_id', 'points', 'goals']
        indexed_results = indexed_results[columns]
        self.previous_week_predictions = self.__read_data('../csv/soccer/{}/all_predictions.csv'.format(self.prev_week))
        self.previous_week_predictions = self.__concat_data([self.previous_week_predictions, indexed_results], axis=1)
        self.previous_week_predictions.to_csv('../csv/soccer/{}/actual_results.csv'.format(self.td.strftime('%m_%d_%y')))
        print('Actual Results compared with Last Weeks Predictions printed...')

    def predictions_save(self):
        self.reordered_matches = self.reordered_matches.reset_index(drop=True)
        self.reordered_matches.to_csv(self.predictions_csv)
        print('Prediction CSV saved')

    def init_raw_data(self):
        if self.testing:
            self.raw_data = self.__get_data()
            self.raw_data.to_csv(self.data_csv)
        else:
            self.raw_data = self.__read_data(self.data_csv)
            self.raw_data = self.raw_data.drop(self.raw_data.columns[[0]], axis=1)

        print('Data Loaded...')
        print("Dataset size :: {}".format(self.raw_data.shape))

    def init_ranked_data(self):
        if self.testing:
            args = (self.leagues, self.teams, self.rounds, self.raw_data, self.prev_week, False)
            self.ranked_data = self.__get_rankings(*args)
            self.ranked_data.to_csv(self.ranked_data_csv)
        else:
            self.ranked_data = self.__read_data(self.ranked_data_csv)
            self.ranked_data = self.ranked_data.drop(self.ranked_data.columns[[0]], axis=1)
        print('Ranked Data Loaded...')

    def init_upcoming_matches_data(self):
        self.upcoming_matches = self.upcoming_matches
        self.upcoming_matches.to_csv(self.upcoming_matches_csv)
        self.upcoming_data = self.__predictions(self.upcoming_matches)

    def init_ranked_upcoming_matches_data(self):
        if self.testing:
            args = (self.adjusted_leagues, self.teams, self.adjusted_league_rounds, self.upcoming_data, self.prev_week, True)
            self.upcoming_ranked_data = self.__get_rankings(*args)
            self.upcoming_ranked_data.to_csv(self.ranked_upcoming_matches_csv)
        else:
            self.upcoming_ranked_data = self.__read_data(self.ranked_upcoming_matches_csv)
            self.upcoming_ranked_data = self.upcoming_ranked_data.drop(self.upcoming_ranked_data.columns[[0]], axis=1)
        print('Loaded Upcoming Data...')
