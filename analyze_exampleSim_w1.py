import os
import datetime
import pandas as pd
import numpy as np
from simtools.Analysis.AnalyzeManager import AnalyzeManager
from simtools.SetupParser import SetupParser
from simtools.Analysis.BaseAnalyzers import BaseAnalyzer

from analyzer_collection import InsetChartAnalyzer
# This block will be used unless overridden on the command-line
SetupParser.default_block = 'LOCAL'

user = os.getlogin()  # user initials
expt_name = f'{user}_FE_2022_example_w1'
expt_id = '2022_04_29_02_14_46_106520'  ## change expt_id
working_dir = os.path.join('simulation_outputs')




if __name__ == "__main__":
    SetupParser.init()

    analyzers = [InsetChartAnalyzer(expt_name=expt_name, working_dir=working_dir)]

    am = AnalyzeManager(expt_id, analyzers=analyzers)
    am.analyze()
