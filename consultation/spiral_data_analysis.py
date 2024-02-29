import glob
import os
import time

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn import metrics
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import joblib


class FeatureEngineering:
    def __init__(self, spiral_data):
        self.center = [200, 200]
        self.end = [400, 200]
        self.turns = 3
        self.spiral = pd.DataFrame()
        self.spiral2 = pd.DataFrame()
        self.errors = pd.DataFrame()

        self.spiral_data = spiral_data

    def pull_tests(self, input):
        pd_data = input[input['Test ID'] == 0].copy()
        return pd_data

    def gen_data(self, df):
        turns = 0
        df.loc[:, 'Time'] = df['Time'] - df['Time'].iloc[0]
        if df['Time'].iloc[-1] > 100:
            df.loc[:, 'Time'] = df['Time'] / 1000
        df.loc[:, 'X'] = df['Plot X'] - 200
        df.loc[:, 'Y'] = df['Plot Y'] - 200
        df.loc[:, 'Theta'] = np.arctan2(df['Y'], df['X'])

        df.loc[:, 'Angular Velocity'] = df['Theta'].diff()

        for index, row in df.iterrows():
            if abs(row['Angular Velocity']) >= 6.2:
                turns += 1
            df.loc[index, 'Theta'] = abs((row['Theta'] - turns * 2 * np.pi))

        df.loc[:, 'Angular Velocity'] = df['Theta'].diff() / df['Time'].diff()
        df.loc[:, 'Magnitude'] = np.linalg.norm(df[['X', 'Y']], axis=1)
        df.loc[:, 'Dist'] = np.linalg.norm(df[['X', 'Y']].diff(axis=0, periods=20), axis=1)
        df.loc[:, 'Drawing Speed'] = df['Dist'] / (df['Time'].diff(periods=20))
        return df

    def gen_spiral(self, df):
        self.spiral = pd.DataFrame()
        n = len(df)
        b = np.linalg.norm(np.array(self.end) - np.array(self.center)) / (self.turns * 2 * np.pi)
        self.spiral.loc[:, 'Time'] = np.linspace(0, (df['Time'].iloc[-1]) - (df['Time'].iloc[0]), n)
        self.spiral['Theta'] = np.sqrt(np.linspace(0, (self.turns * 2 * np.pi) ** 2, n))
        # self.spiral['Theta'] = np.linspace(0, (self.turns * 2 * np.pi), n)

        self.spiral.loc[:, 'X'] = (b * self.spiral['Theta']) * np.cos(-self.spiral['Theta'])
        self.spiral.loc[:, 'Y'] = (b * self.spiral['Theta']) * np.sin(-self.spiral['Theta'])

        self.spiral.loc[:, 'Magnitude'] = np.linalg.norm(self.spiral[['X', 'Y']], axis=1)
        self.spiral.loc[:, 'Angular Velocity'] = self.spiral['Theta'].diff(periods=20) / self.spiral['Time'].diff(
            periods=20)
        self.spiral.loc[:, 'Dist'] = np.linalg.norm(self.spiral[['X', 'Y']].diff(axis=0, periods=20), axis=1)
        self.spiral.loc[:, 'Drawing Speed'] = self.spiral['Dist'] / (self.spiral['Time'].diff(periods=20))

    def gen_spiral_time(self, df, Y):
        self.spiral_time = pd.DataFrame()

        b = np.linalg.norm(np.array(self.end) - np.array(self.center)) / (self.turns * 2 * np.pi)
        self.spiral_time.loc[:, 'Time'] = df['Time']
        # # normalised=df['Time']/max(df['Time'])
        if Y == 'Magnitude':
            self.spiral_time['Theta'] = df['Theta']
            self.spiral_time.loc[:, 'X'] = (b * self.spiral_time['Theta']) * np.cos(-self.spiral_time['Theta'])
            self.spiral_time.loc[:, 'Y'] = (b * self.spiral_time['Theta']) * np.sin(-self.spiral_time['Theta'])
            self.spiral_time.loc[:, 'Magnitude'] = abs(np.linalg.norm(self.spiral_time[['X', 'Y']], axis=1))
        elif Y == 'Theta':
            self.spiral_time['Magnitude'] = df['Magnitude']
            n = len(df['Magnitude'])
            theta = (np.linspace(0, self.turns * 2 * np.pi, n))
            index = np.round((self.spiral_time['Magnitude'] / max(self.spiral_time['Magnitude'])) * (n - 1)).astype(int)
            self.spiral_time['Theta'] = theta[index]
            self.spiral_time.loc[:, 'X'] = (b * self.spiral_time['Theta']) * np.cos(-self.spiral_time['Theta'])
            self.spiral_time.loc[:, 'Y'] = (b * self.spiral_time['Theta']) * np.sin(-self.spiral_time['Theta'])
        else:
            n = len(df['Time'])
            self.spiral_time['Theta'] = np.sqrt(np.linspace(0, (self.turns * 2 * np.pi) ** 2, n))
            self.spiral_time.loc[:, 'X'] = (b * self.spiral_time['Theta']) * np.cos(-self.spiral_time['Theta'])
            self.spiral_time.loc[:, 'Y'] = (b * self.spiral_time['Theta']) * np.sin(-self.spiral_time['Theta'])
            self.spiral_time.loc[:, 'Magnitude'] = abs(np.linalg.norm(self.spiral_time[['X', 'Y']], axis=1))
            self.spiral_time.loc[:, 'Angular Velocity'] = self.spiral_time['Theta'].diff(periods=20) / self.spiral_time[
                'Time'].diff(periods=20)
            self.spiral_time.loc[:, 'Dist'] = np.linalg.norm(self.spiral_time[['X', 'Y']].diff(axis=0, periods=20),
                                                             axis=1)
            self.spiral_time.loc[:, 'Drawing Speed'] = self.spiral_time['Dist'] / (
                self.spiral_time['Time'].diff(periods=20))

    def get_closest_coords(self, df):
        self.closest_coords = pd.DataFrame()
        spiral_points = list(zip(self.spiral['X'], self.spiral['Y']))
        for i in range(len(df)):
            distances = np.linalg.norm(spiral_points - np.array([df['X'].iloc[i], df['Y'].iloc[i]]), axis=1)
            closest_idx = np.argmin(distances)
            self.closest_coords.loc[i, 'X'] = self.spiral.loc[closest_idx, 'X']
            self.closest_coords.loc[i, 'Y'] = self.spiral.loc[closest_idx, 'Y']
            self.closest_coords.loc[i, 'Error'] = min(distances)

        self.closest_coords.loc[:, 'Time'] = df['Time']
        self.closest_coords.loc[:, 'Theta'] = np.arctan2(df['Y'], df['X'])
        self.closest_coords.loc[:, 'Angular Velocity'] = df['Theta'].diff()
        turns = 0
        for index, row in self.closest_coords.iterrows():
            if abs(row['Angular Velocity']) >= 6:
                turns += 1
            self.closest_coords.loc[index, 'Theta'] = abs(row['Theta'] - turns * 2 * np.pi)

        self.closest_coords.loc[:, 'Angular Velocity'] = self.closest_coords['Theta'].diff() / self.closest_coords[
            'Time'].diff()
        self.closest_coords.loc[:, 'Magnitude'] = np.linalg.norm(self.closest_coords[['X', 'Y']], axis=1)
        self.closest_coords.loc[:, 'Dist'] = np.linalg.norm(self.closest_coords[['X', 'Y']].diff(axis=0, periods=20),
                                                            axis=1)
        self.closest_coords.loc[:, 'Drawing Speed'] = self.closest_coords['Dist'] / (
            self.closest_coords['Time'].diff(periods=20))

    def plot_graph(self, X, Y, file_name):
        if X == 'Time':
            plt.scatter(self.spiral_time[X], self.spiral_time[Y], s=0.09)
        else:
            plt.scatter(self.spiral[X], self.spiral[Y], s=0.09)
        for df in self.dfs.values():
            plt.scatter(df[X], df[Y], s=0.09)

        plt.xlabel(X)
        plt.ylabel(Y)
        plt.grid(True)
        plt.title(str(file_name))
        plt.show()
        # plt.savefig(\Generated)

    # def plot_graphs(self):
    #     self.plot_graph('X', 'Y' )
    #     self.plot_graph('Theta', 'Magnitude')
    #     self.plot_graph('Time', 'Drawing Speed')
    #     self.plot_graph('Time', 'Magnitude')
    #     self.plot_graph('Time','Theta')        # self.plot_graph('Time', 'Angular Velocity')

    def sum_error(self, X, Y):
        for name, df in self.dfs.items():
            df.reset_index(drop=True, inplace=True)
            if X == 'Time':
                self.gen_spiral_time(df, Y)
                error = abs(df[Y] - self.spiral_time[Y])
                error_diff = abs(error.diff() / df[X].diff())
                error_diff.replace(np.inf, 0, inplace=True)
            else:
                self.gen_spiral(df)
                self.get_closest_coords(df)
                error = abs(df[X] - self.closest_coords[X]) + abs(df[Y] - self.closest_coords[Y])
                errorX = abs(df[X] - self.closest_coords[X])
                sum_errorX = errorX.sum() / len(df[X])
                string = '_'.join([X, 'closest_error'])
                self.errors.at[self.index, string] = sum_errorX
                errorY = abs(df[Y] - self.closest_coords[Y])
                sum_errorY = errorY.sum() / len(df[Y])
                string = '_'.join([Y, 'closest_error'])
                self.errors.at[self.index, string] = sum_errorY
                error_diff = abs(error.diff() / df[X].diff())
                error_diff.replace(np.inf, 0, inplace=True)
            sum_error = error.sum() / len(df[X])
            sum_error_diff = error_diff.sum() / len(df[X])
            string1 = '_'.join([X, Y])
            self.errors.at[self.index, string1] = sum_error
            string2 = '_'.join([X, Y, 'diff'])
            self.errors.at[self.index, string2] = sum_error_diff

    # def sum_error_closest(self, X, Y):
    #     for name, df in self.dfs.items():
    #         df.reset_index(drop=True, inplace=True)
    #         squared_error = (abs(df[X] - self.spiral[X]) + abs(df[Y] - self.spiral[Y]))
    #         sum_squared_error = squared_error.sum() / len(df[X])
    #         string = '_'.join([name, X, Y])
    #         self.errors.at[self.index, string] = sum_squared_error

    def final_value(self, Y):
        for name, df in self.dfs.items():
            string = '_'.join([Y, 'Final'])
            self.errors.at[self.index, string] = df[Y].iloc[-1]

    def std(self, Y):
        for name, df in self.dfs.items():
            string = '_'.join([Y, 'std'])
            self.errors.at[self.index, string] = df[Y].std()

    def calc_errors(self, file_name):
        self.sum_error('Theta', 'Magnitude')
        self.plot_graph('Theta', 'Magnitude', file_name)
        self.plot_graph('X', 'Y', file_name)
        self.sum_error('Time', 'Drawing Speed')
        self.plot_graph('Time', 'Drawing Speed', file_name)
        self.sum_error('Time', 'Angular Velocity')
        # self.plot_graph('Time', 'Angular Velocity',file_name)
        self.sum_error('Time', 'Magnitude')
        self.plot_graph('Time', 'Magnitude', file_name)
        self.std('Theta')
        self.std('Magnitude')
        self.std('Drawing Speed')
        self.final_value('Time')

    def plot_file(self, test, input, file):
        base_path = r'C:/Users/Thinkpad/Desktop/Warwick/hero-monitor/data/parkinsons_data'
        file_path = os.path.join(base_path, input, file)
        if test == 'SST':
            pd_data = pd.read_csv(file_path, delimiter=';', header=None,
                                  names=['Plot X', 'Plot Y', 'Z', 'Pressure', 'GripAngle', 'Time', 'Test ID'])
            pd_data = self.pull_tests(pd_data)
        if test == 'Manual':
            pd_data = pd.read_csv(file_path, delimiter=';')

        self.spiral = pd.DataFrame()
        self.errors = pd.DataFrame()
        self.index = 0
        print(pd_data)
        pd_data = self.gen_data(pd_data)
        self.dfs = {'_'.join([file, test]): pd_data}
        file_name = '_'.join([test, input, file, 'error_test.txt'])
        self.calc_errors(file_name)
        self.errors.to_csv(file_name, sep=';', index=False)

    def loop_SST(self, input):
        print(f"Calculating errors for {input} SST ...")
        self.errors = pd.DataFrame()
        base_path = r'C:/Users/Thinkpad/Desktop/Warwick/hero-monitor/data/parkinsons_data/hw_dataset'
        folder_path = os.path.join(base_path, input)
        file_list = glob.glob(os.path.join(folder_path, '*.txt'))
        print(file_list)
        self.index = 0
        for file_index, file_path in enumerate(file_list):
            file_name = os.path.basename(os.path.normpath(file_path))
            print(file_name)
            self.index = file_index
            pd_data = pd.read_csv(file_path, delimiter=';')
            if file_name[0] == 'C' or file_name[0] == 'P' or file_name[0] == 'H':
                pd_data = pd.read_csv(file_path, delimiter=';', header=None,
                                      names=['Plot X', 'Plot Y', 'Z', 'Pressure', 'GripAngle', 'Time', 'Test ID'])
                pd_data = self.pull_tests(pd_data)
            print(pd_data)
            pd_data = self.gen_data(pd_data)
            self.dfs = {'SST': pd_data}
            self.calc_errors(file_name)
            # self.plot_graphs(file_name)
            time.sleep(1)

        # Create the "SST" folder if it does not exist
        folder_path = r'C:/Users/Thinkpad/Desktop/Warwick/hero-monitor/data'
        sst_folder = os.path.join(folder_path, 'SST')
        os.makedirs(sst_folder, exist_ok=True)

        # Save the CSV file inside the "SST" folder
        file_name = os.path.join(sst_folder, f'{input}_error_squared.txt')
        self.errors['File'] = [os.path.basename(os.path.normpath(path)) for path in file_list]
        self.errors.to_csv(file_name, sep=';', index=False)
        print('Done')

    def process_data(self):
        self.index = 0

        self.errors = pd.DataFrame()

        spiral_data = self.gen_data(self.spiral_data)
        self.gen_spiral(spiral_data)
        self.dfs = {'USER': spiral_data}
        self.calc_errors('User')
        self.errors.to_csv(r'data\user_drawing\user_spiral_errors.txt', sep=';', index=False)

        with open('columns_for_training.txt', 'r') as file:
            lines = file.readlines()

        include_indices = [index for index, line in enumerate(lines) if line.startswith('1')]
        # print(include_indices)
        new_errors = self.errors.iloc[:, include_indices]
        new_errors.to_csv(r'user_drawing\selected_user_spiral_errors.txt',
                          sep=';', index=False)
        return new_errors


