import os
import datetime
import pandas as pd
import numpy as np
from simtools.Analysis.AnalyzeManager import AnalyzeManager
from simtools.Analysis.BaseAnalyzers import BaseAnalyzer
from simtools.SetupParser import SetupParser

import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.dates as mdates
import seaborn as sns

mpl.rcParams['pdf.fonttype'] = 42
palette = sns.color_palette("tab10")

# This block will be used unless overridden on the command-line
SetupParser.default_block = 'LOCAL'

user = os.getlogin()  # user initials
expt_name = f'{user}_FE_2022_example_w4'
expt_id = '2022_04_26_09_11_01_710653'  ## change expt_id
working_dir = os.path.join('simulation_outputs')


class MonthlyInsetChartAnalyzer(BaseAnalyzer):

    @classmethod
    def monthparser(self, x):
        if x == 0:
            return 12
        else:
            return datetime.datetime.strptime(str(x), '%j').month

    def __init__(self, expt_name, sweep_variables=None, working_dir=".", start_year=2022, end_year=2023):
        super(MonthlyInsetChartAnalyzer, self).__init__(working_dir=working_dir, filenames=["output/InsetChart.json"])
        self.sweep_variables = sweep_variables or ["Run_Number"]
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


class IndividualEventsAnalyzer(BaseAnalyzer):

    @classmethod
    def monthparser(self, x):
        if x == 0:
            return 12
        else:
            return datetime.datetime.strptime(str(x), '%j').month

    def __init__(self, expt_name, sweep_variables=None, working_dir='./', start_year=2022,
                 selected_year=None, filter_exists=False):
        super(IndividualEventsAnalyzer, self).__init__(working_dir=working_dir,
                                                       filenames=["output/ReportEventRecorder.csv"]
                                                       )
        self.sweep_variables = sweep_variables or ["Run_Number"]
        self.expt_name = expt_name
        self.start_year = start_year
        self.selected_year = selected_year
        self.filter_exists = filter_exists  # flag used for NUCLUSTER

    def filter(self, simulation):
        if self.filter_exists:
            file = os.path.join(simulation.get_path(), self.filenames[0])
            return os.path.exists(file)
        else:
            return True

    def select_simulation_data(self, data, simulation):

        simdata = pd.DataFrame(data[self.filenames[0]])
        simdata['Day'] = simdata['Time'] % 365
        simdata['Month'] = simdata['Day'].apply(lambda x: self.monthparser((x + 1) % 365))
        simdata['Year'] = simdata['Time'].apply(lambda x: int(x / 365) + self.start_year)
        if self.selected_year is not None:
            simdata = simdata.loc[(simdata['Year'] == self.selected_year)]

        for sweep_var in self.sweep_variables:
            if sweep_var in simulation.tags.keys():
                try:
                    simdata[sweep_var] = simulation.tags[sweep_var]
                except:
                    simdata[sweep_var] = '-'.join([str(x) for x in simulation.tags[sweep_var]])
        return simdata

    def finalize(self, all_data):

        selected = [data for sim, data in all_data.items()]
        if len(selected) == 0:
            print("\nWarning: No data have been returned... Exiting...")
            return

        if self.selected_year is not None:
            selected_year_suffix = f'_{self.selected_year}'
        else:
            selected_year_suffix = '_all_years'

        if not os.path.exists(os.path.join(self.working_dir, self.expt_name)):
            os.mkdir(os.path.join(self.working_dir, self.expt_name))

        print(f'\nSaving outputs to: {os.path.join(self.working_dir, self.expt_name)}')

        adf = pd.concat(selected).reset_index(drop=True)
        adf.to_csv(os.path.join(self.working_dir, self.expt_name, f'IndividualEvents{selected_year_suffix}.csv'),
                   index=False)


