# Replace 'your_file.csv' with the path to your CSV file
os.chdir('/Users/Thinkpad/Desktop/Warwick/hero-monitor')

# Read the CSV file into a Pandas DataFrame with additional parameters
spiraldata = pd.read_csv('spiraldata.csv')


def radial_speed(df):
    plt.plot(df['time'], abs(df['theta']))
    plt.title('Radial Speed Over Time')
    plt.xlabel('Time')
    plt.ylabel('Radial Speed (|Theta|)')
    plt.grid(True)
    plt.show()


def cum_dist(df):
    df['dist'] = np.linalg.norm(df[['rel_pos_x', 'rel_pos_y']].diff(axis=0), axis=1)
    df['cum_dist'] = df['dist'].cumsum()
    plt.plot(df['time'], df['cum_dist'])
    plt.title('Cumulative Distance Over Time')
    plt.xlabel('Time')
    plt.ylabel('Cumulative Distance')
    plt.grid(True)
    plt.show()


def error(df):
    plt.plot(df['time'], df['error'])
    plt.title('Error Over Time')
    plt.xlabel('Time')
    plt.ylabel('Error')
    plt.grid(True)
    plt.show()


# %%
print(spiraldata)
radial_speed(spiraldata)
cum_dist(spiraldata)
error(spiraldata)