class DataAnalytics:
    def __init__(self, spiral_data):
        self.spiral_data = spiral_data
        self.probability = None
        self.classification = None

    def extract_errors(self):
        # List of folders to open
        folders_to_open = ['SST']
        data_path = ""
        with open('columns_for_training.txt', 'r') as file:
            lines = file.readlines()

        include_indices = [index for index, line in enumerate(lines) if line.startswith('1')]
        include_indices.extend([len(lines)])
        # print(include_indices)
        for folder in folders_to_open:
            folder_path = os.path.join(data_path, folder)
            control_error_file = os.path.join(folder_path, 'control_error.txt')
            parkinsons_error_file = os.path.join(folder_path, 'parkinson_error.txt')

            control_error_data = pd.read_csv(control_error_file, sep=';')
            control_error_data = control_error_data.iloc[:, include_indices]
            control_error_data['Catagory'] = 0

            parkinsons_error_data = pd.read_csv(parkinsons_error_file, sep=';')
            parkinsons_error_data = parkinsons_error_data.iloc[0:14, include_indices]
            parkinsons_error_data['Catagory'] = 1
            train_ratio = 0.7

            control_error_data = control_error_data.sample(frac=1).reset_index(drop=True)
            parkinsons_error_data = parkinsons_error_data.sample(frac=1).reset_index(drop=True)

            # print(control_error_data.columns)

            c_test = control_error_data.iloc[:-(round(train_ratio * len(control_error_data))), :]
            p_test = parkinsons_error_data.iloc[:-(round(train_ratio * len(parkinsons_error_data))), :]
            c_train = control_error_data.iloc[(round((1 - train_ratio) * len(control_error_data))):, :]
            p_train = parkinsons_error_data.iloc[(round((1 - train_ratio) * len(parkinsons_error_data))):, :]

            test = pd.concat([c_test, p_test])
            train = pd.concat([c_train, p_train])
            whole_set = pd.concat([control_error_data, parkinsons_error_data])

            whole_set.to_csv(r'user_drawing/whole_set_errors.txt', sep=';', index=False)

        return train, test, whole_set

    def box_plots(self, data):
        for col in data[:-1]:
            if col != 'File':
                plt.boxplot([data[col].dropna(), data[col].dropna()],
                            labels=['control', 'parkinson'])
                plt.xlabel('Data Sets')
                plt.ylabel(col)
                plt.title('Box Plot of Different Data Sets')
                plt.show()

    def confusion_matrix(self, classification):
        if col != 'File' and col != 'Catagory':
            confusion_matrix = metrics.confusion_matrix(classification['Final C'], classification['Catagory'])
            cm_display = metrics.ConfusionMatrixDisplay(confusion_matrix=confusion_matrix,
                                                        display_labels=['Healthy',
                                                                        'Parkinsons'])  # Assuming Category values are 0 and 1
            cm_display.plot()
            plt.title(f'Confusion Matrix for Test Data')
            plt.show()

    def regression(self, train_data):
        Y = np.array(train_data['Catagory'])
        for col in train_data.columns[:-1]:
            if col != 'File':
                X = np.array(train_data[col])

                model = LogisticRegression()
                model.fit(X.reshape(-1, 1), Y)

                model_filename = f"{col}_model.joblib"
                joblib.dump(model, model_filename)

    def random_forest(self, train_data):
        Y = np.array(train_data['Catagory'])
        features = train_data.columns.difference(['File', 'Catagory'])
        X = np.array(train_data[features])

        model = RandomForestClassifier(max_depth=2)
        model.fit(X, Y)

        model_filename = 'random_forest_model.joblib'
        joblib.dump(model, model_filename)

    def get_prob_reg(self, test_data, name):

        if 'File' in test_data.columns:
            prediction = pd.DataFrame()
            classification = pd.DataFrame()

            prediction['File'] = test_data['File'].copy()
            prediction['Catagory'] = test_data['Catagory'].copy()
            classification['File'] = test_data['File'].copy()
            classification['Catagory'] = test_data['Catagory'].copy()

            for col in test_data.columns[:-2]:
                if col != 'File' and col != 'Catagory':
                    model_filename = f"{col}_model.joblib"
                    model = joblib.load(model_filename)
                    X = np.array(test_data[col])
                    odds = model.coef_ * X + model.intercept_
                    odds = np.exp(odds)
                    probability = odds / (1 + odds)
                    prediction[col] = probability.reshape(-1, 1)
                    classification[col] = model.predict(X.reshape(-1, 1))

            test_data['Final P'] = prediction.iloc[:, 2:].mean(axis=1)
            test_data['Final C'] = (test_data['Final P'] > 0.5).astype(int)
        else:

            numeric_values = self.spiral_data.select_dtypes(include='number')
            print(numeric_values)

            predictions = []
            classifications = []
            for col in numeric_values:
                model_filename = f"{col}_model.joblib"
                model = joblib.load(model_filename)
                X = np.array(test_data[col])
                odds = model.coef_ * X + model.intercept_

                # sigmoid activation
                odds = np.exp(odds)
                probability = odds / (1 + odds)

                predictions.append(probability[0, 0])
                classifications.append(model.predict(X.reshape(-1, 1)))

            self.probability = sum(predictions) / len(predictions)
            self.classification = round(self.probability)

    def classify(self):
        numeric_values: pd.DataFrame = self.spiral_data.select_dtypes(include='number')

        models = [joblib.load(f"{predictor}_model.joblib") for predictor in numeric_values.columns]

        predictions = []
        classifications = []
        for col in numeric_values:
            model_filename = f"{col}_model.joblib"
            model = joblib.load(model_filename)
            X = np.array(numeric_values.loc[0, col])
            odds = model.coef_ * X + model.intercept_

            #
            odds = np.exp(odds)
            probability = odds / (1 + odds)

            predictions.append(probability[0, 0])
            classifications.append(model.predict(X.reshape(-1, 1)))

        self.probability = sum(predictions) / len(predictions)
        self.classification = round(self.probability)

    def get_prob_rf(self, test_data, name):
        model_filename = "random_forest_model.joblib"
        model = joblib.load(model_filename)

        if 'File' in test_data.columns:
            features = test_data.columns.difference(['File', 'Catagory'])
            X = np.array(test_data[features])
            probabilities = model.predict_proba(X)
            test_data['Final P'] = probabilities[:, 1]
            test_data['Final C'] = model.predict(X)
            feature_importances = pd.DataFrame({
                'Feature': features,
                'Importance': model.feature_importances_})
            test_data.to_csv(f'Classifications/{name}_prediction.txt', sep=';', index=False)
            feature_importances.to_csv(f'Classifications/{name}_feature_importance.txt', sep=';', index=False)
        else:
            features = test_data.columns
            X = np.array(test_data[features])
            model_filename = "random_forest_model.joblib"
            model = joblib.load(model_filename)

            # Get probability estimates for each class
            probabilities = model.predict_proba(X)
            test_data.loc[:, 'Final P'] = probabilities[:, 1]
            test_data.loc[:, 'Final C'] = model.predict(X)
            print(test_data.loc[:, 'Final C'])
            print(test_data.loc[:, 'Final P'])

            test_data.to_csv(f'Classifications/{name}_prediction.txt', sep=';', index=False)

    def error_graphs(self):
        whole_set = pd.read_csv(r'Classifications/whole_set_prediction.txt', sep=';')
        # print(whole_set)
        test = pd.read_csv(r'Classifications/user_data_prediction.txt', sep=';')
        # print(test)
        for col in test:
            plt.scatter(whole_set[col][whole_set['Final C'] == 0], whole_set['Final P'][whole_set['Final C'] == 0],
                        color='blue', label='z=0')
            plt.scatter(whole_set[col][whole_set['Final C'] == 1], whole_set['Final P'][whole_set['Final C'] == 1],
                        color='red', label='z=1')
            plt.scatter(test[col][test['Final C'] == 0], test['Final P'][test['Final C'] == 0],
                        color='blue', label='z=0', marker='s')
            plt.scatter(test[col][test['Final C'] == 1], test['Final P'][test['Final C'] == 1],
                        color='red', label='z=1', marker='s')
            plt.xlabel(str(col))
            plt.ylabel('Probability')
            plt.title(whole_set['File'].iloc[0])
            plt.show()

        file_path = r'user_drawing/user_spiral_errors.txt'
        test = pd.read_csv(file_path, sep=';')

    def user_classify(self, type, file_path):
        test = pd.read_csv(file_path, sep=';')
        prediction = pd.DataFrame()
        classification = pd.DataFrame()
        # print(test.columns)
        if type == 'Logistic':
            for col in test.columns:
                if col != 'File':
                    model_filename = f"{col}_model.joblib"
                    model = joblib.load(model_filename)
                    X = np.array([test[col]])
                    odds = model.coef_ * X + model.intercept_
                    odds = np.exp(odds)
                    probability = odds / (1 + odds)
                    # print(probability)
                    prediction[col] = probability[0]
                    classification[col] = model.predict(X)
            test['Final P'] = prediction.sum(axis=1)
            classification = classification.sum(axis=1)
            test['Final C'] = classification.apply(lambda x: 0 if x < 0.5 else 1)
            print(test['Final C'])
            print(test['Final P'])

            test.to_csv('prediction.txt', sep=';', index=False)

        elif type == 'RF':
            features = test.columns
            X = np.array(test[features])
            model_filename = "random_forest_model.joblib"
            model = joblib.load(model_filename)

            # Get probability estimates for each class
            probabilities = model.predict_proba(X)
            test['Final P'] = probabilities[:, 1]
            test['Final C'] = model.predict(X)
            print(test['Final C'])
            print(test['Final P'])

            test.to_csv('prediction.txt', sep=';', index=False)

        return test