class TransmissionReport(BaseAnalyzer):

    @classmethod
    def monthparser(self, x):
        if x == 0:
            return 12
        else:
            return datetime.datetime.strptime(str(x), '%j').month

    def __init__(self, expt_name, channels=None, sweep_variables=None, working_dir='./', start_year=2022,
                 selected_year=None, daily_report=False, monthly_report=False, filter_exists=False):
        super(TransmissionReport, self).__init__(working_dir=working_dir,
                                                 filenames=["output/ReportMalariaFiltered.json"])
        self.sweep_variables = sweep_variables or ["Run_Number"]
        self.channels = channels or ['Daily Bites per Human', 'Daily EIR', 'Mean Parasitemia', 'PfHRP2 Prevalence',
                                     'Rainfall']
        self.start_year = start_year
        self.selected_year = selected_year
        self.daily_report = daily_report
        self.monthly_report = monthly_report
        self.expt_name = expt_name
        self.filter_exists = filter_exists

    def filter(self, simulation):
        if self.filter_exists:
            file = os.path.join(simulation.get_path(), self.filenames[0])
            return os.path.exists(file)
        else:
            return True

    def select_simulation_data(self, data, simulation):
        simdata = pd.DataFrame({x: data[self.filenames[0]]['Channels'][x]['Data'] for x in self.channels})
        # simdata = simdata[-365:]
        simdata['Time'] = simdata.index
        simdata['Day'] = simdata['Time'] % 365
        simdata['Month'] = simdata['Day'].apply(lambda x: self.monthparser((x + 1) % 365))
        simdata['Year'] = simdata['Time'].apply(lambda x: int(x / 365) + self.start_year)
        simdata['date'] = simdata.apply(lambda x: datetime.date(int(x['Year']), int(x['Month']), 1), axis=1)
        if self.selected_year is not None:
            simdata = simdata.loc[(simdata['Year'] == self.selected_year)]

        simdata = simdata.groupby(['Time', 'date', 'Day', 'Month', 'Year'])[self.channels].agg(np.mean).reset_index()

        for sweep_var in self.sweep_variables:
            if sweep_var in simulation.tags.keys():
                try:
                    simdata[sweep_var] = simulation.tags[sweep_var]
                except:
                    simdata[sweep_var] = '-'.join([str(x) for x in simulation.tags[sweep_var]])
        return simdata

    def finalize(self, all_data):

        selected = [data for sim, data in all_data.items()]
        if len(selected) == 0:
            print("\nWarning: No data have been returned... Exiting...")
            return

        adf = pd.concat(selected).reset_index(drop=True)

        if not os.path.exists(os.path.join(self.working_dir, self.expt_name)):
            os.mkdir(os.path.join(self.working_dir, self.expt_name))
        print(f'\nSaving outputs to: {os.path.join(self.working_dir, self.expt_name)}')

        if self.selected_year is not None:
            selected_year_suffix = f'_{self.selected_year}'
        else:
            selected_year_suffix = '_all_years'

        ## Aggregate Run_Number
        grp_channels = [x for x in self.sweep_variables if x != "Run_Number"]
        adf = adf.groupby(['Time', 'date', 'Day', 'Month', 'Year'] + grp_channels)[self.channels].agg(
            np.mean).reset_index()

        sum_channels = ['Daily Bites per Human', 'Daily EIR', 'Rainfall']
        mean_channels = ['Mean Parasitemia', 'PfHRP2 Prevalence']
        ### DAILY TRANSMISSION
        if self.daily_report:
            adf.to_csv(
                os.path.join(self.working_dir, self.expt_name, f'daily_transmission_report{selected_year_suffix}.csv'),
                index=False)

        ### MONTHLY TRANSMISSION
        if self.monthly_report:
            df = adf.groupby(['date', 'Year', 'Month'] + grp_channels)[sum_channels].agg(np.sum).reset_index()
            pdf = adf.groupby(['date', 'Year', 'Month'] + grp_channels)[mean_channels].agg(np.mean).reset_index()
            mdf = pd.merge(left=pdf, right=df, on=['date', 'Year', 'Month'] + grp_channels)
            mdf = mdf.rename(columns={'Daily Bites per Human': 'Monthly Bites per Human', 'Daily EIR': 'Monthly EIR'})
            mdf.to_csv(os.path.join(self.working_dir, self.expt_name,
                                    f'monthly_transmission_report{selected_year_suffix}.csv'), index=False)

        ### ANNUAL TRANSMISSION
        df = adf.groupby(['Year'] + grp_channels)[sum_channels].agg(np.sum).reset_index()
        pdf = adf.groupby(['Year'] + grp_channels)[mean_channels].agg(np.mean).reset_index()
        adf = pd.merge(left=pdf, right=df, on=['Year'] + grp_channels)
        adf = adf.rename(columns={'Daily Bites per Human': 'Annual Bites per Human', 'Daily EIR': 'Annual EIR'})
        adf.to_csv(
            os.path.join(self.working_dir, self.expt_name, f'annual_transmission_report{selected_year_suffix}.csv'),
            index=False)


