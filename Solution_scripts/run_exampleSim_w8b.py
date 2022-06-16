## Import basic python functions
import os
import pandas as pd
## Import dtk and EMOD basics functionalities
from dtk.utils.core.DTKConfigBuilder import DTKConfigBuilder
from dtk.vector.species import set_species, set_larval_habitat
from simtools.ExperimentManager.ExperimentManagerFactory import ExperimentManagerFactory
from simtools.SetupParser import SetupParser
from simtools.ModBuilder import ModBuilder, ModFn
## Import custom reporters
from malaria.reports.MalariaReport import add_summary_report
from malaria.reports.MalariaReport import add_event_counter_report
## Import campaign functions
from dtk.interventions.itn import add_ITN
from malaria.interventions.health_seeking import add_health_seeking
from simtools.Utilities.Experiments import retrieve_experiment

SetupParser.default_block = 'HPC'
burnin_id = "24111752-ecd9-ec11-a9f8-b88303911bc1"  # UPDATE with burn-in experiment id
pull_year = 20  # year of burn-in to pick-up from
pickup_years = 2  # years of pick-up to run
numseeds = 5
sim_start_year = 2000 + pull_year

SetupParser.init()
cb = DTKConfigBuilder.from_defaults('MALARIA_SIM', Simulation_Duration=pickup_years * 365)

expt = retrieve_experiment(burnin_id)  # Identifies the desired burn-in experiment

# Loop through unique "tags" to distinguish between burn-in scenarios (ex. varied historical coverage levels)
ser_df = pd.DataFrame([x.tags for x in expt.simulations])
ser_df["outpath"] = pd.Series([sim.get_path() for sim in expt.simulations])

cb.update_params({
    'Demographics_Filenames': [os.path.join('Namawala', 'Namawala_single_node_demographics_wIP.json')],
    "Air_Temperature_Filename": os.path.join('Namawala', 'Namawala_single_node_air_temperature_daily.bin'),
    "Land_Temperature_Filename": os.path.join('Namawala', 'Namawala_single_node_land_temperature_daily.bin'),
    "Rainfall_Filename": os.path.join('Namawala', 'Namawala_single_node_rainfall_daily.bin'),
    "Relative_Humidity_Filename": os.path.join('Namawala', 'Namawala_single_node_relative_humidity_daily.bin')})

cb.update_params({
    'Serialized_Population_Reading_Type': 'READ',
    'Serialized_Population_Filenames': ['state-%05d.dtk' % (pull_year * 365)],
    'Enable_Random_Generator_From_Serialized_Population': 0,
    'Serialization_Mask_Node_Read': 0,
    'Enable_Default_Reporting': 1,
    'Disable_IP_Whitelist': 1
})

set_species(cb, ["arabiensis", "funestus", "gambiae"])
set_larval_habitat(cb, {"arabiensis": {'TEMPORARY_RAINFALL': 7.5e9, 'CONSTANT': 1e7},
                        "funestus": {'WATER_VEGETATION': 4e8},
                        "gambiae": {'TEMPORARY_RAINFALL': 8.3e8, 'CONSTANT': 1e7}
                        })

# Add intervention
event_list = []


# health seeeking, immediate start
def case_management(cb, cm_cov_U5=0.7, cm_cov_adults=0.5, cm_cov_severe=0.85):
    ## Decide whether access would mainly affect treatment seeking among children or total population
    ## Assume high access group = 0.5 of total population
    if cm_cov_U5 >= 0.5:
        cm_cov_U5_high = 1
        cm_cov_U5_low = (cm_cov_U5 - 0.5) / (1 - 0.5)
    else:
        cm_cov_U5_low = 0
        cm_cov_U5_high = cm_cov_U5 / 0.5

    if cm_cov_adults >= 0.5:
        cm_cov_adults_high = 1
        cm_cov_adults_low = (cm_cov_adults - 0.5) / (1 - 0.5)
    else:
        cm_cov_adults_low = 0
        cm_cov_adults_high = cm_cov_adults / 0.5

    if cm_cov_severe >= 0.5:
        cm_cov_severe_high = 1
        cm_cov_severe_low = (cm_cov_severe - 0.5) / (1 - 0.5)
    else:
        cm_cov_severe_low = 0
        cm_cov_severe_high = cm_cov_severe / 0.5

    add_health_seeking(cb, start_day=0,
                       targets=[{'trigger': 'NewClinicalCase', 'coverage': cm_cov_U5_low,
                                 'agemin': 0, 'agemax': 5, 'seek': 1, 'rate': 0.3},
                                {'trigger': 'NewClinicalCase', 'coverage': cm_cov_adults_low,
                                 'agemin': 5, 'agemax': 100, 'seek': 1, 'rate': 0.3}],
                       drug=['Artemether', 'Lumefantrine'],
                       ind_property_restrictions=[{'Access': 'Low'}])

    add_health_seeking(cb, start_day=0,
                       targets=[{'trigger': 'NewClinicalCase', 'coverage': cm_cov_U5_high,
                                 'agemin': 0, 'agemax': 5, 'seek': 1, 'rate': 0.3},
                                {'trigger': 'NewClinicalCase', 'coverage': cm_cov_adults_high,
                                 'agemin': 5, 'agemax': 100, 'seek': 1, 'rate': 0.3}],
                       drug=['Artemether', 'Lumefantrine'],
                       ind_property_restrictions=[{'Access': 'High'}])

    add_health_seeking(cb, start_day=0,
                       targets=[{'trigger': 'NewSevereCase', 'coverage': cm_cov_severe_low,
                                 'agemin': 0, 'agemax': 100, 'seek': 1, 'rate': 0.5}],
                       drug=['Artemether', 'Lumefantrine'],
                       ind_property_restrictions=[{'Access': 'Low'}])

    add_health_seeking(cb, start_day=0,
                       targets=[{'trigger': 'NewSevereCase', 'coverage': cm_cov_severe_high,
                                 'agemin': 0, 'agemax': 100, 'seek': 1, 'rate': 0.5}],
                       drug=['Artemether', 'Lumefantrine'],
                       ind_property_restrictions=[{'Access': 'High'}])

    return {'cm_cov_U5': cm_cov_U5,
            'cm_cov_adults': cm_cov_adults,
            'cm_cov_severe': cm_cov_severe}


