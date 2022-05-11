import os
import pandas as pd
import matplotlib.pyplot as plt
from simtools.Analysis.AnalyzeManager import AnalyzeManager
from simtools.SetupParser import SetupParser

from analyzer_collection import InsetChartAnalyzer
# This block will be used unless overridden on the command-line
SetupParser.default_block = 'LOCAL'

user = os.getlogin()  # user initials
expt_name = f'{user}_FE_2022_example_w1'
expt_id = '2022_05_11_20_59_18_543317'  ## change expt_id
working_dir = os.path.join('simulation_outputs')


if __name__ == "__main__":
    SetupParser.init()

    # set desired channels to analyze and plot
    channels = ['Statistical Population', 'New Clinical Cases', 'Adult Vectors', 'Infected']

    # call analyzer to grab EMOD output and process into analyzed data
    analyzers = [InsetChartAnalyzer(expt_name=expt_name,
                                    channels=channels,
                                    working_dir=working_dir)]

    am = AnalyzeManager(expt_id, analyzers=analyzers)
    am.analyze()

    # read in analyzed data
    df = pd.read_csv(os.path.join(working_dir, expt_name, 'All_Age_InsetChart.csv'))
    df['date'] = pd.to_datetime(df['date'])

    # make plot
    fig = plt.figure(figsize=(12,6))
    fig.subplots_adjust(hspace=0.5, left=0.08, right=0.97)
    for ch, channel in enumerate(channels) :
        ax = fig.add_subplot(2,2,ch+1)
        ax.plot(df['date'], df[channel])
        ax.set_title(channel)
    plt.savefig(os.path.join(working_dir, expt_name, 'InsetChart.png'))
    plt.show()