class BednetUsageAnalyzer(BaseAnalyzer):

    @classmethod
    def monthparser(self, x):
        if x == 0:
            return 12
        else:
            return datetime.datetime.strptime(str(x), '%j').month

    def __init__(self, expt_name, channels=None, sweep_variables=None, working_dir='./', start_year=2022,
                 selected_year=None, filter_exists=False):
        super(BednetUsageAnalyzer, self).__init__(working_dir=working_dir,
                                                  filenames=["output/ReportEventCounter.json",
                                                             "output/ReportMalariaFiltered.json"])
        self.sweep_variables = sweep_variables or ["Run_Number"]
        self.channels = channels or ['Bednet_Using', 'Bednet_Got_New_One']
        self.inset_channels = ['Statistical Population']
        self.start_year = start_year
        self.selected_year = selected_year
        self.expt_name = expt_name
        self.filter_exists = filter_exists

    def filter(self, simulation):
        if self.filter_exists:
            file = os.path.join(simulation.get_path(), self.filenames[0])
            return os.path.exists(file)
        else:
            return True

    def select_simulation_data(self, data, simulation):

        simdata = pd.DataFrame({x: data[self.filenames[1]]['Channels'][x]['Data'] for x in self.inset_channels})
        simdata['Time'] = simdata.index

        if self.channels:
            d = pd.DataFrame({x: data[self.filenames[0]]['Channels'][x]['Data'] for x in self.channels})
            # d = pd.DataFrame({x: data[self.filenames[0]]['Channels'][x]['Data'][:len(simdata)] for x in self.channels})
            d['Time'] = d.index
            simdata = pd.merge(left=simdata, right=d, on='Time')

        simdata['Day'] = simdata['Time'] % 365
        simdata['Month'] = simdata['Day'].apply(lambda x: self.monthparser((x + 1) % 365))
        simdata['Year'] = simdata['Time'].apply(lambda x: int(x / 365) + self.start_year)

        if self.selected_year is not None:
            simdata = simdata.loc[(simdata['Year'] == self.selected_year)]

        for sweep_var in self.sweep_variables:
            if sweep_var in simulation.tags.keys():
                try:
                    simdata[sweep_var] = simulation.tags[sweep_var]
                except:
                    simdata[sweep_var] = '-'.join([str(x) for x in simulation.tags[sweep_var]])
        return simdata

    def finalize(self, all_data):

        selected = [data for sim, data in all_data.items()]
        if len(selected) == 0:
            print("\nWarning: No data have been returned... Exiting...")
            return

        adf = pd.concat(selected).reset_index(drop=True)
        adf['date'] = adf.apply(lambda x: datetime.date(int(x['Year']), int(x['Month']), 1), axis=1)

        if not os.path.exists(os.path.join(self.working_dir, self.expt_name)):
            os.mkdir(os.path.join(self.working_dir, self.expt_name))
        print(f'\nSaving outputs to: {os.path.join(self.working_dir, self.expt_name)}')

        ## Aggregate time to months
        sum_channels = ['Bednet_Got_New_One']
        for x in [y for y in sum_channels if y not in adf.columns.values]:
            adf[x] = 0
        mean_channels = ['Statistical Population', 'Bednet_Using']
        df = adf.groupby(['date'] + self.sweep_variables)[sum_channels].agg(np.sum).reset_index()
        pdf = adf.groupby(['date'] + self.sweep_variables)[mean_channels].agg(np.mean).reset_index()

        adf = pd.merge(left=pdf, right=df, on=['date'] + self.sweep_variables)
        adf['mean_usage'] = adf['Bednet_Using'] / adf['Statistical Population']
        adf['new_net_coverage'] = adf['Bednet_Got_New_One'] / adf['Statistical Population']
        adf.to_csv(os.path.join(self.working_dir, self.expt_name, f'BednetUsageAnalyzer.csv'), index=False)


