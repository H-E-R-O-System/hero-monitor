import os
import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix


class FeatureEngineering:
    def __init__(self):
        self.center = [200, 200]
        self.end = [400, 200]
        self.turns = 3
        self.clockwise = True
        self.spiral = pd.DataFrame()
        self.errors = pd.DataFrame()

    def pull_tests(self):
        SST = self.pd_data[self.pd_data['Test ID'] == 0].copy()
        DST = self.pd_data[self.pd_data['Test ID'] == 1].copy()
        return SST, DST

    def gen_data(self, df):
        turns = 0
        df.loc[:, 'Time'] = df['Time'] - df['Time'].iloc[0]
        df.loc[:, 'X'] = df['Plot X'] - self.center[0]
        df.loc[:, 'Y'] = df['Plot Y'] - self.center[1]
        df.loc[:, 'Theta'] = np.arctan2(df['Y'], df['X'])
        df.loc[:, 'Angular Velocity'] = df['Theta'].diff()

        for index, row in df.iterrows():
            if abs(row['Angular Velocity']) >= 6:
                turns += 1
            df.loc[index, 'Theta'] = row['Theta'] - turns * 2 * np.pi

        df.loc[:, 'Angular Velocity'] = df['Theta'].diff() / df['Time'].diff()
        df.loc[:, 'Magnitude'] = np.linalg.norm(df[['X', 'Y']], axis=1)
        df.loc[:, 'Dist'] = np.linalg.norm(df[['X', 'Y']].diff(axis=0, periods=20), axis=1)
        df.loc[:, 'DrawingSpeed'] = df['Dist'] / (df['Time'].diff(periods=20))
        return df

    def gen_spiral(self, df):
        self.spiral = pd.DataFrame()
        n = len(df)
        b = np.linalg.norm(np.array(self.end) - np.array(self.center)) / (self.turns * 2 * np.pi)
        self.spiral.loc[:, 'Time'] = np.linspace(0, (df['Time'].iloc[-1]) - (df['Time'].iloc[0]), n)
        self.spiral['Theta'] = np.sqrt(np.linspace(0, (self.turns * 2 * np.pi) ** 2, n))
        # self.spiral['Theta'] = np.linspace(0, (self.turns * 2 * np.pi), n)
        if self.clockwise == True:
            self.spiral['Theta'] = -self.spiral['Theta']

        self.spiral.loc[:, 'X'] = -(b * self.spiral['Theta']) * np.cos(self.spiral['Theta'])
        self.spiral.loc[:, 'Y'] = -(b * self.spiral['Theta']) * np.sin(self.spiral['Theta'])

        self.spiral.loc[:, 'Plot X'] = self.center[0] + self.spiral['X']
        self.spiral.loc[:, 'Plot Y'] = self.center[1] + self.spiral['Y']
        self.spiral.loc[:, 'Magnitude'] = np.linalg.norm(self.spiral[['X', 'Y']], axis=1)
        self.spiral.loc[:, 'Angular Velocity'] = self.spiral['Theta'].diff() / self.spiral['Time'].diff()
        self.spiral.loc[:, 'Dist'] = np.linalg.norm(self.spiral[['X', 'Y']].diff(axis=0, periods=20), axis=1)
        self.spiral.loc[:, 'DrawingSpeed'] = self.spiral['Dist'] / (self.spiral['Time'].diff(periods=20))

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
            self.closest_coords.loc[index, 'Theta'] = row['Theta'] - turns * 2 * np.pi

        self.closest_coords.loc[:, 'Angular Velocity'] = self.closest_coords['Theta'].diff() / self.closest_coords[
            'Time'].diff()
        self.closest_coords.loc[:, 'Magnitude'] = np.linalg.norm(self.closest_coords[['X', 'Y']], axis=1)
        self.closest_coords.loc[:, 'Dist'] = np.linalg.norm(self.closest_coords[['X', 'Y']].diff(axis=0, periods=20),
                                                            axis=1)
        self.closest_coords.loc[:, 'DrawingSpeed'] = self.closest_coords['Dist'] / (
            self.closest_coords['Time'].diff(periods=20))

    def plot_graph(self, X, Y, file_name):
        plt.scatter(self.spiral[X], self.spiral[Y], s=0.05)
        plt.xlabel(X)
        plt.ylabel(Y)
        plt.grid(True)

        for df in self.dfs.values():
            plt.scatter(df[X], df[Y], s=0.05)
            plt.xlabel(X)
            plt.ylabel(Y)
            plt.grid(True)
        plt.show()
        # plt.title = (str(file_name))
        # plt.savefig(file_name[:-4] + '.png')

    def sum_squared_error(self, X, Y):
        for name, df in self.dfs.items():
            df.reset_index(drop=True, inplace=True)
            squared_error = (abs(df[X] - self.spiral[X]) + abs(df[Y] - self.spiral[Y]))
            sum_squared_error = squared_error.sum() / len(df[X])
            string = '_'.join([name, X, Y])
            self.errors.at[self.index, string] = sum_squared_error

    def sum_squared_error_closest(self, X, Y):
        for name, df in self.dfs.items():
            df.reset_index(drop=True, inplace=True)
            squared_error = (abs(df[X] - self.closest_coords[X]) + abs(df[Y] - self.closest_coords[Y]))

            # new_df = pd.DataFrame({
            #     'Original_X': df[X].round(3),
            #     'Spiral_X': self.closest_coords[X].round(3),
            #     'Original_Y': df[Y].round(3),
            #     'Spiral_Y': self.closest_coords[Y].round(3),
            #     'Error_X': abs(df[X] - self.closest_coords[X]).round(3),
            #     'Error_Y': abs(df[Y] - self.closest_coords[Y]).round(3),
            #     'Error_XY': (abs(df[X] - self.closest_coords[X]) + abs(df[Y] - self.closest_coords[Y])).round(3)
            # })
            #
            # file_name = '_'.join([str(self.index), 'error_test.txt'])
            # new_df.to_csv(file_name, sep=';', index=False)

            sum_squared_error = squared_error.sum() / len(df[X])
            string = '_'.join([name, X, Y])
            self.errors.at[self.index, string] = sum_squared_error

    def export_files(self, input):
        file_name = "spiral_output.txt"
        self.spiral.to_csv(file_name, sep=';', index=False)

        file_name = '_'.join([input, 'error_output.txt'])
        self.errors.to_csv(file_name, sep=';', index=False)

        for name, df in self.dfs.items():
            file_name = f"{name}_output.txt"
            df.to_csv(file_name, sep=';', index=False)

    def plot_graphs(self, file_name):
        self.plot_graph('X', 'Y', file_name)

        self.plot_graph('Theta', 'Magnitude', file_name)
        self.plot_graph('Time', 'Theta', file_name)
        self.plot_graph('Time', 'Magnitude', file_name)
        self.plot_graph('Time', 'Angular Velocity', file_name)
        self.plot_graph('Time', 'DrawingSpeed', file_name)

    def calc_errors(self):
        # self.sum_squared_error_closest('X', 'Y')
        self.sum_squared_error_closest('Theta', 'Magnitude')
        self.sum_squared_error_closest('Magnitude', 'DrawingSpeed')
        self.errors.at[self.index, '_'.join([SST,total_time]) = sum_squared_error
        # self.sum_squared_error('Time', 'Theta')
        # self.sum_squared_error('Time', 'Magnitude')
        # self.sum_squared_error_closest('Magnitude', 'Angular Velocity')

    def plot_file(self, test, input, file):
        base_path = r'C:\Users\Thinkpad\Desktop\Warwick\hero-monitor\data\parkinsons_data\hw_dataset'
        file_path = os.path.join(base_path, input, file)
        self.pd_data = pd.read_csv(file_path, delimiter=';', header=None,
                                   names=['Plot X', 'Plot Y', 'Z', 'Pressure', 'GripAngle', 'Time', 'Test ID'])
        [SST, DST] = self.pull_tests()
        self.spiral = pd.DataFrame()
        self.errors = pd.DataFrame()
        self.index = 0
        if test == 'SST':
            self.gen_spiral(SST)
            SST = self.gen_data(SST)
            self.dfs = {'_'.join([file, test]): SST}
            self.get_closest_coords(SST)
            self.calc_errors()
            file_name = '_'.join([test, input, file, 'error_test.txt'])
            self.errors.to_csv(file_name, sep=';', index=False)
        if test == 'DST':
            self.gen_spiral(DST)
            DST = self.gen_data(DST)
            self.dfs = {'_'.join([file, test]): DST}
            self.get_closest_coords(SST)
            self.calc_errors()
            file_name = '_'.join([test, input, file, 'error_test.txt'])
            self.errors.to_csv(file_name, sep=';', index=False)
        self.plot_graphs(file)

    def loop_SST(self, input):
        print(f"Calculating errors for {input} SST ...")
        self.errors = pd.DataFrame()
        base_path = r'C:\Users\Thinkpad\Desktop\Warwick\hero-monitor\data\parkinsons_data\hw_dataset'
        folder_path = os.path.join(base_path, input)
        file_list = glob.glob(os.path.join(folder_path, '*.txt'))
        self.index = 0
        for file_index, file_path in enumerate(file_list):
            file_name = os.path.basename(os.path.normpath(file_path))
            print(file_name)
            self.index = file_index
            self.pd_data = pd.read_csv(file_path, delimiter=';', header=None,
                                       names=['Plot X', 'Plot Y', 'Z', 'Pressure', 'GripAngle', 'Time', 'Test ID'])
            SST, DST = self.pull_tests()
            self.gen_spiral(SST)
            SST = self.gen_data(SST)
            self.dfs = {'SST': SST}
            self.get_closest_coords(SST)
            self.calc_errors()
            # self.plot_graphs(file_name)
            # time.sleep(1)

        # Create the "SST" folder if it does not exist
        folder_path = r'C:\Users\Thinkpad\Desktop\Warwick\hero-monitor\data'
        sst_folder = os.path.join(folder_path, 'SST')
        os.makedirs(sst_folder, exist_ok=True)

        # Save the CSV file inside the "SST" folder
        file_name = os.path.join(sst_folder, f'{input}_error.txt')
        self.errors['File'] = [os.path.basename(os.path.normpath(path)) for path in file_list]
        self.errors.to_csv(file_name, sep=';', index=False)

        print("Done")

    def loop_DST(self, input):
        print(f"Calculating errors for {input} DST ...")
        base_path = r'C:\Users\Thinkpad\Desktop\Warwick\hero-monitor\data\parkinsons_data\hw_dataset'
        folder_path = os.path.join(base_path, input)
        file_list = glob.glob(os.path.join(folder_path, '*.txt'))

        for file_index, file_path in enumerate(file_list):
            print(file_index)
            self.spiral = pd.DataFrame()
            self.index = file_index
            self.pd_data = pd.read_csv(file_path, delimiter=';', header=None,
                                       names=['Plot X', 'Plot Y', 'Z', 'Pressure', 'GripAngle', 'Time', 'Test ID'])
            SST, DST = self.pull_tests()
            self.gen_spiral(DST)
            DST = self.gen_data(DST)
            self.dfs = {'DST': DST}
            self.get_closest_coords(DST)
            self.calc_errors()
            # self.plot_graphs()
            # time.sleep(0.5)

        folder_path = r'C:\Users\Thinkpad\Desktop\Warwick\hero-monitor\data'
        dst_folder = os.path.join(folder_path, 'DST')
        os.makedirs(dst_folder, exist_ok=True)

        file_name = os.path.join(dst_folder, f'{input}_error.txt')
        self.errors['File'] = [os.path.basename(os.path.normpath(path)) for path in file_list]
        self.errors.to_csv(file_name, sep=';', index=False)
        print("Done")


class DataAnalytics:
    def __init__(self):

    def extract_errors(self):
        # List of folders to open
        folders_to_open = ['SST']
        data_path = r'C:\Users\Thinkpad\Desktop\Warwick\hero-monitor\data'

        for folder in folders_to_open:
            folder_path = os.path.join(data_path, folder)

            control_error_file = os.path.join(folder_path, 'control_error.txt')
            parkinsons_error_file = os.path.join(folder_path, 'parkinson_error.txt')

            control_error_data = pd.read_csv(control_error_file, sep=';')
            parkinsons_error_data = pd.read_csv(parkinsons_error_file, sep=';')

            train_ratio = 0.75

            control_error_data['Catagory'] = 0
            parkinsons_error_data['Catagory'] = 1

            control_error_data = control_error_data.sample(frac=1).reset_index(drop=True)
            parkinsons_error_data = parkinsons_error_data.sample(frac=1).reset_index(drop=True)

            c_test = control_error_data.iloc[:-(round(train_ratio * len(control_error_data))), :]
            p_test = parkinsons_error_data.iloc[:-(round(train_ratio * len(parkinsons_error_data))), :]
            c_train = control_error_data.iloc[(round((1 - train_ratio) * len(control_error_data))):, :]
            p_train = parkinsons_error_data.iloc[(round((1 - train_ratio) * len(parkinsons_error_data))):, :]

            test = pd.concat([c_test, p_test])
            train = pd.concat([c_train, p_train])

        return train, test, control_error_data, parkinsons_error_data

    def box_plots(self, data):
        for col in data[:-1]:
            if col != 'File':
                plt.boxplot([data[column].dropna(), data[column].dropna()],
                            labels=['control', 'parkinson'])
                plt.xlabel('Data Sets')
                plt.ylabel(column)
                plt.title('Box Plot of Different Data Sets')
                plt.show()

    def regression(self, train_data):
        Y = np.array(train_data['Catagory'])
        models = {}  # Dictionary to store models for each column

        for col in train_data.columns[:-1]:
            if col != 'File':
                X = np.array(train_data[col])

                model = LogisticRegression()
                model.fit(X.reshape(-1, 1), Y)
                models[col] = model

        return models

    def get_prob(self, test_data, models):
        predictions = pd.DataFrame()
        predictions['Catagory'] = test_data['File'].copy()

        for col, model in models.items():
            if col != 'File':
                X = np.array(test_data[col])
                odds = model.coef_ * X + model.intercept_
                odds = np.exp(odds)
                probability = odds / (1 + odds)
                predictions[col] = probability.reshape(-1, 1)

        predictions.to_csv('predictions.txt', sep=';', index=False)
        return predictions


if __name__ == "__main__":
    os.chdir('/Users/Thinkpad/Desktop/Warwick/hero-monitor/data')

    data = FeatureEngineering()
    data.loop_SST('control')
    # print('-----------------------------------------------------------------')
    data.loop_SST('parkinson')
    # data.loop_DST('control')
    # data.loop_DST('parkinson')
    data.plot_file('SST', 'control', 'C_0012.txt')
    spiral = DataAnalytics()
    train, test, control, parkinsons = spiral.extract_errors()
    models = spiral.regression(train)
    print(spiral.get_prob(train, models))
