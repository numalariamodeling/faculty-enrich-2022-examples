library(dplyr)
library(tidyr)
library(data.table)
library(lubridate)
library(ggplot2)


plot_All_Age_Cases <- function(sim_dir, channels = NULL, scen_channels = NULL) {
  dat <- fread(file.path(sim_dir, 'All_Age_InsetChart.csv'))

  output_channels = c('Statistical Population', 'New Clinical Cases', 'New Severe Cases', 'PfHRP2 Prevalence')

  if (is.null(channels)) {
    channels = c('Statistical Population', 'New Clinical Cases', 'New Severe Cases', 'PfHRP2 Prevalence')
  }

  ## Automatically sset variable to color by
  if (is.null(scen_channels) | length(scen_channels) > 1) {
    scen_channels = colnames(dat)[!(colnames(dat)) %in% c(output_channels, 'date', 'Time', 'Day', 'Year', 'Run_Number')]
    dat = unite(dat, 'unique_sweep', scen_channels, sep = "_", remove = TRUE, na.rm = FALSE)
    scen_channel = 'unique_sweep'
  }else {
    scen_channel = scen_channels[0]
  }

  ## Aggregate runs
  dat <- dat %>%
    group_by_at(.vars = c('date', scen_channel)) %>%
    summarize_at(output_channels, .funs = 'mean')

  fig <- dat %>%
    pivot_longer(cols = -c('date', scen_channel)) %>%
    filter(name %in% channels) %>%
    ggplot() +
    geom_hline(yintercept = 0) +
    geom_line(aes(x = date, y = value, col = get(scen_channel))) +
    facet_wrap(~name, scales = 'free') +
    scale_x_date(date_breaks = '4 month', date_labels = "%b\n'%y") +
    labs(x = 'Time', color = scen_channel) +
    theme_minimal() +
    theme(panel.border = element_rect(color = 'black', fill = NA),
          plot.background = element_rect(, fill = 'white'),
          panel.background = element_rect(, fill = 'white'),
          panel.grid = element_blank())

  print(fig)
  ggsave("All_Age_InsetChart.png", plot = fig, path = sim_dir,
         width = 6, height = 6, device = "png")
}


plot_PfPR_ClinicalIncidence <- function(sim_dir, Uage = 'U5', channels = NULL, scen_channels = NULL) {
  dat <- fread(file.path(sim_dir, paste0(Uage, '_PfPR_ClinicalIncidence.csv'))) %>%
    rename_with(~gsub(paste0(" ", Uage), "", .x)) %>%
    mutate(date = make_date(year, month, '01'))

  output_channels = c('PfPR', 'Cases', 'Severe cases', 'Mild anaemia',
                      'Moderate anaemia', 'Severe anaemia', 'New infections',
                      'Mean Log Parasite Density', 'Pop')
  output_channels = output_channels[(output_channels %in% colnames(dat))]

  if (is.null(channels)) {
    channels = c('Pop', 'Cases', 'Severe cases', 'PfPR')
  }

  ## Automatically sset variable to color by
  if (is.null(scen_channels) | length(scen_channels) > 1) {
    scen_channels = colnames(dat)[!(colnames(dat)) %in% c(output_channels, 'date', 'year', 'month', 'Run_Number')]
    dat = unite(dat, 'unique_sweep', scen_channels, sep = "_", remove = TRUE, na.rm = FALSE)
    scen_channel = 'unique_sweep'
  }else {
    scen_channel = scen_channels[0]
  }

  ## Aggregate runs
  dat <- dat %>%
    group_by_at(.vars = c('date', 'year', scen_channel)) %>%
    summarize_at(output_channels, .funs = 'mean')

  fig <- dat %>%
    pivot_longer(cols = -c('date', 'year', scen_channel)) %>%
    filter(name %in% channels) %>%
    ggplot() +
    geom_hline(yintercept = 0) +
    geom_line(aes(x = date, y = value, col = as.factor(scen_channel))) +
    facet_wrap(~name, scales = 'free') +
    labs(x = 'Year', y = 'value', color = 'agebin') +
    theme_minimal() +
    theme(panel.border = element_rect(color = 'black', fill = NA),
          plot.background = element_rect(, fill = 'white'),
          panel.background = element_rect(, fill = 'white'),
          panel.grid = element_blank())

  print(fig)
  ggsave(paste0("PfPR_ClinicalIncidence_", Uage, ".png"), plot = fig, path = sim_dir,
         width = 5, height = 5, device = "png")
}