class ReceivedCampaignAnalyzer(BaseAnalyzer):

    @classmethod
    def monthparser(self, x):
        if x == 0:
            return 12
        else:
            return datetime.datetime.strptime(str(x), '%j').month

    def __init__(self, expt_name, channels=None, sweep_variables=None, working_dir='./', start_year=2022,
                 selected_year=None, daily_report=False, monthly_report=False, filter_exists=False):
        super(ReceivedCampaignAnalyzer, self).__init__(working_dir=working_dir,
                                                       filenames=["output/ReportEventCounter.json",
                                                                  "output/ReportMalariaFiltered.json"])
        self.sweep_variables = sweep_variables or ["Run_Number"]
        self.channels = channels or ['Received_Treatment']
        self.inset_channels = ['Statistical Population']
        self.start_year = start_year
        self.selected_year = selected_year
        self.expt_name = expt_name
        self.filter_exists = filter_exists

    def filter(self, simulation):
        if self.filter_exists:
            file = os.path.join(simulation.get_path(), self.filenames[0])
            return os.path.exists(file)
        else:
            return True

    def select_simulation_data(self, data, simulation):

        simdata = pd.DataFrame({x: data[self.filenames[1]]['Channels'][x]['Data'] for x in self.inset_channels})
        simdata['Time'] = simdata.index

        if self.channels:
            d = pd.DataFrame({x: data[self.filenames[0]]['Channels'][x]['Data'] for x in self.channels})
            # d = pd.DataFrame({x: data[self.filenames[0]]['Channels'][x]['Data'][:len(simdata)] for x in self.channels})
            d['Time'] = d.index
            simdata = pd.merge(left=simdata, right=d, on='Time')

        simdata['Day'] = simdata['Time'] % 365
        simdata['Month'] = simdata['Day'].apply(lambda x: self.monthparser((x + 1) % 365))
        simdata['Year'] = simdata['Time'].apply(lambda x: int(x / 365) + self.start_year)

        if self.selected_year is not None:
            simdata = simdata.loc[(simdata['Year'] == self.selected_year)]

        for sweep_var in self.sweep_variables:
            if sweep_var in simulation.tags.keys():
                try:
                    simdata[sweep_var] = simulation.tags[sweep_var]
                except:
                    simdata[sweep_var] = '-'.join([str(x) for x in simulation.tags[sweep_var]])
        return simdata

    def finalize(self, all_data):

        selected = [data for sim, data in all_data.items()]
        if len(selected) == 0:
            print("\nWarning: No data have been returned... Exiting...")
            return

        adf = pd.concat(selected).reset_index(drop=True)
        adf['date'] = adf.apply(lambda x: datetime.date(int(x['Year']), int(x['Month']), 1), axis=1)

        if not os.path.exists(os.path.join(self.working_dir, self.expt_name)):
            os.mkdir(os.path.join(self.working_dir, self.expt_name))
        print(f'\nSaving outputs to: {os.path.join(self.working_dir, self.expt_name)}')

        ## Aggregate
        sum_channels = self.channels
        for x in [y for y in sum_channels if y not in adf.columns.values]:
            adf[x] = 0
        mean_channels = ['Statistical Population']
        df = adf.groupby(['date'] + self.sweep_variables)[sum_channels].agg(np.sum).reset_index()
        pdf = adf.groupby(['date'] + self.sweep_variables)[mean_channels].agg(np.mean).reset_index()

        adf = pd.merge(left=pdf, right=df, on=['date'] + self.sweep_variables)
        adf['Treatment_Coverage'] = adf['Received_Treatment'] / adf['Statistical Population']
        adf['SMC_Coverage'] = adf['Received_SMC'] / adf['Statistical Population']
        adf['IRS_Coverage'] = adf['Received_IRS'] / adf['Statistical Population']
        adf['Vaccine_Coverage'] = adf['Received_Vaccine'] / adf['Statistical Population']
        adf.to_csv(os.path.join(self.working_dir, self.expt_name, f'BednetUsageAnalyzer.csv'), index=False)


""""OTHER/NEW ANALYZER TO RUN AND TO INTRODUCE (TODO)""""


