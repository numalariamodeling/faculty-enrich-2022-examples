import os
from dtk.utils.core.DTKConfigBuilder import DTKConfigBuilder
from dtk.vector.species import set_species, set_larval_habitat
from simtools.ExperimentManager.ExperimentManagerFactory import ExperimentManagerFactory
from simtools.SetupParser import SetupParser
from simtools.ExperimentManager.ExperimentManagerFactory import ExperimentManagerFactory
from simtools.ModBuilder import ModBuilder, ModFn

# This block will be used unless overridden on the command-line
SetupParser.default_block = 'HPC'
serialize_years = 20
numseeds = 5

cb = DTKConfigBuilder.from_defaults('MALARIA_SIM', Simulation_Duration= serialize_years * 365)

cb.update_params({
    'Demographics_Filenames': [os.path.join('Namawala', 'Namawala_single_node_demographics_wIP.json')],
    "Air_Temperature_Filename": os.path.join('Namawala', 'Namawala_single_node_air_temperature_daily.bin'),
    "Land_Temperature_Filename": os.path.join('Namawala', 'Namawala_single_node_land_temperature_daily.bin'),
    "Rainfall_Filename": os.path.join('Namawala', 'Namawala_single_node_rainfall_daily.bin'),
    "Relative_Humidity_Filename": os.path.join('Namawala', 'Namawala_single_node_relative_humidity_daily.bin')
})

cb.update_params({
    'Serialization_Time_Steps': [365 * serialize_years],
    'Serialization_Type': 'TIMESTEP',
    'Serialized_Population_Writing_Type': 'TIMESTEP',
    'Serialized_Population_Reading_Type': 'NONE',
    'Serialization_Mask_Node_Write': 0,
    'Serialization_Precision': 'REDUCED',
    'Disable_IP_Whitelist': 1
})

set_species(cb, ["arabiensis", "funestus", "gambiae"])
set_larval_habitat(cb, {"arabiensis": {'TEMPORARY_RAINFALL': 7.5e9, 'CONSTANT': 1e7},
                        "funestus": {'WATER_VEGETATION': 4e8},
                        "gambiae": {'TEMPORARY_RAINFALL': 8.3e8, 'CONSTANT': 1e7}
                        })

# run_sim_args is what the `dtk run` command will look for
builder = ModBuilder.from_list([[ModFn(DTKConfigBuilder.set_param, 'Run_Number', seed)]
                                for seed in range(numseeds)
                                ])

user = os.getlogin()  # user initials
run_sim_args = {
    'exp_name': f'{user}_FE_2022_example_w8a',
    'config_builder': cb,
    'exp_builder': builder
}

# If you prefer running with `python example_sim.py`, you will need the following block
if __name__ == "__main__":
    SetupParser.init()
    exp_manager = ExperimentManagerFactory.init()
    exp_manager.run_simulations(**run_sim_args)
    # Wait for the simulations to be done
    exp_manager.wait_for_finished(verbose=True)
    assert (exp_manager.succeeded())
