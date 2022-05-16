library(dplyr)
library(tidyr)
library(data.table)
library(lubridate)
library(ggplot2)
library(scales)

theme_set(theme_minimal())
tab10_palette = c('#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf')
theme_py = theme(axis.ticks = element_line(),
                 plot.title = element_text(size = 14, vjust = -1, hjust = 0.5),
                 strip.text = element_text(size = 14),
                 axis.text = element_text(size = 11),
                 panel.border = element_rect(color = 'black', fill = NA),
                 plot.background = element_rect(, fill = 'white'),
                 panel.background = element_rect(, fill = 'white'),
                 panel.grid = element_blank(),
                 panel.spacing = unit(1, "lines"),
                 legend.position = c(0.85, 0.15))

plot_inset_chart <- function(channels_inset_chart, sweep_variables) {
  dat <- fread(file.path(sim_dir, 'All_Age_InsetChart.csv'))

  ## Aggregate runs
  dat <- dat %>%
    group_by_at(.vars = c('date', all_of(sweep_variables))) %>%
    summarize_at(channels_inset_chart, .funs = 'mean')

  fig <- dat %>%
    pivot_longer(cols = -c('date', sweep_variables)) %>%
    mutate(name = factor(name, levels = channels_inset_chart)) %>%
    unite('sweep', sweep_variables, sep = ", ", remove = FALSE, na.rm = FALSE) %>%
    ggplot() +
    geom_hline(yintercept = 0, col = 'white', alpha = 0.1) + # dummy for ymin
    geom_line(aes(x = date, y = value, col = sweep)) +
    facet_wrap(~name, scales = 'free') +
    scale_x_date(date_breaks = '12 month', date_labels = "%Y-%m-%d") +
    scale_y_continuous(labels = comma) +
    scale_color_manual(values = tab10_palette) +
    labs(title = 'InsetChartAnalyzer',
         x = '', y = '',
         color = paste(sweep_variables, collapse = ", ")) +
    theme_py

  ggsave("InsetChart_R.png", plot = fig, path = sim_dir,
         width = 12, height = 6, device = "png")
}


plot_summary_report <- function(sweep_variables, channels_summary_report = NULL, Uage = 'U5') {
  dat <- fread(file.path(sim_dir, paste0(Uage, '_PfPR_ClinicalIncidence.csv'))) %>%
    rename_with(~gsub(paste0(" ", Uage), "", .x)) %>%
    mutate(date = make_date(year, month, '01'))

  if (is.null(channels_summary_report)) {
    channels_summary_report = c('Pop', 'Cases', 'Severe cases', 'PfPR')
  }


  ## Aggregate runs
  dat <- dat %>%
    group_by_at(.vars = c('date', 'year', all_of(sweep_variables))) %>%
    summarize_at(channels_summary_report, .funs = 'mean')

  fig <- dat %>%
    pivot_longer(cols = -c('date', 'year', sweep_variables)) %>%
    mutate(name = factor(name, levels = channels_summary_report)) %>%
    unite('sweep', sweep_variables, sep = ", ", remove = FALSE, na.rm = FALSE) %>%
    ggplot() +
    geom_hline(yintercept = 0, col = 'white', alpha = 0.1) + # dummy for ymin
    geom_line(aes(x = date, y = value, col = sweep)) +
    facet_wrap(~name, scales = 'free') +
    scale_y_continuous(labels = comma) +
    scale_color_manual(values = tab10_palette) +
    labs(title = paste0('MalariaSummaryReport ', Uage),
         x = 'Year', y = '',
         color = paste(sweep_variables, collapse = ", ")) +
    theme_py

  ggsave(paste0("PfPR_ClinicalIncidence_", Uage, "_R.png"), plot = fig, path = sim_dir,
         width = 5, height = 5, device = "png")
}


plot_Agebin_summary_report <- function(sweep_variables, channels_summary_report = NULL) {
  dat <- fread(file.path(sim_dir, 'Agebin_PfPR_ClinicalIncidence_annual.csv'))


  if (is.null(channels_summary_report)) {
    channels_summary_report = c('Pop', 'Cases', 'Severe cases', 'PfPR')
  }

  ## Aggregate runs
  dat <- dat %>%
    group_by_at(.vars = c('agebin', all_of(sweep_variables))) %>%
    summarize_at(channels_summary_report, .funs = 'mean')

  fig <- dat %>%
    pivot_longer(cols = -c('agebin', sweep_variables)) %>%
    mutate(name = factor(name, levels = channels_summary_report)) %>%
    #mutate(agebin = factor(agebin, levels = unique(dat$agebin)))%>%
    unite('sweep', sweep_variables, sep = ", ", remove = FALSE, na.rm = FALSE) %>%
    ggplot() +
    geom_hline(yintercept = 0, col = 'white', alpha = 0.1) + # dummy for ymin
    geom_line(aes(x = agebin, y = value, col = sweep, group = sweep)) +
    facet_wrap(~name, scales = 'free') +
    scale_y_continuous(labels = comma) +
    scale_color_manual(values = tab10_palette) +
    labs(title = paste0('MalariaSummaryReport (agebin)'),
         x = 'Agebin', y = '',
         color = paste(sweep_variables, collapse = ", ")) +
    theme_py

  ggsave("Agebin_PfPR_ClinicalIncidence_R.png", plot = fig, path = sim_dir,
         width = 12, height = 6, device = "png")
}