##TODO OTHER (to be tested on example sim with intructions
class MonthlyTreatedCasesAnalyzer(BaseAnalyzer):

    @classmethod
    def monthparser(self, x):
        if x == 0:
            return 12
        else:
            return datetime.datetime.strptime(str(x), '%j').month

    def __init__(self, expt_name, channels=None, sweep_variables=None, working_dir=".", start_year=2010,
                 end_year=2020, filter_exists=False):
        super(MonthlyTreatedCasesAnalyzer, self).__init__(working_dir=working_dir,
                                                          filenames=["output/ReportEventCounter.json",
                                                                     "output/ReportMalariaFiltered.json"]
                                                          )
        self.sweep_variables = sweep_variables or ["LGA", "Run_Number"]
        self.channels = channels or ['Received_Treatment']
        self.inset_channels = ['Statistical Population', 'New Infections', 'Newly Symptomatic', 'New Clinical Cases',
                               'New Severe Cases', 'PfHRP2 Prevalence']
        self.expt_name = expt_name
        self.start_year = start_year
        self.end_year = end_year
        self.filter_exists = filter_exists

    def filter(self, simulation):
        if self.filter_exists:
            file = os.path.join(simulation.get_path(), self.filenames[0])
            return os.path.exists(file)
        else:
            return True

    def select_simulation_data(self, data, simulation):
        simdata = pd.DataFrame({x: data[self.filenames[1]]['Channels'][x]['Data'] for x in self.inset_channels})
        simdata['Time'] = simdata.index
        if self.channels:
            d = pd.DataFrame({x: data[self.filenames[0]]['Channels'][x]['Data'] for x in self.channels})
            d['Time'] = d.index
            simdata = pd.merge(left=simdata, right=d, on='Time')
        simdata['Day'] = simdata['Time'] % 365
        simdata['Month'] = simdata['Day'].apply(lambda x: self.monthparser((x + 1) % 365))
        simdata['Year'] = simdata['Time'].apply(lambda x: int(x / 365) + self.start_year)
        if self.start_year > 0:
            simdata['date'] = simdata.apply(lambda x: datetime.date(int(x['Year']), int(x['Month']), 1), axis=1)
        else:
            simdata['date'] = simdata["Year"].astype(str) + '-' + simdata["Month"].astype(str) + '-' + simdata[
                "Day"].astype(str)

        sum_channels = self.channels + ['New Clinical Cases', 'New Severe Cases']
        mean_channels = ['Statistical Population', 'PfHRP2 Prevalence']
        for x in [y for y in sum_channels if y not in simdata.columns.values]:
            simdata[x] = 0

        df = simdata.groupby(['date'])[sum_channels].agg(np.sum).reset_index()
        pdf = simdata.groupby(['date'])[mean_channels].agg(np.mean).reset_index()

        simdata = pd.merge(left=pdf, right=df, on=['date'])

        for sweep_var in self.sweep_variables:
            if sweep_var in simulation.tags.keys():
                try:
                    simdata[sweep_var] = simulation.tags[sweep_var]
                except:
                    simdata[sweep_var] = '-'.join([str(x) for x in simulation.tags[sweep_var]])

        return simdata

    def finalize(self, all_data):

        selected = [data for sim, data in all_data.items()]
        if len(selected) == 0:
            print("No data have been returned... Exiting...")
            return

        if not os.path.exists(os.path.join(self.working_dir)):
            os.mkdir(os.path.join(self.working_dir))

        print(f'\nSaving outputs to: {os.path.join(self.working_dir)}')

        adf = pd.concat(selected).reset_index(drop=True)
        adf.to_csv(os.path.join(self.working_dir, 'All_Age_Monthly_Cases.csv'), index=False)


