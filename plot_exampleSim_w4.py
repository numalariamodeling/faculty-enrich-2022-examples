import os
import datetime
import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.dates as mdates
import seaborn as sns

mpl.rcParams['pdf.fonttype'] = 42
palette = sns.color_palette("tab10")

def plot_All_Age_Monthly_Cases(sim_dir, channels=None, scen_channels=None):
    df = pd.read_csv(os.path.join(sim_dir, 'All_Age_Monthly_Cases.csv'))
    df['date'] = pd.to_datetime(df['date'])

    output_channels = ['Statistical Population', 'New Clinical Cases', 'New Severe Cases', 'PfHRP2 Prevalence',
                       'Received_Treatment', 'Received_Severe_Treatment']

    if channels is None:
        channels = ['Statistical Population', 'New Clinical Cases', 'New Severe Cases', 'PfHRP2 Prevalence']

    ## Automatically set variable to color by
    if scen_channels is None or len(scen_channels) > 1:
        scen_channels = [x for x in df.columns if x not in output_channels + ['date', 'Run_Number']]
        df['unique_sweep'] = df[scen_channels].apply(lambda x: ",".join(x.astype(str)), axis=1)
        scen_channel = 'unique_sweep'
    else:
        scen_channel = scen_channels[0]

    ## Aggregate runs
    df = df.groupby(['date', scen_channel])[output_channels].agg(np.mean).reset_index()

    ## Figure with panel per outcome channel
    fig = plt.figure(figsize=(6, 5))
    fig.subplots_adjust(right=0.96, left=0.12, hspace=0.55, wspace=0.35, top=0.83, bottom=0.10)
    axes = [fig.add_subplot(2, 2, x + 1) for x in range(4)]
    fig.suptitle('aggregated_malaria_burden_by_time')

    for ai, channel in enumerate(channels):
        ax = axes[ai]
        ax.set_title(channel)
        ax.set_ylabel(channel)
        if channel == 'PfHRP2 Prevalence':
            ax.set_ylim(0, 1)
        else:
            ax.set_ylim(0, np.max(df[channel]))
        ax.set_xlabel('Time')
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m\n%y'))

        for si, scen in enumerate(df[scen_channel].unique()):
            sdf = df[df[scen_channel] == scen]
            ax.plot(sdf['date'], sdf[channel], '-', color=palette[si], linewidth=0.8, label=scen)

    axes[0].legend(title="Unique sweep")
    fig.savefig(os.path.join(working_dir, expt_name, 'All_Age_Monthly_Cases.png'))


def plot_Agebin_PfPR_ClinicalIncidence(sim_dir, scen_channels=None, channels=None):
    df = pd.read_csv(os.path.join(sim_dir, 'Agebin_PfPR_ClinicalIncidence.csv'))
    df['date'] = df.apply(lambda x: datetime.date(int(x['year']), int(x['month']), 1), axis=1)

    output_channels = ['PfPR', 'Cases', 'Severe cases', 'Mild anaemia',
                       'Moderate anaemia', 'Severe anaemia', 'New infections',
                       'Mean Log Parasite Density', 'Pop']
    output_channels = [x for x in output_channels if x in df.columns]

    if channels is None:
        channels = ['Pop', 'Cases', 'Severe cases', 'PfPR']

    ## Automatically set variable to color by
    if scen_channels is None or len(scen_channels) > 1:
        scen_channels = [x for x in df.columns if
                         x not in output_channels + ['agebin', 'date', 'year', 'month', 'Run_Number']]
        df['unique_sweep'] = df[scen_channels].apply(lambda x: ",".join(x.astype(str)), axis=1)
        scen_channel = 'unique_sweep'
    else:
        scen_channel = scen_channels[0]
    df['unique_sweep'] = df[scen_channels].apply(lambda x: ",".join(x.astype(str)), axis=1)

    ## Aggregate runs and time (for simplicity take mean across all)!
    df = df.groupby(['agebin', scen_channel])[channels].agg(np.mean).reset_index()

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
            ax.set_ylim(0, np.max(df[channel]))
        ax.set_xlabel('agebin')

        for si, scen in enumerate(df['unique_sweep'].unique()):
            sdf = df[df['unique_sweep'] == scen]
            ax.plot(sdf['agebin'], sdf[channel], '-', color=palette[si], linewidth=0.8, label=scen)

    axes[0].legend(title="Unique sweep")
    fig.savefig(os.path.join(working_dir, expt_name, 'Agebin_PfPR_ClinicalIncidence.png'))