if __name__ == "__main__":
    # os.chdir('/Users/Thinkpad/Desktop/Warwick/hero-monitor/data')
    os.chdir("/Users/benhoskings/Documents/Pycharm/Hero_Monitor/data")


    def final_gen_SST():
        data = FeatureEngineering()
        data.loop_SST('control')
        data.loop_SST('parkinson')


    def final_train_model():
        spiral = DataAnalytics()
        train, test, whole_set = spiral.extract_errors()
        # spiral.regression(train)
        spiral.get_prob_reg(test, 'test')
        spiral.get_prob_reg(whole_set, 'whole_set')
        # test_output,test_feature_importance=spiral.get_prob_rf(test)
        # test_output.to_csv(r'\SST\test_output.txt', sep=';',
        #                  index=False)
        # test_feature_importance.to_csv(r'\SST\test_feature_importance.txt', sep=';',
        #                  index=False)
        # p_whole = spiral.user_classify('RF','C:/Users/Thinkpad/Desktop/Warwick/hero-monitor/data/user_drawing/whole_set_errors.txt')
        # p_whole.to_csv('C:/Users/Thinkpad/Desktop/Warwick/hero-monitor/data/user_drawing/whole_set_errors.txt', sep=';')
        # spiral.confusion_matrix(test)


    def final_user():
        data = FeatureEngineering()
        user_data = data.user_data()
        spiral = DataAnalytics()
        spiral.get_prob_reg(user_data, 'user_data')
        # p_user=spiral.user_classify('RF', 'C:/Users/Thinkpad/Desktop/Warwick/hero-monitor/data/user_drawing/selected_user_spiral_errors.txt')
        spiral.error_graphs()


    # final_gen_SST()
    final_train_model()
    final_user()

    # data = FeatureEngineering()
    # data.plot_file('Manual', 'spiral_data', 'manual1.txt')
    #
