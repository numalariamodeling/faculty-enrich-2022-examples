import os
import datetime
import pandas as pd
import numpy as np
from simtools.Analysis.AnalyzeManager import AnalyzeManager
from simtools.Analysis.BaseAnalyzers import BaseAnalyzer
from simtools.SetupParser import SetupParser

from analyzer_plots_collection import *

import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.dates as mdates
import seaborn as sns

mpl.rcParams['pdf.fonttype'] = 42
palette = sns.color_palette("tab10")

# This block will be used unless overridden on the command-line
SetupParser.default_block = 'LOCAL'

user = os.getlogin()  # user initials
expt_name = f'{user}_FE_2022_example_w3b'
expt_id = '2022_04_26_07_56_42_515978'  ## change expt_id
working_dir = os.path.join('simulation_outputs')

if __name__ == "__main__":
    SetupParser.init()

    sweep_variables = ['cm_cov_U5', 'smc_coverage', 'itn_coverage',
                       'irs_coverage', 'rtss_coverage', 'Run_Number']

    analyzers = [InsetChartAnalyzer(expt_name=expt_name,
                                    working_dir=working_dir,
                                    sweep_variables=sweep_variables),
                 AnnualAgebinPfPRAnalyzer(expt_name=expt_name,
                                          working_dir=working_dir,
                                          start_year=2022,
                                          end_year=2025,
                                          sweep_variables=sweep_variables),
                 ReceivedCampaignAnalyzer(expt_name=expt_name,
                                          working_dir=working_dir,
                                          channels=['Received_Treatment', 'Received_Severe_Treatment', 'Received_ITN',
                                                    'Received_IRS', 'Received_SMC', 'Received_Vaccine'],
                                          start_year=2022,
                                          sweep_variables=sweep_variables),
                 TransmissionReport(expt_name=expt_name,
                                    working_dir=working_dir,
                                    start_year=2022,
                                    selected_year=None,
                                    monthly_report=True,
                                    daily_report=True,
                                    sweep_variables=sweep_variables)
                 ]

    am = AnalyzeManager(expt_id, analyzers=analyzers)
    am.analyze()
