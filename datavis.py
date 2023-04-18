import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def data_vis(csv):

    # Load the CSV file into a pandas DataFrame
    csvFile = open(csv,"r")
    dataFrame = pd.read_csv(csvFile)

    # motor_angvel & motor_power vs. sample_time
    fig1 = plt.figure()
    sns.scatterplot(x='sample_time', y='motor_angvel', data=dataFrame, color='blue')
    sns.scatterplot(x='sample_time', y='motor_power', data=dataFrame, color='red')

    plt.legend(labels=['motor_angvel', 'motor_power'])
    plt.title(csv.rstrip('.csv'))
    plt.ylabel('motor_angvel & motor_power')

    # motor_angvel vs. sample_time
    fig2 = plt.figure()
    sns.scatterplot(x='sample_time', y='motor_angvel', data=dataFrame, color='blue')

    plt.title(csv.rstrip('.csv'))
    plt.ylabel('motor_angvel')

    # motor_power vs. sample_time
    fig3 = plt.figure()
    sns.scatterplot(x='sample_time', y='motor_power', data=dataFrame, color='red')

    plt.title(csv.rstrip('.csv'))
    plt.yscale('log')
    plt.ylabel('motor_power')

    # Display figures
    plt.show()

