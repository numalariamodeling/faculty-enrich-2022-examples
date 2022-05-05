## Import basic python functions
import os
import datetime
import pandas as pd
import numpy as np
## Import dtk and EMOD basics functionalities
from simtools.Analysis.AnalyzeManager import AnalyzeManager
from simtools.Analysis.BaseAnalyzers import BaseAnalyzer
from simtools.SetupParser import SetupParser

from analyzer_plots_collection import InsetChartAnalyzer, AnnualAgebinPfPRAnalyzer
## For plotting
import matplotlib.pyplot as plt
import matplotlib as mpl

mpl.rcParams['pdf.fonttype'] = 42

# This block will be used unless overridden on the command-line
SetupParser.default_block = 'LOCAL'

user = os.getlogin()  # user initials
expt_name = f'{user}_FE_2022_example_w2'
expt_id = '2022_04_25_13_03_42_075543'  ## change expt_id
working_dir = os.path.join('simulation_outputs')

if __name__ == "__main__":
    SetupParser.init()

    analyzers = [InsetChartAnalyzer(expt_name=expt_name,
                                    working_dir=working_dir),
                 AnnualAgebinPfPRAnalyzer(expt_name=expt_name,
                                          working_dir=working_dir,
                                          start_year=2022,
                                          end_year=2025)
                 ]

    am = AnalyzeManager(expt_id, analyzers=analyzers)
    am.analyze()
