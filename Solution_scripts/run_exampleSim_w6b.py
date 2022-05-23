import os

import pandas as pd
from dtk.interventions.itn import add_ITN
from dtk.utils.core.DTKConfigBuilder import DTKConfigBuilder
from dtk.vector.species import set_species, set_larval_habitat
from malaria.reports.MalariaReport import add_event_counter_report, add_summary_report
from simtools.ExperimentManager.ExperimentManagerFactory import ExperimentManagerFactory
from simtools.ModBuilder import ModBuilder, ModFn
from simtools.SetupParser import SetupParser

# This block will be used unless overridden on the command-line
from simtools.Utilities.Experiments import retrieve_experiment

SetupParser.default_block = 'HPC'
burnin_id = "b4f6741c-07da-ec11-a9f8-b88303911bc1"  # UPDATE with burn-in experiment id
pull_year = 50  # year of burn-in to pick-up from
pickup_years = 2  # years of pick-up to run
numseeds = 1
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
    "Relative_Humidity_Filename": os.path.join('Namawala', 'Namawala_single_node_relative_humidity_daily.bin')
})

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

for i in range(pickup_years):
    add_summary_report(cb, start=1 + 365 * i, interval=30,
                       duration_days=365,
                       age_bins=[0.25, 5, 120],
                       description=f'Monthly_U5_{i}')

# run_sim_args is what the `dtk run` command will look for
builder = ModBuilder.from_list([[
    ModFn(DTKConfigBuilder.set_param, 'Serialized_Population_Path',
          os.path.join(ser_df[ser_df.Run_Number == seed].outpath.iloc[0], 'output')),
    ModFn(DTKConfigBuilder.set_param, 'Run_Number', seed)]
    # Run pick-up from each unique burn-in scenario
    for seed in range(numseeds)
])

user = os.getlogin()  # user initials
run_sim_args = {
    'exp_name': f'{user}_FE_2022_example_w6b',
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
