import os
import datetime
import pandas as pd
import numpy as np
from simtools.Analysis.AnalyzeManager import AnalyzeManager
from simtools.Analysis.BaseAnalyzers import BaseAnalyzer
from simtools.SetupParser import SetupParser

import matplotlib.pyplot as plt
import matplotlib as mpl

mpl.rcParams['pdf.fonttype'] = 42

# This block will be used unless overridden on the command-line
SetupParser.default_block = 'LOCAL'

user = os.getlogin()  # user initials
expt_name = f'{user}_FE_2022_example_w2'
expt_id = '2022_04_25_13_03_42_075543'  ## change expt_id
working_dir = os.path.join('simulation_outputs')


class MonthlyInsetChartAnalyzer(BaseAnalyzer):

    @classmethod
    def monthparser(self, x):
        if x == 0:
            return 12
        else:
            return datetime.datetime.strptime(str(x), '%j').month

    def __init__(self, expt_name, working_dir=".", start_year=2022, end_year=2023):
        super(MonthlyInsetChartAnalyzer, self).__init__(working_dir=working_dir, filenames=["output/InsetChart.json"])
        self.sweep_variables = ["Run_Number"]
        self.inset_channels = ['Statistical Population', 'New Clinical Cases', 'New Severe Cases', 'PfHRP2 Prevalence']
        self.expt_name = expt_name
        self.start_year = start_year
        self.end_year = end_year

    def select_simulation_data(self, data, simulation):
        simdata = pd.DataFrame({x: data[self.filenames[0]]['Channels'][x]['Data'] for x in self.inset_channels})
        simdata['Time'] = simdata.index
        simdata['Day'] = simdata['Time'] % 365
        simdata['Month'] = simdata['Day'].apply(lambda x: self.monthparser((x + 1) % 365))
        simdata['Year'] = simdata['Time'].apply(lambda x: int(x / 365) + self.start_year)
        simdata['date'] = simdata.apply(lambda x: datetime.date(int(x['Year']), int(x['Month']), 1), axis=1)

        sum_channels = ['New Clinical Cases', 'New Severe Cases']
        for x in [y for y in sum_channels if y not in simdata.columns.values]:
            simdata[x] = 0
        mean_channels = ['Statistical Population', 'PfHRP2 Prevalence']

        df = simdata.groupby(['date', 'Month'])[sum_channels].agg(np.sum).reset_index()
        pdf = simdata.groupby(['date', 'Month'])[mean_channels].agg(np.mean).reset_index()

        simdata = pd.merge(left=pdf, right=df, on=['date', 'Month'])

        for sweep_var in self.sweep_variables:
            if sweep_var in simulation.tags.keys():
                simdata[sweep_var] = simulation.tags[sweep_var]
        return simdata

    def finalize(self, all_data):

        selected = [data for sim, data in all_data.items()]
        if len(selected) == 0:
            print("No data have been returned... Exiting...")
            return

        if not os.path.exists(os.path.join(self.working_dir, self.expt_name)):
            os.mkdir(os.path.join(self.working_dir, self.expt_name))

        adf = pd.concat(selected).reset_index(drop=True)
        adf.to_csv(os.path.join(self.working_dir, self.expt_name, 'All_Age_Monthly_Cases.csv'), index=False)

        # Figure with panel per outcome channel
        # Take mean across multiple years and runs for plots per agebin on the x-axis
        adf = adf.groupby(['Month'])[self.inset_channels].agg(np.mean).reset_index()

        fig = plt.figure(figsize=(6, 5))
        fig.subplots_adjust(right=0.96, left=0.12, hspace=0.55, wspace=0.35, top=0.83, bottom=0.10)
        axes = [fig.add_subplot(2, 2, x + 1) for x in range(4)]
        fig.suptitle(f'Analyzer: MonthlyInsetChartAnalyzer')

        for ai, channel in enumerate(self.inset_channels):
            ax = axes[ai]
            ax.set_title(channel)
            ax.set_ylabel(channel)
            if channel == 'PfHRP2 Prevalence':
                ax.set_ylim(0, 1)
            else:
                ax.set_ylim(0, np.max(adf[channel]))
            ax.set_xlabel('Month')
            ax.set_xticks(range(1, 13))
            ax.set_xticklabels(range(1, 13))
            ax.plot(adf['Month'], adf[channel], '-', color='black', linewidth=0.8)
        fig.savefig(os.path.join(self.working_dir, self.expt_name, 'All_Age_Monthly_Cases.png'))


