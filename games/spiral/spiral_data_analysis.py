import os
import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Set the current working directory
os.chdir('/Users/Thinkpad/Desktop/Warwick/hero-monitor')

# Specify the folder path using double backslashes or a raw string
folder_path = r'C:\Users\Thinkpad\Desktop\Warwick\hero-monitor\data\parkinsons_data\hw_dataset\parkinson'

# Use the glob module to get a list of all files in the folder
file_list = glob.glob(os.path.join(folder_path, '*.txt'))


class DataAnalytics:
    def __init__(self,pd_data):
        self.center = [200, 200]
        self.end = [400, 200]
        self.turns = 3
        self.clockwise = True
        self.spiral=pd.DataFrame()
        self.pd_data=pd_data
        self.errors=pd.DataFrame()


    def pull_tests(self):
        self.SST = self.pd_data[self.pd_data['Test ID'] == 0]
        self.DST = self.pd_data[self.pd_data['Test ID'] == 1]


    def gen_data(self,df):
        turns = 0
        df.loc[:, 'X'] = df['Plot X'] - self.center[0]
        df.loc[:, 'Y'] = df['Plot Y'] - self.center[1]
        df.loc[:, 'Theta'] = np.arctan2(df['Y'], df['X'])
        df.loc[:, 'Angular Velocity'] = df['Theta'].diff()
        for i in range(len(df['X'])):
            if abs(df['Angular Velocity'].iloc[i]) > 6:
                turns += 1
            df.at[i, 'Theta'] = df.at[i, 'Theta'] - turns * 2 * np.pi

        df.loc[:, 'Angular Velocity'] = df['Theta'].diff() / df['Time'].diff()
        df.loc[:, 'Magnitude'] = np.linalg.norm(df[['X', 'Y']], axis=1)
        df.loc[:, 'Dist'] = np.linalg.norm(df[['X', 'Y']].diff(axis=0, periods=20), axis=1)
        df.loc[:, 'DrawingSpeed'] = df['Dist'] / (df['Time'].diff(periods=20))

    def gen_spiral(self,df):
        n = len(self.SST)
        b = np.linalg.norm(np.array(self.end) - np.array(self.center)) / (self.turns * 2 * np.pi)
        self.spiral.loc[:, 'Time'] = np.linspace(df['Time'].iloc[0], df['Time'].iloc[-1], n)
        self.spiral.loc[:, 'Theta'] = np.linspace(0, self.turns * 2 * np.pi, n)
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


    def plot_graph(self,dfs,X, Y):
        for i, df in enumerate(dfs):
            plt.plot(df[X], df[Y])
            plt.xlabel(X)
            plt.ylabel(Y)
            plt.grid(True)
        plt.show()

    def sum_squared_error(self,dfs,X,Y):
        if X and Y:
            squared_error =(dfs[0][X] - dfs[1][X])**2 + (dfs[0][Y] - dfs[1][Y])**2
            sum_squared_error = squared_error.sum()
            self.errors.loc[str.join(X,Y)]=sum_squared_error
        else:
            squared_error=(dfs[0][Y] - dfs[1][Y]) ** 2
            sum_squared_error=squared_error.sum()
            self.errors.loc[Y] = sum_squared_error

    def sum_error(self,dfs,X,Y):
        if X and Y:
            error=np.linalg.norm([(dfs[0][X] - dfs[1][X]),(dfs[0][Y] - dfs[1][Y])],axis=1)
            sum_error = error.sum()
            self.errors.loc[str.join(X,Y)]=sum_error
        else:
            error = (dfs[0][Y] - dfs[1][Y])
            sum_error=error.sum()
            self.errors.loc[Y] = sum_error





    def plot_graphs(self):
        self.plot_graph(self.dfs, 'X', 'Y')
        self.plot_graph(self.dfs, 'Theta', 'Magnitude')
        self.plot_graph(self.dfs, 'Time', 'Theta')
        self.plot_graph(self.dfs, 'Time', 'Magnitude')
        self.plot_graph(self.dfs, 'Time', 'Angular Velocity')

    def calc_errors(self):
        self.sum_squared_error(self.dfs, 'X', 'Y')
        self.sum_squared_error(self.dfs, 'Magnitude')
        self.sum_squared_error(self.dfs, 'Theta')
        self.sum_squared_error(self.dfs, 'Magnitude')
        self.sum_squared_error(self.dfs, 'Angular Velocity')

    def entry(self):
        self.pull_tests()
        self.gen_spiral(self.SST)
        self.gen_data(self.SST)
        self.dfs=[self.SST,self.spiral]







if __name__ == "__main__":
    file_path = 'C:\\Users\\Thinkpad\\Desktop\\Warwick\\hero-monitor\\data\\parkinsons_data\\hw_dataset\\control\\C_0006.txt'
    pd_data = pd.read_csv(file_path, delimiter=';', header=None,names=['Plot X', 'Plot Y', 'Z', 'Pressure', 'GripAngle', 'Time', 'Test ID'])
    data=DataAnalytics(pd_data)
    data.entry()
