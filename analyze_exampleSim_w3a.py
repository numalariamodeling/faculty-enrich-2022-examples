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

mpl.rcParams['pdf.fonttype'] = 42

# This block will be used unless overridden on the command-line
SetupParser.default_block = 'LOCAL'

user = os.getlogin()  # user initials
expt_name = f'{user}_FE_2022_example_w3a'
expt_id = '2022_04_29_04_26_46_512944'  ## change expt_id
working_dir = os.path.join('simulation_outputs')


if __name__ == "__main__":
    SetupParser.init()

    analyzers = [
        InsetChartAnalyzer(expt_name=expt_name,
                           working_dir=working_dir),
        AnnualAgebinPfPRAnalyzer(expt_name=expt_name,
                                 working_dir=working_dir,
                                 start_year=2022,
                                 end_year=2025),
        IndividualEventsAnalyzer(expt_name=expt_name,
                                 working_dir=working_dir,
                                 start_year=2022,
                                 selected_year=None),
        # BednetUsageAnalyzer(expt_name=expt_name,
        #                     working_dir=working_dir,
        #                     start_year=2022),   # only if using add_ITN_age_season instead of add_ITN
        ReceivedCampaignAnalyzer(expt_name=expt_name,
                                 working_dir=working_dir,
                                 channels=['Received_Treatment', 'Received_Severe_Treatment', 'Received_ITN',
                                           'Received_IRS', 'Received_SMC', 'Received_Vaccine'],
                                 start_year=2022),
        TransmissionReport(expt_name=expt_name,
                           working_dir=working_dir,
                           start_year=2022,
                           selected_year=None,
                           monthly_report=True,
                           daily_report=True)
    ]

    am = AnalyzeManager(expt_id, analyzers=analyzers)
    am.analyze()
