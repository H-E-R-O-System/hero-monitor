import glob
import os

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn import metrics
from sklearn.linear_model import LogisticRegression


class FeatureEngineering:
    def __init__(self):
        self.center = [200, 200]
        self.end = [400, 200]
        self.turns = 3
        self.clockwise = False
        self.spiral = pd.DataFrame()
        self.spiral2 = pd.DataFrame()
        self.errors = pd.DataFrame()

    def pull_tests(self):
        SST = self.pd_data[self.pd_data['Test ID'] == 0].copy()
        DST = self.pd_data[self.pd_data['Test ID'] == 1].copy()
        return SST, DST

    def gen_data(self, df):
        turns = 0
        df.loc[:, 'Time'] = df['Time'] - df['Time'].iloc[0]
        df.loc[:, 'X'] = df['Plot X']-200
        df.loc[:, 'Y'] = df['Plot Y']-200
        df.loc[:, 'Theta'] = np.arctan2(df['Y'], df['X'])
        df.loc[:, 'Angular Velocity'] = df['Theta'].diff()

        for index, row in df.iterrows():
            if abs(row['Angular Velocity']) >= 6:
                turns += 1
            df.loc[index, 'Theta'] = abs(row['Theta']+ turns * 2 * np.pi)

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

        self.spiral.loc[:, 'X'] = (b * self.spiral['Theta']) * np.cos(self.spiral['Theta'])
        self.spiral.loc[:, 'Y'] = (b * self.spiral['Theta']) * np.sin(self.spiral['Theta'])

        self.spiral.loc[:, 'Plot X'] = self.center[0] + self.spiral['X']
        self.spiral.loc[:, 'Plot Y'] = self.center[1] + self.spiral['Y']
        self.spiral.loc[:, 'Magnitude'] = np.linalg.norm(self.spiral[['X', 'Y']], axis=1)
        self.spiral.loc[:, 'Angular Velocity'] = self.spiral['Theta'].diff() / self.spiral['Time'].diff()
        self.spiral.loc[:, 'Dist'] = np.linalg.norm(self.spiral[['X', 'Y']].diff(axis=0, periods=20), axis=1)
        self.spiral.loc[:, 'DrawingSpeed'] = self.spiral['Dist'] / (self.spiral['Time'].diff(periods=20))

    def gen_spiral_time(self, df,Y):
        self.spiral_time = pd.DataFrame()

        b = np.linalg.norm(np.array(self.end) - np.array(self.center)) / (self.turns * 2 * np.pi)
        self.spiral_time.loc[:, 'Time'] = df['Time']
        # normalised=df['Time']/max(df['Time'])
        if Y=='Magnitude':
            self.spiral_time['Theta'] = df['Theta']
            if self.clockwise == True:
                self.spiral_time['Theta'] = -self.spiral_time['Theta']
            self.spiral_time.loc[:, 'X'] = (b * self.spiral_time['Theta']) * np.cos(-self.spiral_time['Theta'])
            self.spiral_time.loc[:, 'Y'] = (b * self.spiral_time['Theta']) * np.sin(-self.spiral_time['Theta'])
            self.spiral_time.loc[:, 'Magnitude'] = np.linalg.norm(self.spiral_time[['X', 'Y']], axis=1)

        elif Y=='Theta':
            self.spiral_time['Magnitude'] = df['Magnitude']
            n = len(df['Magnitude'])
            theta = np.sqrt(np.linspace(0, (self.turns * 2 * np.pi) ** 2, n))
            index = np.round((self.spiral_time['Magnitude'] / max(self.spiral_time['Magnitude'])) * (n - 1)).astype(int)
            self.spiral_time['Theta'] = theta[index]
            if self.clockwise == True:
                self.spiral_time['Theta'] = -self.spiral_time['Theta']
            self.spiral_time.loc[:, 'X'] = (b * self.spiral_time['Theta']) * np.cos(-self.spiral_time['Theta'])
            self.spiral_time.loc[:, 'Y'] = (b * self.spiral_time['Theta']) * np.sin(-self.spiral_time['Theta'])
        else:
            self.spiral_time['Theta'] = np.sqrt(np.linspace(0, (self.turns * 2 * np.pi) ** 2, n))
            if self.clockwise == True:
                self.spiral_time['Theta'] = -self.spiral_time['Theta']
            self.spiral_time.loc[:, 'X'] = (b * self.spiral_time['Theta']) * np.cos(-self.spiral_time['Theta'])
            self.spiral_time.loc[:, 'Y'] = (b * self.spiral_time['Theta']) * np.sin(-self.spiral_time['Theta'])
            self.spiral_time.loc[:, 'Magnitude'] = np.linalg.norm(self.spiral_time[['X', 'Y']], axis=1)
        self.spiral_time.loc[:, 'Plot X'] = self.center[0] + self.spiral_time['X']
        self.spiral_time.loc[:, 'Plot Y'] = self.center[1] + self.spiral_time['Y']
        self.spiral_time.loc[:, 'Angular Velocity'] = self.spiral_time['Theta'].diff() / self.spiral_time['Time'].diff()
        self.spiral_time.loc[:, 'Dist'] = np.linalg.norm(self.spiral_time[['X', 'Y']].diff(axis=0, periods=20), axis=1)
        self.spiral_time.loc[:, 'DrawingSpeed'] = self.spiral_time['Dist'] / (self.spiral_time['Time'].diff(periods=20))

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
        self.closest_coords.loc[:, 'DrawingSpeed'] = self.closest_coords['Dist'] / (
            self.closest_coords['Time'].diff(periods=20))

    def plot_graph(self, X, Y):
        if X == 'Time':
            plt.scatter(self.spiral_time[X], self.spiral_time[Y], s=0.05)
        else:
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

    def plot_graphs(self):
        self.plot_graph('X', 'Y' )
        self.plot_graph('Theta', 'Magnitude')
        self.plot_graph('Magnitude', 'DrawingSpeed')
        self.plot_graph('Time', 'Magnitude')

    def sum_squared_error(self, X, Y):
        for name, df in self.dfs.items():
            df.reset_index(drop=True, inplace=True)
            if X=='Time':
                self.gen_spiral_time(df,Y)
                squared_error = (abs(df[X] - self.spiral_time[X]) + abs(df[Y] - self.spiral_time[Y]))
            else:
                self.gen_spiral(df)
                self.get_closest_coords(df)
                squared_error = (abs(df[X] - self.closest_coords[X]) + abs(df[Y] - self.closest_coords[Y]))
            sum_squared_error = squared_error.sum() / len(df[X])
            string = '_'.join([X, Y])
            self.errors.at[self.index, string] = sum_squared_error

    # def sum_error_closest(self, X, Y):
    #     for name, df in self.dfs.items():
    #         df.reset_index(drop=True, inplace=True)
    #         squared_error = (abs(df[X] - self.spiral[X]) + abs(df[Y] - self.spiral[Y]))
    #         sum_squared_error = squared_error.sum() / len(df[X])
    #         string = '_'.join([name, X, Y])
    #         self.errors.at[self.index, string] = sum_squared_error

    def final_value(self,Y):
        for name, df in self.dfs.items():
            string = '_'.join([Y,'Final'])
            self.errors.at[self.index, string] = df[Y].iloc[-1]

    def calc_errors(self,):
        # self.sum_squared_error('X', 'Y')
        self.sum_squared_error('Theta', 'Magnitude')
        self.sum_squared_error('Magnitude', 'DrawingSpeed')
        self.final_value('Time')
        # self.sum_squared_error('Time', 'Theta')
        self.sum_squared_error('Time', 'Magnitude')
        #self.sum_squared_error_closest('Magnitude', 'Angular Velocity')


    def plot_file(self, test, input, file):
        base_path = r'C:/Users/Thinkpad/Desktop/Warwick/hero-monitor/data/parkinsons_data/hw_dataset'
        file_path = os.path.join(base_path, input, file)
        self.pd_data = pd.read_csv(file_path, delimiter=';', header=None,
                                   names=['Plot X', 'Plot Y', 'Z', 'Pressure', 'GripAngle', 'Time', 'Test ID'])
        [SST, DST] = self.pull_tests()
        self.spiral = pd.DataFrame()
        self.errors = pd.DataFrame()
        self.index = 0
        if test == 'SST':
            SST = self.gen_data(SST)
            self.dfs = {'_'.join([file, test]): SST}
            # self.get_closest_coords(SST)
            self.calc_errors()
            file_name = '_'.join([test, input, file, 'error_test.txt'])
            self.errors.to_csv(file_name, sep=';', index=False)
        if test == 'DST':
            DST = self.gen_data(DST)
            self.dfs = {'_'.join([file, test]): DST}
            # self.get_closest_coords(SST)
            self.calc_errors()
            file_name = '_'.join([test, input, file, 'error_test.txt'])
            self.errors.to_csv(file_name, sep=';', index=False)
        self.plot_graphs(file)

    def loop_SST(self, input):
        print(f"Calculating errors for {input} SST ...")
        self.errors = pd.DataFrame()
        base_path = r'C:/Users/Thinkpad/Desktop/Warwick/hero-monitor/data/parkinsons_data/hw_dataset'
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
            SST = self.gen_data(SST)
            self.dfs = {'SST': SST}
            self.calc_errors()
            # self.plot_graphs(file_name)
            # time.sleep(1)

        # Create the "SST" folder if it does not exist
        folder_path = r'C:/Users/Thinkpad/Desktop/Warwick/hero-monitor/data'
        sst_folder = os.path.join(folder_path, 'SST')
        os.makedirs(sst_folder, exist_ok=True)

        # Save the CSV file inside the "SST" folder
        file_name = os.path.join(sst_folder, f'{input}_error.txt')
        self.errors['File'] = [os.path.basename(os.path.normpath(path)) for path in file_list]
        self.errors.to_csv(file_name, sep=';', index=False)

        print("Done")

    def loop_DST(self, input):
        print(f"Calculating errors for {input} DST ...")
        base_path = r'C:/Users/Thinkpad/Desktop/Warwick/hero-monitor/data/parkinsons_data/hw_dataset'
        folder_path = os.path.join(base_path, input)
        file_list = glob.glob(os.path.join(folder_path, '*.txt'))

        for file_index, file_path in enumerate(file_list):
            print(file_index)
            self.spiral = pd.DataFrame()
            self.index = file_index
            self.pd_data = pd.read_csv(file_path, delimiter=';', header=None,
                                       names=['Plot X', 'Plot Y', 'Z', 'Pressure', 'GripAngle', 'Time', 'Test ID'])
            SST, DST = self.pull_tests()
            DST = self.gen_data(DST)
            self.dfs = {'DST': DST}
            self.calc_errors()
            # self.plot_graphs()
            # time.sleep(0.5)

        folder_path = r'C:/Users/Thinkpad/Desktop/Warwick/hero-monitor/data'
        dst_folder = os.path.join(folder_path, 'DST')
        os.makedirs(dst_folder, exist_ok=True)

        file_name = os.path.join(dst_folder, f'{input}_error.txt')
        self.errors['File'] = [os.path.basename(os.path.normpath(path)) for path in file_list]
        self.errors.to_csv(file_name, sep=';', index=False)
        print("Done")

    def user_data(self):
        self.index=0
        self.errors = pd.DataFrame()
        file_path = r'C:/Users/Thinkpad/Desktop/Warwick/hero-monitor/data/user_drawing/user_spiral.txt'
        data = pd.read_csv(file_path, delimiter=',')
        data= self.gen_data(data)
        self.gen_spiral(data)
        self.dfs = {'USER': data}
        self.calc_errors()
        self.plot_graphs()
        self.errors.to_csv(r'C:\Users\Thinkpad\Desktop\Warwick\hero-monitor\data\user_drawing\user_spiral_errors.txt', sep=';', index=False)

        print("Done")




