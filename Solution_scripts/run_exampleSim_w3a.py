import os
from dtk.utils.core.DTKConfigBuilder import DTKConfigBuilder
from dtk.vector.species import set_species, set_larval_habitat
from simtools.ExperimentManager.ExperimentManagerFactory import ExperimentManagerFactory
from simtools.SetupParser import SetupParser
from malaria.reports.MalariaReport import add_summary_report
from malaria.interventions.health_seeking import add_health_seeking
from malaria.interventions.malaria_drug_campaigns import add_drug_campaign

# This block will be used unless overridden on the command-line
SetupParser.default_block = 'LOCAL'

cb = DTKConfigBuilder.from_defaults('MALARIA_SIM', Simulation_Duration=365)
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

"""CUSTOM REPORTS"""
add_summary_report(cb, start=1, interval=30,
                   age_bins=[0.25, 5, 100],
                   description='Monthly_U5')

"""ADDITIONAL CAMPAIGNS"""
# health seeeking
add_health_seeking(cb, start_day=0,
                   targets=[{'trigger': 'NewClinicalCase',
                             'coverage': 0.7,
                             'agemin': 0,
                             'agemax': 5,
                             'seek': 1,
                             'rate': 0.3},
                            {'trigger': 'NewClinicalCase',
                             'coverage': 0.5,
                             'agemin': 5,
                             'agemax': 100,
                             'seek': 1,
                             'rate': 0.3},
                            {'trigger': 'NewSevereCase',
                             'coverage': 0.85,
                             'agemin': 0,
                             'agemax': 100,
                             'seek': 1,
                             'rate': 0.5}],
                   drug=['Artemether', 'Lumefantrine'])

# seasonal malaria chemoprevention
add_drug_campaign(cb, campaign_type='SMC', drug_code='SPA',
                  coverage=0.8,
                  start_days=[30],
                  repetitions=4,
                  tsteps_btwn_repetitions=30,
                  target_group={'agemin': 0.25, 'agemax': 5},
                  receiving_drugs_event_name='Received_SMC')

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
