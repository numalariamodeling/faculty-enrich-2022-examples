import os
import argparse
import datetime
import pandas as pd
from simtools.Analysis.AnalyzeManager import AnalyzeManager
from simtools.SetupParser import SetupParser
from simtools.Analysis.BaseAnalyzers import BaseAnalyzer

if os.name == "posix":
    SetupParser.default_block = 'NUCLUSTER'
    filter_exists = True
else:
    SetupParser.default_block = 'HPC'
    filter_exists = False
SetupParser.init()

"""allow parsing arguments when running script in terminal"""


def parse_args():
    description = "Simulation specifications"
    parser = argparse.ArgumentParser(description=description)

    parser.add_argument(
        "-name",
        "--expt_name",
        type=str,
        help="Name of simulation experiment",
        default=None
    )
    parser.add_argument(
        "-id",
        "--exp_id",
        type=str,
        nargs='+',
        help="Unique ID of simulation experiment"
    )
    parser.add_argument(
        "-syr",
        "--start_year",
        type=int,
        help="First year of reports to analyze",
        default=0
    )
    parser.add_argument(
        "-eyr",
        "--end_year",
        type=int,
        help="Last year of reports to analyze",
        default=6
    )
    return parser.parse_args()


class MonthlyPfPRAnalyzer(BaseAnalyzer):

    def __init__(self, expt_name, sweep_variables=None, working_dir=".", start_year=0, end_year=6):
        super(MonthlyPfPRAnalyzer, self).__init__(working_dir=working_dir,
                                                  filenames=[f"output/MalariaSummaryReport_Monthly_{x}.json"
                                                             for x in range(start_year, end_year)]
                                                  )
        self.sweep_variables = sweep_variables or ["Run_Number"]
        self.expt_name = expt_name
        self.start_year = start_year
        self.end_year = end_year
        self.output_csv = os.path.join(self.working_dir, self.expt_name, 'U5_PfPR_ClinicalIncidence.csv')

    def select_simulation_data(self, data, simulation):

        adf = pd.DataFrame()
        for year, fname in zip(range(self.start_year, self.end_year), self.filenames):
            d = data[fname]['DataByTimeAndAgeBins']['PfPR by Age Bin'][:12]
            pfpr = [x[1] for x in d]
            d = data[fname]['DataByTimeAndAgeBins']['Annual Clinical Incidence by Age Bin'][:12]
            clinical_cases = [x[1] for x in d]
            d = data[fname]['DataByTimeAndAgeBins']['Annual Severe Incidence by Age Bin'][:12]
            severe_cases = [x[1] for x in d]
            d = data[fname]['DataByTimeAndAgeBins']['Average Population by Age Bin'][:12]  # this add pop col in U5
            pop = [x[1] for x in d]
            simdata = pd.DataFrame({'month': range(1, 13),
                                    'PfPR U5': pfpr,
                                    'Cases U5': clinical_cases,
                                    'Severe cases U5': severe_cases,
                                    'Pop U5': pop})
            simdata['year'] = year
            adf = pd.concat([adf, simdata])

        for sweep_var in self.sweep_variables:
            if sweep_var in simulation.tags.keys():
                adf[sweep_var] = simulation.tags[sweep_var]
        return adf

    def finalize(self, all_data):

        selected = [data for sim, data in all_data.items()]
        if len(selected) == 0:
            print("No data have been returned... Exiting...")
            return

        if not os.path.exists(os.path.join(self.working_dir, self.expt_name)):
            os.mkdir(os.path.join(self.working_dir, self.expt_name))

        adf = pd.concat(selected).reset_index(drop=True)
        adf.to_csv(self.output_csv, index=False, index_label=False)


if __name__ == "__main__":

    project_path = os.path.join(os.getcwd())

    """Simulation arguments"""
    use_parse = False
    if use_parse:
        args = parse_args()
        expt_name = args.expt_name
        expt_id = args.expt_id
        start_year = args.start_year
        end_year = args.end_year
    else:
        expt_name = 'MR_FE_2022_example_w2'
        expt_id = '98be6b18-3bc2-ec11-a9f6-9440c9be2c51'
        start_year = 0
        end_year = 6

    """Define experiment sweeps and IPTi treatment_channels"""
    sweep_variables = ['Run_Number']

    """Create simulation output folder"""
    working_dir = os.path.join('./','simulation_outputs')
    if not os.path.exists(os.path.join(working_dir)):
        os.mkdir(os.path.join(working_dir))

    """Run analyzer comment out those not needed"""
    analyzers = [
        MonthlyPfPRAnalyzer(expt_name=expt_name,
                            sweep_variables=sweep_variables,
                            working_dir=working_dir,
                            start_year=start_year,
                            end_year=end_year)
    ]
    am = AnalyzeManager(expt_id, analyzers=analyzers)
    am.analyze()