event_list = event_list + ['Received_Treatment']


def itn_intervention(cb, coverage_level):
    ## Assume high access group = 0.5 of total population
    if coverage_level >= 0.5:
        coverage_level_high = 1
        coverage_level_low = (coverage_level - 0.5) / (1 - 0.5)
    else:
        coverage_level_low = 0
        coverage_level_high = coverage_level / 0.5

    add_ITN(cb,
            start=1,  # starts on first day of second year
            coverage_by_ages=[
                {"coverage": coverage_level_low, "min": 0, "max": 10},  # Highest coverage for 0-10 years old
                {"coverage": coverage_level_low * 0.75, "min": 10, "max": 50},
                # 25% lower than for children for 10-50 years old
                {"coverage": coverage_level_low * 0.6, "min": 50, "max": 125}
                # 40% lower than for children for everyone else
            ],
            repetitions=5,  # ITN will be distributed 5 times
            tsteps_btwn_repetitions=365 * 3,  # three years between ITN distributions
            ind_property_restrictions=[{'Access': 'Low'}]
            )

    add_ITN(cb,
            start=1,  # starts on first day of second year
            coverage_by_ages=[
                {"coverage": coverage_level_high, "min": 0, "max": 10},  # Highest coverage for 0-10 years old
                {"coverage": coverage_level_high * 0.75, "min": 10, "max": 50},
                # 25% lower than for children for 10-50 years old
                {"coverage": coverage_level_high * 0.6, "min": 50, "max": 125}
                # 40% lower than for children for everyone else
            ],
            repetitions=5,  # ITN will be distributed 5 times
            tsteps_btwn_repetitions=365 * 3,  # three years between ITN distributions
            ind_property_restrictions=[{'Access': 'High'}]
            )
    return {'itn_coverage': coverage_level}


event_list = event_list + ['Received_ITN']

cb.update_params({
    "Report_Event_Recorder": 1,
    "Report_Event_Recorder_Individual_Properties": ['Access'],
    "Report_Event_Recorder_Ignore_Events_In_List": 0,
    "Report_Event_Recorder_Events": event_list,
    'Custom_Individual_Events': event_list
})

# Report_Event_Counter
add_event_counter_report(cb, event_trigger_list=event_list, duration=pickup_years * 365)

for i in range(pickup_years):
    add_summary_report(cb, start=1 + 365 * i, interval=30,
                       duration_days=365,
                       age_bins=[0.25, 5, 120],
                       description=f'Monthly_U5_{sim_start_year + i}')
    add_summary_report(cb, start=1 + 365 * i, interval=30,
                       duration_days=365,
                       age_bins=[0.25, 5, 120],
                       description=f'Monthly_U5_accesslow_{sim_start_year + i}',
                       ipfilter='Access:Low')
    add_summary_report(cb, start=1 + 365 * i, interval=30,
                       duration_days=365,
                       age_bins=[0.25, 5, 120],
                       description=f'Monthly_U5_accesshigh_{sim_start_year + i}',
                       ipfilter='Access:High')

# run_sim_args is what the `dtk run` command will look for
builder = ModBuilder.from_list([[ModFn(case_management, cm_cov_U5),
                                 ModFn(itn_intervention, itn_cov),
                                 ModFn(DTKConfigBuilder.set_param, 'Serialized_Population_Path',
                                       os.path.join(ser_df[ser_df.Run_Number == seed].outpath.iloc[0], 'output')),
                                 ModFn(DTKConfigBuilder.set_param, 'Run_Number', seed)]
                                # Run pick-up from each unique burn-in scenario
                                for cm_cov_U5 in [0.6]
                                for itn_cov in [0.7]
                                for seed in range(numseeds)
                                ])

user = os.getlogin()  # user initials
run_sim_args = {
    'exp_name': f'{user}_FE_2022_example_w8b',
    'config_builder': cb,
    'exp_builder': builder
}

# If you prefer running with `python example_sim.py`, you will need the following block
if __name__ == "__main__":
    exp_manager = ExperimentManagerFactory.init()
    exp_manager.run_simulations(**run_sim_args)
    # Wait for the simulations to be done
    exp_manager.wait_for_finished(verbose=True)
    assert (exp_manager.succeeded())