plot_events <- function(event_list, sweep_variables) {
  dat <- fread(file.path(sim_dir, 'Event_Count.csv'))

  cov_channel_list = paste0(gsub('Received_', '', event_list), '_Coverage')
  cov_channel_list = cov_channel_list[(cov_channel_list %in% colnames(dat))]

  ## Aggregate runs
  dat <- dat %>%
    group_by_at(.vars = c('date', all_of(sweep_variables))) %>%
    summarize_at(c(event_list, cov_channel_list), .funs = 'mean')

  fig <- dat %>%
    pivot_longer(cols = -c('date', sweep_variables)) %>%
    mutate(name = factor(name, levels = as.vector(unlist(Map(c, event_list, cov_channel_list))))) %>%
    unite('sweep', sweep_variables, sep = ", ", remove = FALSE, na.rm = FALSE) %>%
    ggplot() +
    geom_hline(yintercept = 0, col = 'white', alpha = 0.1) + # dummy for ymin
    geom_line(aes(x = date, y = value, col = sweep)) +
    scale_x_date(date_breaks = '12 month', date_labels = "%Y-%m-%d") +
    facet_wrap(~name, scales = 'free', ncol = 2) +
    scale_y_continuous(labels = comma) +
    scale_color_manual(values = tab10_palette) +
    labs(title = 'ReceivedCampaignAnalyzer',
         x = 'date', y = '',
         color = paste(sweep_variables, collapse = ", ")) +
    theme_py

  ggsave("Events_R.png", plot = fig, path = sim_dir,
         width = 12, height = 3 * length(event_list), device = "png")
}

plot_transmission <- function(sweep_variables, time_res = 'Monthly', selected_year = NULL) {

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

  channels = c('Daily Bites per Human', 'Daily EIR', 'Rainfall', 'PfHRP2 Prevalence')
  channels = gsub('Daily', time_res, channels)


  ## Aggregate runs
  dat <- dat %>%
    group_by_at(.vars = all_of(c(x_var, sweep_variables))) %>%
    summarize_at(channels, .funs = 'mean')

  fig <- dat %>%
    pivot_longer(cols = -c(x_var, sweep_variables)) %>%
    mutate(name = factor(name, levels = channels)) %>%
    unite('sweep', sweep_variables, sep = ", ", remove = FALSE, na.rm = FALSE) %>%
    ggplot() +
    geom_hline(yintercept = 0, col = 'white', alpha = 0.1) + # dummy for ymin
    geom_line(aes(x = get(x_var), y = value, col = sweep)) +
    facet_wrap(~name, scales = 'free') +
    scale_y_continuous(labels = comma) +
    scale_color_manual(values = tab10_palette) +
    labs(title = 'TransmissionReport',
         x = x_var, y = '',
         color = paste(sweep_variables, collapse = ", ")) +
    theme_py

  if (x_var == 'date') {
    fig = fig +
      scale_x_date(date_breaks = '4 month', date_labels = "%b\n'%y")
  }

  ggsave(paste0("Transmission_", time_res, "_R.png"), plot = fig, path = sim_dir,
         width = 12, height = 6, device = "png")
}


user = Sys.getenv('USERNAME')  # user initials
expt_name = paste0(user, '_FE_2022_example_w4')
working_dir = file.path('simulation_outputs')
sim_dir = file.path(working_dir, expt_name)

## Set sweep_variables and event_list as required depending on experiment
sweep_variables = c('cm_cov_U5', 'itn_coverage', 'smc_coverage')
event_list = c('Received_Treatment', 'Received_ITN', 'Received_SMC')
channels_inset_chart = c('Statistical Population', 'New Clinical Cases', 'Adult Vectors', 'Infected')


## Generate plots
plot_inset_chart(channels_inset_chart, sweep_variables)
plot_summary_report(sweep_variables, Uage = 'U5')  # (MalariaSummaryReport aggregated age)
plot_Agebin_summary_report(sweep_variables)  # (MalariaSummaryReport agebins)
plot_events(event_list, sweep_variables)
# plot_transmission(sweep_variables)  # optional

