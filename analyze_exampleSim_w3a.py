from simtools.Analysis.AnalyzeManager import AnalyzeManager
from simtools.SetupParser import SetupParser

from analyzer_collection import *

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# This block will be used unless overridden on the command-line
SetupParser.default_block = 'LOCAL'

user = os.getlogin()  # user initials
expt_name = f'{user}_FE_2022_example_w3a'
expt_id = '2022_05_12_16_49_45_242132'  ## change expt_id
working_dir = os.path.join('simulation_outputs')


def plot_inset_chart(channels_inset_chart) :

    # read in analyzed InsetChart data
    df = pd.read_csv(os.path.join(working_dir, expt_name, 'All_Age_InsetChart.csv'))
    df['date'] = pd.to_datetime(df['date'])

    # make InsetChart plot
    fig1 = plt.figure('InsetChart', figsize=(12,6))
    fig1.subplots_adjust(hspace=0.5, left=0.08, right=0.97)
    fig1.suptitle(f'Analyzer: InsetChartAnalyzer')
    for ch, channel in enumerate(channels_inset_chart) :
        ax = fig1.add_subplot(2,2,ch+1)
        ax.plot(df['date'], df[channel], '-', linewidth=0.8)
        ax.set_title(channel)
        ax.set_ylabel(channel)
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=12))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    fig1.savefig(os.path.join(working_dir, expt_name, 'InsetChart.png'))


def plot_summary_report() :

    # read in analyzed summary reporrt
    channels_summary_report = ['Pop', 'Cases', 'Severe cases', 'PfPR']
    df = pd.read_csv(os.path.join(working_dir, expt_name, 'Agebin_PfPR_ClinicalIncidence_annual.csv'))
    df = df.sort_values(by='agebin')
    # take mean over all years in report
    df = df.groupby(['agebin', 'Run_Number'])[channels_summary_report].agg(np.mean).reset_index()

    # make summary report plot
    fig2 = plt.figure('Summary Report', figsize=(6, 5))
    fig2.subplots_adjust(right=0.96, left=0.12, hspace=0.55, wspace=0.35, top=0.83, bottom=0.10)
    axes = [fig2.add_subplot(2, 2, x + 1) for x in range(4)]
    fig2.suptitle(f'Analyzer: AnnualAgebinPfPRAnalyzer')

    for ai, channel in enumerate(channels_summary_report):
        ax = axes[ai]
        ax.set_title(channel)
        ax.set_ylabel(channel)
        ax.set_ylim(0, max([1, 1.1*np.max(df[channel])]))
        ax.set_xlabel('age')

        ax.plot(df['agebin'], df[channel], '-', linewidth=0.8)

    fig2.savefig(os.path.join(working_dir, expt_name, 'Agebin_PfPR_ClinicalIncidence.png'))


def plot_events(event_list) :

    # read in analyzed event data
    df = pd.read_csv(os.path.join(working_dir, expt_name, 'Event_Count.csv'))
    df['date'] = pd.to_datetime(df['date'])
    cov_channel_list = ['%s_Coverage' % x[9:] for x in event_list]
    cov_channel_list = [x for x in cov_channel_list if x in df.columns.values]
    df = df.groupby(['date'])[event_list + cov_channel_list].agg(np.mean).reset_index()

    # make event plot
    fig3 = plt.figure('Events', figsize=(12,3*len(event_list)))
    fig3.subplots_adjust(hspace=0.5, left=0.08, right=0.97)
    fig3.suptitle(f'Analyzer: ReceivedCampaignAnalyzer')
    axes = [fig3.add_subplot(len(event_list), 2, x + 1) for x in range(len(event_list)*2)]
    for ch, channel in enumerate(event_list) :
        ax = axes[ch*2]
        ax.plot(df['date'], df[channel], '-', linewidth=0.8)
        ax.set_title(channel)
        ax.set_ylabel(channel)
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=12))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))

        coverage_channel = '%s_Coverage' % channel[9:]
        if coverage_channel not in df.columns.values :
            continue
        ax = axes[ch*2+1]
        ax.plot(df['date'], df[coverage_channel], '-', linewidth=0.8)
        ax.set_title(coverage_channel)
        ax.set_ylabel(coverage_channel)
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=12))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))

    fig3.savefig(os.path.join(working_dir, expt_name, 'Events.png'))


if __name__ == "__main__":
    SetupParser.init()

    event_list = ['Received_Treatment', 'Received_ITN']
    channels_inset_chart = ['Statistical Population', 'New Clinical Cases', 'Adult Vectors', 'Infected']

    analyzers = [
        InsetChartAnalyzer(expt_name=expt_name,
                           channels=channels_inset_chart,
                           working_dir=working_dir),
        AnnualAgebinPfPRAnalyzer(expt_name=expt_name,
                                 working_dir=working_dir,
                                 start_year=2022),
        ReceivedCampaignAnalyzer(expt_name=expt_name,
                                 working_dir=working_dir,
                                 channels=event_list,
                                 start_year=2022)
    ]

    am = AnalyzeManager(expt_id, analyzers=analyzers)
    am.analyze()

    plot_inset_chart(channels_inset_chart)
    plot_summary_report()
    plot_events(event_list)
    plt.show()

