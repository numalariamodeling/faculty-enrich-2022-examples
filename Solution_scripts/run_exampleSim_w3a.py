## Import basic python functions
import os
## Import dtk and EMOD basics functionalities
from dtk.utils.core.DTKConfigBuilder import DTKConfigBuilder
from dtk.vector.species import set_species, set_larval_habitat
from simtools.ExperimentManager.ExperimentManagerFactory import ExperimentManagerFactory
from simtools.SetupParser import SetupParser
## Import custom reporters
from malaria.reports.MalariaReport import add_summary_report
from malaria.reports.MalariaReport import add_event_counter_report
## Import campaign functions
# from dtk.interventions.itn import add_ITN
from dtk.interventions.itn_age_season import add_ITN_age_season
from dtk.interventions.irs import add_IRS
from malaria.interventions.health_seeking import add_health_seeking
from malaria.interventions.malaria_drug_campaigns import add_drug_campaign
from malaria.interventions.malaria_vaccine import add_vaccine

# This block will be used unless overridden on the command-line
SetupParser.default_block = 'LOCAL'
years = 3
cb = DTKConfigBuilder.from_defaults('MALARIA_SIM', Simulation_Duration=years * 365)

cb.update_params({
    'Demographics_Filenames': [os.path.join('Ghana', 'Ghana_2.5arcmin_demographics.json')],
    "Air_Temperature_Filename": os.path.join('Ghana', 'Ghana_30arcsec_air_temperature_daily.bin'),
    "Land_Temperature_Filename": os.path.join('Ghana', 'Ghana_30arcsec_air_temperature_daily.bin'),
    "Rainfall_Filename": os.path.join('Ghana', 'Ghana_30arcsec_rainfall_daily.bin'),
    "Relative_Humidity_Filename": os.path.join('Ghana', 'Ghana_30arcsec_relative_humidity_daily.bin'),
    "Age_Initialization_Distribution_Type": 'DISTRIBUTION_COMPLEX'
})

set_species(cb, ["arabiensis", "funestus", "gambiae"])
set_larval_habitat(cb, {"arabiensis": {'TEMPORARY_RAINFALL': 7.5e9, 'CONSTANT': 1e7},
                        "funestus": {'WATER_VEGETATION': 4e8},
                        "gambiae": {'TEMPORARY_RAINFALL': 8.3e8, 'CONSTANT': 1e7}
                        })

"""ADDITIONAL CAMPAIGNS"""
event_list = []  ## Collect events to track in reports
# health seeeking, immediate start
add_health_seeking(cb, start_day=0,
                   targets=[{'trigger': 'NewClinicalCase', 'coverage': 0.7,
                             'agemin': 0, 'agemax': 5, 'seek': 1, 'rate': 0.3},
                            {'trigger': 'NewClinicalCase', 'coverage': 0.5,
                             'agemin': 5, 'agemax': 100, 'seek': 1, 'rate': 0.3},
                            {'trigger': 'NewSevereCase', 'coverage': 0.85,
                             'agemin': 0, 'agemax': 100, 'seek': 1, 'rate': 0.5}],
                   drug=['Artemether', 'Lumefantrine'])
event_list = event_list + ['Received_Treatment', 'Received_Severe_Treatment']

# malaria vaccine (RTS,S), no booster start after 1 year
add_vaccine(cb,
            vaccine_type='RTSS',
            vaccine_params={"Waning_Config":
                                {"Initial_Effect": 0.8,
                                 "Decay_Time_Constant": 592.4066512,
                                 "class": 'WaningEffectExponential'}},
            start_days=[366],
            coverage=1,
            repetitions=1,
            tsteps_btwn_repetitions=-1,
            target_group={'agemin': 274, 'agemax': 275})  # children 9 months of age
event_list = event_list + ['Received_Vaccine']

# seasonal malaria chemoprevention, start after 1 year
add_drug_campaign(cb, campaign_type='SMC', drug_code='SPA',
                  coverage=0.8,
                  start_days=[366],
                  repetitions=4,
                  tsteps_btwn_repetitions=30,
                  target_group={'agemin': 0.25, 'agemax': 5},
                  receiving_drugs_event_name='Received_SMC')
event_list = event_list + ['Received_SMC']

# ITN, start after 1 year
# add_ITN(cb, start=0, coverage_by_ages=[{'min': 0, 'max': 100, 'coverage': 0.6}])
add_ITN_age_season(cb, start=366,
                   demographic_coverage=0.8,
                   killing_config={
                       "Initial_Effect": 0.520249973,  # LLIN Burkina
                       "Decay_Time_Constant": 1460,
                       "class": "WaningEffectExponential"},
                   blocking_config={
                       "Initial_Effect": 0.53,
                       "Decay_Time_Constant": 730,
                       "class": "WaningEffectExponential"},
                   discard_times={"Expiration_Period_Distribution": "DUAL_EXPONENTIAL_DISTRIBUTION",
                                  "Expiration_Period_Proportion_1": 0.9,
                                  "Expiration_Period_Mean_1": 365 * 1.7,  # Burkina 1.7
                                  "Expiration_Period_Mean_2": 3650},
                   age_dependence={'Times': [0, 100],
                                   'Values': [0.9, 0.9]},
                   duration=-1, birth_triggered=False
                   )
event_list = event_list + ['Bednet_Got_New_One', 'Bednet_Using', 'Bednet_Discarded']

# IRS, start after 1 year - single campaign
add_IRS(cb, start=366,
        coverage_by_ages=[{"coverage": 0.8, "min": 0, "max": 100}],
        killing_config={
            "class": "WaningEffectBoxExponential",
            "Box_Duration": 180,  # based on PMI data from Burkina
            "Decay_Time_Constant": 90,  # Sumishield from Benin
            "Initial_Effect": 0.7},
        )
event_list = event_list + ['Received_IRS']

"""CUSTOM REPORTS"""
# add_filtered_report(cb, start=0, end=years * 365)
## Summary report per agebin
add_summary_report(cb, start=1, interval=365,
                   age_bins=[0.25, 2, 5, 10, 15, 20, 100, 120],
                   description='Annual_Agebin')

## Enable reporters
cb.update_params({
    "Report_Event_Recorder": 1,
    "Report_Event_Recorder_Individual_Properties": [],
    "Report_Event_Recorder_Ignore_Events_In_List": 0,
    "Report_Event_Recorder_Events": event_list,
    'Custom_Individual_Events': event_list
})

## Event_counter_report
add_event_counter_report(cb, event_trigger_list=event_list, start=0, duration=10000)

# run_sim_args is what the `dtk run` command will look for
user = os.getlogin()  # user initials
run_sim_args = {
    'exp_name': f'{user}_FE_2022_example_w3a',
    'config_builder': cb
}

# If you prefer running with `python example_sim.py`, you will need the following block
if __name__ == "__main__":
    SetupParser.init()
    exp_manager = ExperimentManagerFactory.init()
    exp_manager.run_simulations(**run_sim_args)
    # Wait for the simulations to be done
    exp_manager.wait_for_finished(verbose=True)
    assert (exp_manager.succeeded())