def plot_TransmissionReport(sim_dir, scen_channels=None, time_res='monthly', selected_year=None):
    if selected_year is not None:
        selected_year = f'_{selected_year}'
    else:
        selected_year = '_all_years'

    df = pd.read_csv(os.path.join(sim_dir, f'{time_res}_transmission_report{selected_year}.csv'))
    x_var ='Year'
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
        x_var = 'date'

    output_channels = ['Daily Bites per Human', 'Daily EIR', 'Mean Parasitemia', 'PfHRP2 Prevalence',
                       'Rainfall']

    time_channels = ['date', 'Year', 'Month']
    channels = ['Daily Bites per Human', 'Daily EIR', 'Rainfall', 'PfHRP2 Prevalence']
    if time_res == 'monthly':
        output_channels = [x.replace('Daily ', 'Monthly ') for x in output_channels]
        channels = [x.replace('Daily ', 'Monthly ') for x in channels]
        time_channels = ['date', 'Year', 'Month']
    if time_res == 'annual':
        output_channels = [x.replace('Daily ', 'Annual ') for x in output_channels]
        channels = [x.replace('Daily ', 'Annual ') for x in channels]
        time_channels = ['Year']

    ## Automatically set variable to color by
    if scen_channels is None or len(scen_channels) > 1:
        scen_channels = [x for x in df.columns if x not in output_channels + time_channels + ['Run_Number']]
        df['unique_sweep'] = df[scen_channels].apply(lambda x: ",".join(x.astype(str)), axis=1)
        scen_channel = 'unique_sweep'
    else:
        scen_channel = scen_channels[0]

    ## Aggregate runs
    df = df.groupby([x_var, scen_channel])[channels].agg(np.mean).reset_index()

    fig = plt.figure(figsize=(6, 5))
    fig.subplots_adjust(right=0.96, left=0.12, hspace=0.55, wspace=0.35, top=0.83, bottom=0.10)
    axes = [fig.add_subplot(2, 2, x + 1) for x in range(4)]
    fig.suptitle(f'Analyzer: TransmissionReport')

    for ai, channel in enumerate(channels):
        ax = axes[ai]
        ax.set_title(channel)
        ax.set_ylabel(channel)
        if channel == 'PfHRP2 Prevalence':
            ax.set_ylim(0, 1)
        else:
            ax.set_ylim(0, np.max(df[channel]))
        ax.set_xlabel('Time')

        for si, scen in enumerate(df['unique_sweep'].unique()):
            sdf = df[df['unique_sweep'] == scen]
            ax.plot(sdf[x_var], sdf[channel], '-', color=palette[si], linewidth=0.8, label=scen)

    axes[0].legend(title="Unique sweep")
    fig.savefig(os.path.join(working_dir, expt_name, f'TransmissionReport_{time_res}.png'))


def plot_ReceivedCampaigns(sim_dir, scen_channels=None, channels=None):
    df = pd.read_csv(os.path.join(sim_dir, 'monthly_Event_Count.csv'))
    df['date'] = pd.to_datetime(df['date'])

    output_channels = ['Statistical Population',
                       'Received_Treatment', 'Received_IRS', 'Received_SMC',
                       'Received_Vaccine', 'Received_ITN', 'Treatment_Coverage', 'SMC_Coverage',
                       'IRS_Coverage', 'Vaccine_Coverage', 'ITN_Coverage']
    output_channels = [x for x in output_channels if x in df.columns]

    ##subset of output_channels that are plotted
    if channels is None:
        channels = ['Received_Treatment', 'Received_SMC', 'Received_IRS', 'Received_Vaccine']  # Received_ITN
        # channels = ['Treatment_Coverage', 'SMC_Coverage', 'IRS_Coverage', 'Vaccine_Coverage']  # 'ITN_Coverage'

    ## Automatically set variable to color by
    if scen_channels is None or len(scen_channels) > 1:
        scen_channels = [x for x in df.columns if x not in output_channels + ['date','Run_Number']]
        df['unique_sweep'] = df[scen_channels].apply(lambda x: ",".join(x.astype(str)), axis=1)
        scen_channel = 'unique_sweep'
    else:
        scen_channel = scen_channels[0]

    ## Aggregate runs
    df = df.groupby(['date', scen_channel])[channels].agg(np.mean).reset_index()

    fig = plt.figure(figsize=(6, 5))
    fig.subplots_adjust(right=0.96, left=0.12, hspace=0.55, wspace=0.35, top=0.83, bottom=0.10)
    axes = [fig.add_subplot(2, 2, x + 1) for x in range(4)]
    fig.suptitle(f'Analyzer: ReceivedCampaignAnalyzer')

    for ai, channel in enumerate(channels):
        ax = axes[ai]
        ax.set_title(channel)
        ax.set_ylabel(channel)
        if 'Coverage' in channel:
            ax.set_ylim(0, 1)
        else:
            ax.set_ylim(0, np.max(df[channel]))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m\n%y'))

        for si, scen in enumerate(df['unique_sweep'].unique()):
            sdf = df[df['unique_sweep'] == scen]
            ax.plot(sdf['date'], sdf[channel], '-', color=palette[si], linewidth=0.8, label=scen)

    axes[0].legend(title="Unique sweep")
    fig.savefig(os.path.join(working_dir, expt_name, 'Received_Campaigns.png'))


if __name__ == "__main__":
    user = os.getlogin()  # user initials
    expt_name = f'{user}_FE_2022_example_w4'
    working_dir = os.path.join('simulation_outputs')
    sim_dir = os.path.join(working_dir, expt_name)

    ## Select which plots to generate
    """Malaria Burden over time"""
    plot_All_Age_Monthly_Cases(sim_dir)

    """Malaria Burden over age"""
    plot_Agebin_PfPR_ClinicalIncidence(sim_dir)

    """Event campaign and transmission plots"""
    plot_TransmissionReport(sim_dir)
    plot_ReceivedCampaigns(sim_dir)