class MonthlyAgebinSevereTreatedAnalyzer(BaseAnalyzer):
    @classmethod
    def monthparser(self, x):
        if x == 0:
            return 12
        else:
            return datetime.datetime.strptime(str(x), '%j').month

    def __init__(self, expt_name, event_name='Received_Severe_Treatment', agebin_name='customagebins', agebins=None,
                 sweep_variables=None, IP_variable=None, working_dir=".", start_year=2000, end_year=2020,
                 filter_exists=False):
        super(MonthlyAgebinSevereTreatedAnalyzer, self).__init__(working_dir=working_dir,
                                                                 filenames=["output/ReportEventRecorder.csv"]
                                                                 )
        self.sweep_variables = sweep_variables or ["Run_Number"]
        self.IP_variable = IP_variable
        self.event_name = event_name
        self.agebin_name = agebin_name
        self.agebins = agebins or [2, 5, 10, 20, 100]
        self.expt_name = expt_name
        self.start_year = start_year
        self.end_year = end_year
        self.filter_exists = filter_exists

    def filter(self, simulation):
        if self.filter_exists:
            file = os.path.join(simulation.get_path(), self.filenames[0])
            return os.path.exists(file)
        else:
            return True

    def select_simulation_data(self, data, simulation):

        output_data = data[self.filenames[0]]
        output_data = output_data[output_data['Event_Name'] == self.event_name]

        simdata = pd.DataFrame()
        if len(output_data) > 0:  # there are events of this type
            output_data['Day'] = output_data['Time'] % 365
            output_data['month'] = output_data['Day'].apply(lambda x: self.monthparser((x + 1) % 365))
            output_data['year'] = output_data['Time'].apply(lambda x: int(x / 365) + self.start_year)
            output_data['age in years'] = output_data['Age'] / 365

            for i, agemax in enumerate(self.agebins):
                if i == 0:
                    agemin = 0
                else:
                    agemin = self.agebins[i - 1]

                d = output_data[(output_data['age in years'].between(agemin, agemax))]
                g = d.groupby(list(filter(None, ['year', 'month'] + [self.IP_variable])))['Event_Name'].agg(
                    len).reset_index()
                g = g.rename(columns={'Event_Name': 'Num_Received_Severe_Treatment'})
                if simdata.empty:
                    simdata = g
                    simdata['agebin'] = agemax
                else:
                    if not g.empty:
                        g['agebin'] = agemax
                        simdata = pd.concat([g, simdata])
                        simdata = simdata.fillna(0)

            for sweep_var in self.sweep_variables:
                if sweep_var in simulation.tags.keys():
                    try:
                        simdata[sweep_var] = simulation.tags[sweep_var]
                    except:
                        simdata[sweep_var] = '-'.join([str(x) for x in simulation.tags[sweep_var]])
        else:
            simdata = pd.DataFrame(
                columns=list(filter(None, ['year', 'month', 'agebin', 'Num_Received_Severe_Treatment'] +
                                    self.sweep_variables + [self.IP_variable])))
        return simdata

    def finalize(self, all_data):

        selected = [data for sim, data in all_data.items()]
        if len(selected) == 0:
            print("No data have been returned... Exiting...")
            return

        if not os.path.exists(os.path.join(self.working_dir, self.expt_name)):
            os.mkdir(os.path.join(self.working_dir, self.expt_name))

        adf = pd.concat(selected, sort=False).reset_index(drop=True)
        adf = adf.fillna(0)

        merged_df_all = pd.DataFrame()
        for i, agebin in enumerate(self.agebins):

            # Does not support IPfilter, currently also not needed
            if os.path.exists(os.path.join(self.working_dir, f'{self.agebin_name}_PfPR_ClinicalIncidence.csv')):
                severe_treat_df = adf[
                    ['year', 'month', 'agebin', 'Num_Received_Severe_Treatment'] + self.sweep_variables]
                severe_treat_df = severe_treat_df[(severe_treat_df['agebin'] == agebin)]
                # cast to int65 data type for merge with incidence df
                severe_treat_df = severe_treat_df.astype({'month': 'int64', 'year': 'int64', 'Run_Number': 'int64'})

                # combine with existing columns of the clinical incidence and PfPR dataframe
                incidence_df = pd.read_csv(
                    os.path.join(self.working_dir, f'{self.agebin_name}_PfPR_ClinicalIncidence.csv'))
                incidence_df = incidence_df[(incidence_df['agebin'] == agebin)]
                merged_df = pd.merge(left=incidence_df, right=severe_treat_df,
                                     on=self.sweep_variables + ['year', 'month', 'agebin'],
                                     how='left')
                merged_df = merged_df.fillna(0)

                # fix any excess treated cases!
                merged_df['num severe cases'] = merged_df['Severe cases'] * merged_df['Pop'] * 30 / 365
                merged_df['excess sev treat'] = merged_df['Num_Received_Severe_Treatment'] - merged_df[
                    'num severe cases']
                merged_df['sweep_id'] = merged_df.groupby(self.sweep_variables, sort=False).ngroup().apply(
                    '{:010}'.format)

                for (rn, sweep), rdf in merged_df.groupby(['Run_Number', 'sweep_id']):
                    for r, row in rdf.iterrows():
                        if row['excess sev treat'] < 1:
                            continue
                        # fix Jan 2020 (start of sim) excess treated severe cases
                        if row['year'] == self.start_year and row['month'] == 1:
                            merged_df.loc[(merged_df['year'] == self.start_year) & (merged_df['month'] == 1) & (
                                    merged_df['Run_Number'] == rn) & (merged_df['sweep_id'] == sweep),
                                          'Num_Received_Severe_Treatment'] = np.sum(
                                merged_df[(merged_df['year'] == self.start_year) &
                                          (merged_df['month'] == 1) &
                                          (merged_df['Run_Number'] == rn) &
                                          (merged_df['sweep_id'] == sweep)]['num severe cases'])
                        else:
                            # figure out which is previous month
                            newyear = row['year']
                            newmonth = row['month'] - 1
                            if newmonth < 1:
                                newyear -= 1
                            excess = row['excess sev treat']
                            merged_df.loc[(merged_df['year'] == self.start_year) & (merged_df['month'] == 1) & (
                                    merged_df['Run_Number'] == rn) & (merged_df[
                                                                          'sweep_id'] == sweep), 'Num_Received_Severe_Treatment'] = \
                                merged_df.loc[(merged_df['year'] == self.start_year) & (merged_df['month'] == 1) & (
                                        merged_df['Run_Number'] == rn) & (merged_df['sweep_id'] == sweep),
                                              'Num_Received_Severe_Treatment'] - excess
                            merged_df.loc[(merged_df['year'] == self.start_year) & (merged_df['month'] == 1) & (
                                    merged_df['Run_Number'] == rn) & (merged_df[
                                                                          'sweep_id'] == sweep), 'Num_Received_Severe_Treatment'] = \
                                merged_df.loc[(merged_df['year'] == self.start_year) & (merged_df['month'] == 1) & (
                                        merged_df['Run_Number'] == rn) & (merged_df['sweep_id'] == sweep),
                                              'Num_Received_Severe_Treatment'] + excess
                merged_df['excess sev treat'] = merged_df['Num_Received_Severe_Treatment'] - \
                                                merged_df['num severe cases']
                merged_df.loc[
                    merged_df['excess sev treat'] > 0.5, 'Num_Received_Severe_Treatment'] = \
                    merged_df.loc[merged_df['excess sev treat'] > 0.5, 'num severe cases']

                del merged_df['num severe cases']
                del merged_df['excess sev treat']
                if merged_df_all.empty:
                    merged_df_all = merged_df
                else:
                    merged_df_all = pd.concat([merged_df_all, merged_df])
                # merged_df.to_csv(os.path.join(self.working_dir,
                #                              f'{self.agebin_name}_PfPR_ClinicalIncidence_severeTreatment_{agebin}.csv'), index=False)
            else:
                pass
        merged_df_all.to_csv(os.path.join(self.working_dir,
                                          f'{self.agebin_name}_PfPR_ClinicalIncidence_severeTreatment.csv'),
                             index=False)