plot_Agebin_PfPR_ClinicalIncidence <- function(sim_dir, channels = NULL, scen_channels = NULL) {
  dat <- fread(file.path(sim_dir, 'Agebin_PfPR_ClinicalIncidence.csv'))

  output_channels = c('PfPR', 'Cases', 'Severe cases', 'Mild anaemia',
                      'Moderate anaemia', 'Severe anaemia', 'New infections',
                      'Mean Log Parasite Density', 'Pop')
  output_channels = output_channels[(output_channels %in% colnames(dat))]

  if (is.null(channels)) {
    channels = c('Pop', 'Cases', 'Severe cases', 'PfPR')
  }

  ## Automatically sset variable to color by
  if (is.null(scen_channels) | length(scen_channels) > 1) {
    scen_channels = colnames(dat)[!(colnames(dat)) %in% c(output_channels, 'agebin', 'date', 'year', 'month', 'Run_Number')]
    dat = unite(dat, 'unique_sweep', scen_channels, sep = "_", remove = TRUE, na.rm = FALSE)
    scen_channel = 'unique_sweep'
  }else {
    scen_channel = scen_channels[0]
  }

  ## Aggregate runs
  dat <- dat %>%
    group_by_at(.vars = c('agebin', scen_channel)) %>%
    summarize_at(output_channels, .funs = 'mean')

  fig <- dat %>%
    pivot_longer(cols = -c('agebin', scen_channel)) %>%
    filter(name %in% channels) %>%
    ggplot() +
    geom_hline(yintercept = 0) +
    geom_line(aes(x = agebin, y = value, col = get(scen_channel))) +
    facet_wrap(~name, scales = 'free') +
    labs(x = 'Agebin', color = scen_channel) +
    theme_minimal() +
    theme(panel.border = element_rect(color = 'black', fill = NA),
          plot.background = element_rect(, fill = 'white'),
          panel.background = element_rect(, fill = 'white'),
          panel.grid = element_blank())

  print(fig)
  ggsave("Agebin_PfPR_ClinicalIncidence.png", plot = fig, path = sim_dir,
         width = 5, height = 5, device = "png")
}


plot_TransmissionReport <- function(sim_dir, scen_channels = NULL, time_res = 'monthly', selected_year = NULL) {

  if (!is.null(selected_year)) {
    selected_year = paste0('_', selected_year)
  }else {
    selected_year = '_all_years'
  }

  dat <- fread(file.path(sim_dir, paste0(time_res, '_transmission_report', selected_year, '.csv')))
  x_var = 'Year'
  if (sum(grep('date', colnames(dat))) > 0) {
    x_var = 'date'
  }

  output_channels = c('Daily Bites per Human', 'Daily EIR', 'Mean Parasitemia', 'PfHRP2 Prevalence', 'Rainfall')
  channels = c('Daily Bites per Human', 'Daily EIR', 'Rainfall', 'PfHRP2 Prevalence')
  time_channels = c('date', 'Year', 'Month')

  if (time_res == 'monthly') {
    output_channels = gsub('Daily', 'Monthly', output_channels)
    channels = gsub('Daily', 'Monthly', channels)
    time_channels = c('date', 'Year', 'Month')
  }
  if (time_res == 'annual') {
    output_channels = gsub('Daily', 'Annual', output_channels)
    channels = gsub('Daily', 'Annual', channels)
    time_channels = c('Year')
  }


  ## Automatically sset variable to color by
  if (is.null(scen_channels) | length(scen_channels) > 1) {
    scen_channels = colnames(dat)[!(colnames(dat)) %in% c(output_channels, time_channels, 'Run_Number')]
    dat = unite(dat, 'unique_sweep', scen_channels, sep = "_", remove = TRUE, na.rm = FALSE)
    scen_channel = 'unique_sweep'
  }else {
    scen_channel = scen_channels[0]
  }

  ## Aggregate runs
  dat <- dat %>%
    group_by_at(.vars = c(x_var, scen_channel)) %>%
    summarize_at(channels, .funs = 'mean')

  fig <- dat %>%
    pivot_longer(cols = -c(x_var, scen_channel)) %>%
    filter(name %in% channels) %>%
    ggplot() +
    geom_hline(yintercept = 0) +
    geom_line(aes(x = get(x_var), y = value, col = get(scen_channel))) +
    facet_wrap(~name, scales = 'free') +
    labs(x = x_var, color = scen_channel) +
    theme_minimal() +
    theme(panel.border = element_rect(color = 'black', fill = NA),
          plot.background = element_rect(, fill = 'white'),
          panel.background = element_rect(, fill = 'white'),
          panel.grid = element_blank())

  if (x_var == 'date') {
    fig = fig +
      scale_x_date(date_breaks = '4 month', date_labels = "%b\n'%y")
  }

  print(fig)
  ggsave(paste0("TransmissionReport_", time_res, ".png"), plot = fig, path = sim_dir,
         width = 5, height = 5, device = "png")
}