class AnnualAgebinPfPRAnalyzer(BaseAnalyzer):

    def __init__(self, expt_name, sweep_variables=None, agebin_name='customagebins', working_dir='./', start_year=2022,
                 end_year=2025, burnin=None):

        super(AnnualAgebinPfPRAnalyzer, self).__init__(working_dir=working_dir,
                                                       filenames=[
                                                           f"output/MalariaSummaryReport_Annual_Agebin.json"])
        self.sweep_variables = sweep_variables or ["Run_Number"]
        self.expt_name = expt_name
        self.start_year = start_year
        self.end_year = end_year
        self.burnin = burnin


    def select_simulation_data(self, data, simulation):

        adf = pd.DataFrame()
        for fname in self.filenames:

            nyears = (self.end_year - self.start_year)
            age_bins = data[fname]['Metadata']['Age Bins']
            pfpr2to10 = data[fname]['DataByTime']['PfPR_2to10'][:nyears]

            for age in list(range(0, len(age_bins))):
                d = data[fname]['DataByTimeAndAgeBins']['PfPR by Age Bin'][:nyears]
                pfpr = [x[age] for x in d]
                d = data[fname]['DataByTimeAndAgeBins']['Annual Clinical Incidence by Age Bin'][:nyears]
                clinical_cases = [x[age] for x in d]
                d = data[fname]['DataByTimeAndAgeBins']['Annual Severe Incidence by Age Bin'][:nyears]
                severe_cases = [x[age] for x in d]
                d = data[fname]['DataByTimeAndAgeBins']['Average Population by Age Bin'][:nyears]
                pop = [x[age] for x in d]

                simdata = pd.DataFrame({'year': range(self.start_year, self.end_year),
                                        'PfPR': pfpr,
                                        'Cases': clinical_cases,
                                        'Severe cases': severe_cases,
                                        'Pop': pop})
                simdata['agebin'] = age_bins[age]
                simdata['pfpr2to10'] = pfpr2to10
                adf = pd.concat([adf, simdata])

        for sweep_var in self.sweep_variables:
            if sweep_var in simulation.tags.keys():
                try:
                    adf[sweep_var] = simulation.tags[sweep_var]
                except:
                    adf[sweep_var] = '-'.join([str(x) for x in simulation.tags[sweep_var]])

        return adf

    def finalize(self, all_data):

        selected = [data for sim, data in all_data.items()]
        if len(selected) == 0:
            print("\nWarning: No data have been returned... Exiting...")
            return
        adf = pd.concat(selected).reset_index(drop=True)

        if not os.path.exists(os.path.join(self.working_dir, self.expt_name)):
            os.mkdir(os.path.join(self.working_dir, self.expt_name))

        print(f'\nSaving outputs to: {os.path.join(self.working_dir, self.expt_name)}')

        # Discard early years used as burnin
        if self.burnin is not None:
            adf = adf[adf['year'] >= self.start_year + self.burnin]
        adf = adf.loc[adf['agebin'] <= 100]
        adf.to_csv((os.path.join(self.working_dir, 'Agebin_PfPR_ClinicalIncidence_annual.csv')), index=False)

        # Figure with panel per outcome channel

        # Take mean across multiple years for plots per agebin on the x-axis
        channels = ['Pop', 'Cases', 'Severe cases', 'PfPR']
        self.sweep_variables = [x for x in self.sweep_variables if not x == 'Run_Number']
        adf = adf.groupby(['agebin'] + self.sweep_variables)[channels].agg(np.mean).reset_index()

        fig = plt.figure(figsize=(6, 5))
        fig.subplots_adjust(right=0.96, left=0.12, hspace=0.55, wspace=0.35, top=0.83, bottom=0.10)
        axes = [fig.add_subplot(2, 2, x + 1) for x in range(4)]
        fig.suptitle(f'Analyzer: AnnualAgebinPfPRAnalyzer')

        for ai, channel in enumerate(channels):
            ax = axes[ai]
            ax.set_title(channel)
            ax.set_ylabel(channel)
            if channel == 'PfPR':
                ax.set_ylim(0, 1)
            else:
                ax.set_ylim(0, np.max(adf[channel]))
            ax.set_xlabel('agebin')
            ax.plot(adf['agebin'], adf[channel], '-', color='black', linewidth=0.8)
        fig.savefig(os.path.join(self.working_dir, self.expt_name, 'Agebin_PfPR_ClinicalIncidence.png'))


if __name__ == "__main__":
    SetupParser.init()

    analyzers = [MonthlyInsetChartAnalyzer(expt_name=expt_name,
                                           working_dir=working_dir),
                 AnnualAgebinPfPRAnalyzer(expt_name=expt_name,
                                          working_dir=working_dir,
                                          start_year=2022,
                                          end_year=2025)
                 ]

    am = AnalyzeManager(expt_id, analyzers=analyzers)
    am.analyze()