class DataAnalytics:
    def __init__(self):
        pass
    def extract_errors(self):
        # List of folders to open
        folders_to_open = ['SST']
        data_path = r'C:/Users/Thinkpad/Desktop/Warwick/hero-monitor/data'

        for folder in folders_to_open:
            folder_path = os.path.join(data_path, folder)

            control_error_file = os.path.join(folder_path, 'control_error.txt')

            parkinsons_error_file = os.path.join(folder_path, 'parkinson_error.txt')

            control_error_data = pd.read_csv(control_error_file, sep=';')
            parkinsons_error_data = pd.read_csv(parkinsons_error_file, sep=';')

            train_ratio = 1

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
            whole_set= pd.concat([control_error_data, parkinsons_error_data])

        return train, test ,whole_set

    def box_plots(self, data):
        for col in data[:-1]:
            if col != 'File':
                plt.boxplot([data[col].dropna(), data[col].dropna()],
                            labels=['control', 'parkinson'])
                plt.xlabel('Data Sets')
                plt.ylabel(col)
                plt.title('Box Plot of Different Data Sets')
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

    def get_prob(self, test_data):
        prediction = pd.DataFrame()
        classification= pd.DataFrame()
        prediction['File'] = test_data['File'].copy()
        prediction['Catagory'] = test_data['Catagory'].copy()
        classification['File'] = test_data['File'].copy()
        classification['Catagory'] = test_data['Catagory'].copy()

        for col in test_data.columns[:-1]:
            if col != 'File':
                model_filename = f"{col}_model.joblib"
                model= joblib.load(model_filename)
                X = np.array(test_data[col])
                odds = model.coef_ * X + model.intercept_
                odds = np.exp(odds)
                probability = odds / (1 + odds)
                prediction[col] = probability.reshape(-1, 1)
                classification[col]=model.predict(X.reshape(-1, 1))


        weights = [0, 0, 50, 50,0,0]
        prediction['Final P'] = (prediction * weights).sum(axis=1)
        prediction['Final C'] = classification.iloc[:, 1:].mode(axis=1, dropna=True)
        # print(prediction)


        return prediction

    def error_graphs(self):
        file_path = r'C:\Users\Thinkpad\Desktop\Warwick\hero-monitor\data\SST\whole_set_prediction.txt'
        whole_set = pd.read_csv(file_path, sep=';')
        file_path = r'C:/Users/Thinkpad/Desktop/Warwick/hero-monitor/data/prediction.txt'
        test = pd.read_csv(file_path, sep=';')
        print(test)
        for col in whole_set.columns[:-2]:
            if col != 'File' and col != 'Catagory':
                plt.scatter(whole_set[col][whole_set['Final C'] == 0], whole_set['Final P'][whole_set['Final C'] == 0],
                            color='blue', label='z=0')
                plt.scatter(whole_set[col][whole_set['Final C'] == 1], whole_set['Final P'][whole_set['Final C'] == 1],
                            color='red', label='z=1')
                plt.scatter(test[col][test['Final C'] == 0], test['Final P'][test['Final C'] == 0],
                            color='blue', label='z=0',marker='s')
                plt.scatter(test[col][test['Final C'] == 1], test['Final P'][test['Final C'] == 1],
                            color='red', label='z=1',marker='s')
                plt.xlabel(str(col))
                plt.ylabel('Probability')
                plt.show()



        file_path = r'C:/Users/Thinkpad/Desktop/Warwick/hero-monitor/data/user_drawing/user_spiral_errors.txt'
        test = pd.read_csv(file_path, sep=';')






    def user_classify(self):
        file_path = r'C:/Users/Thinkpad/Desktop/Warwick/hero-monitor/data/user_drawing/user_spiral_errors.txt'
        test = pd.read_csv(file_path, sep=';')
        prediction = pd.DataFrame()
        classification= pd.DataFrame()

        for col in test.columns:
            if col!='File':
                model_filename = f"{col}_model.joblib"
                model= joblib.load(model_filename)
                X = np.array([test[col]])
                odds = model.coef_ * X + model.intercept_
                odds = np.exp(odds)
                probability = odds / (1 + odds)
                # print(probability)
                prediction[col] = probability[0]
                classification[col]=model.predict(X)
        # print(classification)
        weights = [ 40, 30, 10, 20]
        prediction['Final P'] = (prediction * weights).sum(axis=1)
        prediction['Final C'] = classification.iloc[0].mode( dropna=True)
        # print(prediction)

        prediction.to_csv('prediction.txt', sep=';', index=False)
        classification.to_csv('classification.txt', sep=';', index=False)

        self.error_graphs()

        return prediction, classification

    def confusion_matrix(self, classification):
        for col in classification.columns:
            if col != 'File' and col != 'Catagory':
                confusion_matrix = metrics.confusion_matrix(classification[col], classification['Catagory'])
                cm_display = metrics.ConfusionMatrixDisplay(confusion_matrix=confusion_matrix,
                                                    display_labels=[0, 1])  # Assuming Category values are 0 and 1
                cm_display.plot()
                plt.title(f'Confusion Matrix for {col}')
                plt.show()




if __name__ == "__main__":
    os.chdir('/Users/Thinkpad/Desktop/Warwick/hero-monitor/data')

    def final_gen_SST():
        data = FeatureEngineering()
        data.loop_SST('control')
        data.loop_SST('parkinson')

    def final_train_model():
        spiral = DataAnalytics()
        train, test , whole_set =spiral.extract_errors()
        whole_set=spiral.get_prob(whole_set)
        whole_set.to_csv(r'C:\Users\Thinkpad\Desktop\Warwick\hero-monitor\data\SST\whole_set_prediction.txt', sep=';',
                         index=False)
        spiral.regression(train)

    def final_user():
        data = FeatureEngineering()
        data.user_data()
        spiral = DataAnalytics()
        spiral.user_classify()
        spiral.error_graphs()

    final_train_model()
    final_user()

    # data.plot_file('SST', 'parkinson', 'P_11120003.txt')