plot_ReceivedCampaigns <- function(sim_dir, channels = NULL, scen_channels = NULL) {
  dat <- fread(file.path(sim_dir, 'monthly_Event_Count.csv'))

  output_channels = c('Statistical Population',
                      'Received_Treatment', 'Received_IRS', 'Received_SMC',
                      'Received_Vaccine', 'Received_ITN', 'Treatment_Coverage', 'SMC_Coverage',
                      'IRS_Coverage', 'Vaccine_Coverage', 'ITN_Coverage')

  output_channels = colnames(dat)[(colnames(dat)) %in% output_channels]
  if (is.null(channels)) {
    channels = c('Received_Treatment', 'Received_SMC', 'Received_IRS', 'Received_Vaccine')  # Received_ITN
    #channels = c('Treatment_Coverage', 'SMC_Coverage', 'IRS_Coverage', 'Vaccine_Coverage')   # 'ITN_Coverage'

  }

  ## Automatically sset variable to color by
  if (is.null(scen_channels) | length(scen_channels) > 1) {
    scen_channels = colnames(dat)[!(colnames(dat)) %in% c(output_channels, 'date', 'Run_Number')]
    dat = unite(dat, 'unique_sweep', scen_channels, sep = "_", remove = TRUE, na.rm = FALSE)
    scen_channel = 'unique_sweep'
  }else {
    scen_channel = scen_channels[0]
  }

  ## Aggregate runs
  dat <- dat %>%
    group_by_at(.vars = c('date', scen_channel)) %>%
    summarize_at(output_channels, .funs = 'mean')

  fig <- dat %>%
    pivot_longer(cols = -c('date', scen_channel)) %>%
    filter(name %in% channels) %>%
    ggplot() +
    geom_hline(yintercept = 0) +
    geom_line(aes(x = date, y = value, col = get(scen_channel))) +
    scale_x_date(date_breaks = '4 month', date_labels = "%b\n'%y") +
    facet_wrap(~name, scales = 'free') +
    labs(x = 'date', color = scen_channel) +
    theme_minimal() +
    theme(panel.border = element_rect(color = 'black', fill = NA),
          plot.background = element_rect(, fill = 'white'),
          panel.background = element_rect(, fill = 'white'),
          panel.grid = element_blank())

  print(fig)
  ggsave("Received_Campaigns.png", plot = fig, path = sim_dir,
         width = 5, height = 5, device = "png")
}


#### Runs plots

user = Sys.getenv('USERNAME')  # user initials
expt_name = paste0(user, '_FE_2022_example_w4')
working_dir = file.path('simulation_outputs')
sim_dir = file.path(working_dir, expt_name)


## Select which plots to generate
##  Malaria Burden over time (InsetChart)
plot_All_Age_Cases(sim_dir)

##  Malaria Burden over time (MalariaSummaryReport)
plot_PfPR_ClinicalIncidence(sim_dir, Uage = 'U5')

##  Malaria Burden over age (MalariaSummaryReport)
plot_Agebin_PfPR_ClinicalIncidence(sim_dir)

## Event campaign and transmission plots
#plot_TransmissionReport(sim_dir)
#plot_ReceivedCampaigns(sim_dir)