class HRP2PrevalenceAnalyzer(BaseAnalyzer):

    def __init__(self, expt_name, sweep_variables=None, working_dir='./',
                 filter_exists=False):  # sweep_variables=None,

        super(HRP2PrevalenceAnalyzer, self).__init__(working_dir=working_dir,
                                                     filenames=["output/ReportEventCounter.json"])
        self.sweep_variables = sweep_variables
        self.expt_name = expt_name
        self.data_channel_type = 'Channels'
        self.channel_name = 'HRP2'
        self.ages = range(5)
        self.age_range = ['%d_to_%d' % (x, x + 1) for x in self.ages]
        self.data_channels = ['Received_Test_Age_%s' % x for x in self.age_range] + \
                             ['Tested_Pos_Age_%s' % x for x in self.age_range]

        self.reference_dict = {
            'post': {
                'Ref_HRP2_0_to_1': 0.09,
                'Ref_HRP2_1_to_2': 0.11,
                'Ref_HRP2_2_to_3': 0.18,
                'Ref_HRP2_3_to_4': 0.20,
                'Ref_HRP2_4_to_5': 0.21
            },
            'pre': {
                'Ref_HRP2_0_to_1': 0.19,
                'Ref_HRP2_1_to_2': 0.29,
                'Ref_HRP2_2_to_3': 0.41,
                'Ref_HRP2_3_to_4': 0.53,
                'Ref_HRP2_4_to_5': 0.58
            }
        }
        self.filter_exists = filter_exists

    def filter(self, simulation):
        if self.filter_exists:
            file = os.path.join(simulation.get_path(), self.filenames[0])
            return os.path.exists(file)
        else:
            return True

    def select_simulation_data(self, data, simulation):

        # Load last 2 years of data from simulation
        output_data_df = pd.DataFrame(
            {channel: data[self.filenames[0]]['Channels'][channel]['Data'][-730:] for channel in self.data_channels})
        # remove dates when there were no prevalence surveys
        output_data_df['day'] = output_data_df.index
        output_data_df = output_data_df[output_data_df[self.data_channels[0]] > 0]
        # calculate prevalence
        for agebin in self.age_range:
            output_data_df['Prevalence_Age_%s' % agebin] = output_data_df['Tested_Pos_Age_%s' % agebin] / \
                                                           output_data_df['Received_Test_Age_%s' % agebin]

        # reorient dataframe to long format
        simdata = pd.DataFrame()
        cols = [x for x in output_data_df.columns.values if 'Prevalence' in x]
        for col in cols:
            sdf = output_data_df[['day', col]]
            sdf = sdf.rename(columns={col: self.channel_name})
            sdf['Age'] = int(col.split('_')[-1]) - 1
            simdata = pd.concat([simdata, sdf])

        # add tags
        for sweep_var in self.sweep_variables:
            if sweep_var in simulation.tags.keys():
                try:
                    simdata[sweep_var] = simulation.tags[sweep_var]
                except:
                    simdata[sweep_var] = '-'.join([str(x) for x in simulation.tags[sweep_var]])

        return simdata

    def finalize(self, all_data):

        # concatenate all simulation data into one dataframe
        selected = [data for sim, data in all_data.items()]  # grab data in tuple form
        if len(selected) == 0:  # error out if no data selected
            print("\nNo data have been returned... Exiting...")
            return
        df = pd.concat(selected, sort=False).reset_index(drop=True)  # concat into dataframe
        grouping_list = self.sweep_variables
        grouping_list.append('Age')
        grouping_list.insert(0, 'day')

        df = df.groupby(grouping_list)['HRP2'].agg([np.min, np.mean, np.max]).reset_index()
        df = df.rename(columns={'amin': 'HRP2_min', 'mean': 'HRP2', 'amax': 'HRP2_max'})
        df = df.sort_values(by=grouping_list)
        df['Ref_HRP2'] = 0
        df['Distance'] = 0

        ages = df['Age'].unique()
        for ai in ages:
            ref_pre = self.reference_dict['pre']['Ref_HRP2_%s_to_%s' % (ai, ai + 1)]
            ref_post = self.reference_dict['post']['Ref_HRP2_%s_to_%s' % (ai, ai + 1)]
            df.loc[((df['day'] == 239) & (df['Age'] == ai)), 'Ref_HRP2'] = ref_pre
            df.loc[((df['day'] == 604) & (df['Age'] == ai)), 'Ref_HRP2'] = ref_post
            df.loc[((df['day'] == 239) & (df['Age'] == ai)), 'Distance'] = np.sqrt(
                (df.loc[((df['day'] == 239) & (df['Age'] == ai)), 'HRP2'] - ref_pre) ** 2)
            df.loc[((df['day'] == 604) & (df['Age'] == ai)), 'Distance'] = np.sqrt(
                (df.loc[((df['day'] == 604) & (df['Age'] == ai)), 'HRP2'] - ref_post) ** 2)

        if not os.path.exists(os.path.join(self.working_dir, self.expt_name)):
            os.mkdir(os.path.join(self.working_dir, self.expt_name))

        print(f'\nSaving outputs to: {os.path.join(self.working_dir, self.expt_name)}')
        df.to_csv(os.path.join(self.working_dir, self.expt_name, 'hrp2_prevalence.csv'))


if __name__ == "__main__":
    SetupParser.init()

    sweep_variables = ['cm_cov_U5', 'smc_coverage', 'itn_coverage',
                       'irs_coverage', 'rtss_coverage', 'Run_Number']

    analyzers = [
        # MonthlyInsetChartAnalyzer(expt_name=expt_name,
        #                           working_dir=working_dir,
        #                           sweep_variables=sweep_variables),
        AnnualAgebinPfPRAnalyzer(expt_name=expt_name,
                                 working_dir=working_dir,
                                 start_year=2022,
                                 end_year=2025,
                                 sweep_variables=sweep_variables),
        BednetUsageAnalyzer(expt_name=expt_name,
                            working_dir=working_dir,
                            start_year=2022,
                            sweep_variables=sweep_variables),
        ReceivedCampaignAnalyzer(expt_name=expt_name,
                                 working_dir=working_dir,
                                 channels=['Received_Treatment', 'Received_IRS',
                                           'Received_SMC', 'Received_Vaccine'],
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
