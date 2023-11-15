
import numpy as np
import matplotlib.pyplot as plt
from screen import Screen

def plot_spiral(A, B, t_max=4, num_points=1000):

    t = np.linspace(0, t_max * np.pi, num_points)
    x = A * t * np.cos(B * t)
    y = A * t * np.sin(B * t)

    plt.figure(figsize=(13,13))
    #Plot the spiral
    plt.plot(x, y ,linewidth=5)
    #Turn off x-axis ticks and labels
    plt.xticks([])
    plt.xlabel('')

    # Turn off y-axis ticks and labels
    plt.yticks([])
    plt.ylabel('')

    plt.gca().set_aspect('equal', adjustable='box')
    plt.savefig('spiral_plot.png')

