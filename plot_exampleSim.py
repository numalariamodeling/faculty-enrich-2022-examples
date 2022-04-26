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

user = os.getlogin()  # user initials
expt_name = f'{user}_FE_2022_example_w4'
working_dir = os.path.join('simulation_outputs')

""" ~~WORK IN PROGRESS ~~ """


def plot_All_Age_Monthly_Cases(df, channels):
    # Figure with panel per outcome channel
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
        ax.set_xlabel('Month')
        ax.set_xticks(range(1, 13))
        ax.set_xticklabels(range(1, 13))

        for si, scen in enumerate(df['unique_sweep'].unique()):
            sdf = df[df['unique_sweep'] == scen]
            ax.plot(sdf['Month'], sdf[channel], '-', color=palette[si], linewidth=0.8, label=scen)

    axes[0].legend(title="Unique sweep")
    fig.savefig(os.path.join(working_dir, expt_name, 'All_Age_Monthly_Cases.png'))


def plot_Agebin_PfPR_ClinicalIncidence(df, grp_channels, channels=None):
    if channels is None:
        channels = ['Pop', 'Cases', 'Severe cases', 'PfPR']

    df = df.groupby(['agebin'] + grp_channels)[channels].agg(np.mean).reset_index()
    df['unique_sweep'] = df[grp_channels].apply(lambda x: ",".join(x.astype(str)), axis=1)

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


def plot_TransmissionReport(df, grp_channels, channels=None, time_res='monthly'):
    if channels is None:
        channels = ['Daily Bites per Human', 'Daily EIR', 'Rainfall', 'PfHRP2 Prevalence']

    df = df.groupby(['date', 'Year', 'Month'] + grp_channels)[channels].agg(np.mean).reset_index()
    df['unique_sweep'] = df[grp_channels].apply(lambda x: ",".join(x.astype(str)), axis=1)

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
        ax.set_xlabel('Time (days)')

        for si, scen in enumerate(df['unique_sweep'].unique()):
            sdf = df[df['unique_sweep'] == scen]
            ax.plot(sdf['date'], sdf[channel], '-', color=palette[si], linewidth=0.8, label=scen)

    axes[0].legend(title="Unique sweep")
    fig.savefig(os.path.join(working_dir, expt_name, f'TransmissionReport_{time_res}.png'))


def plot_BednetUsage(df, grp_channels, channels=None):
    if channels is None:
        channels = ['Bednet_Using', 'Bednet_Got_New_One', 'mean_usage', 'new_net_coverage']

    df = df.groupby(['date'] + grp_channels)[channels].agg(np.mean).reset_index()
    df['unique_sweep'] = df[grp_channels].apply(lambda x: ",".join(x.astype(str)), axis=1)

    fig = plt.figure(figsize=(6, 5))
    fig.subplots_adjust(right=0.96, left=0.12, hspace=0.55, wspace=0.35, top=0.83, bottom=0.10)
    axes = [fig.add_subplot(2, 2, x + 1) for x in range(4)]
    fig.suptitle('BednetUsage')

    for ai, channel in enumerate(channels):
        ax = axes[ai]
        ax.set_title(channel)
        ax.set_ylabel(channel)
        if channel == 'mean_usage' or channel == 'new_net_coverage':
            ax.set_ylim(0, 1)
        else:
            ax.set_ylim(0, np.max(df[channel]))
        # ax.set_xlabel('Time (months)')   #FIXME use continuous months for visualization
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m\n%y'))

        for si, scen in enumerate(df['unique_sweep'].unique()):
            sdf = df[df['unique_sweep'] == scen]
            ax.plot(sdf['date'], sdf[channel], '-', color=palette[si], linewidth=0.8, label=scen)

    axes[0].legend(title="Unique sweep")
    fig.savefig(os.path.join(working_dir, expt_name, 'Bednet_Usage.png'))


def plot_ReceivedCampaigns(df, grp_channels, channels=None):
    if channels is None:
        channels = ['Received_Treatment', 'Received_SMC', 'Received_IRS', 'Received_Vaccine']
        # channels = ['Treatment_Coverage', 'SMC_Coverage', 'IRS_Coverage', 'Vaccine_Coverage']

    df = df.groupby(['date'] + grp_channels)[channels].agg(np.mean).reset_index()
    df['unique_sweep'] = df[grp_channels].apply(lambda x: ",".join(x.astype(str)), axis=1)

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
        # ax.set_xlabel('Time (months)')   #FIXME use continuous months for visualization
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m\n%y'))

        for si, scen in enumerate(df['unique_sweep'].unique()):
            sdf = df[df['unique_sweep'] == scen]
            ax.plot(sdf['date'], sdf[channel], '-', color=palette[si], linewidth=0.8, label=scen)

    axes[0].legend(title="Unique sweep")
    fig.savefig(os.path.join(working_dir, expt_name, 'Received_Campaigns.png'))


if __name__ == "__main__":

## Read data and plot
# plot_All_Age_Monthly_Cases()
# plot_Agebin_PfPR_ClinicalIncidence()
# plot_TransmissionReport()
# plot_BednetUsage()
# plot_ReceivedCampaigns()
