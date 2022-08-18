## Import basic python functions
import os
## Import dtk and EMOD basics functionalities
from dtk.utils.core.DTKConfigBuilder import DTKConfigBuilder
from dtk.vector.species import set_species, set_larval_habitat
from simtools.ExperimentManager.ExperimentManagerFactory import ExperimentManagerFactory
from simtools.SetupParser import SetupParser
## Import custom reporters
from malaria.reports.MalariaReport import add_summary_report
from nucluster_helper import *

# This block will be used unless overridden on the command-line
if os.name == "posix":
    SetupParser.default_block = 'NUCLUSTER'
else:
    SetupParser.default_block = 'HPC'

years = 3
cb = DTKConfigBuilder.from_defaults('MALARIA_SIM', Simulation_Duration=years * 365)

"""MODIFIED SETTING SPECIFIC FILES"""
cb.update_params({
    'Demographics_Filenames': [os.path.join('Namawala', 'Namawala_single_node_demographics.json')],
    "Air_Temperature_Filename": os.path.join('Namawala', 'Namawala_single_node_air_temperature_daily.bin'),
    "Land_Temperature_Filename": os.path.join('Namawala', 'Namawala_single_node_land_temperature_daily.bin'),
    "Rainfall_Filename": os.path.join('Namawala', 'Namawala_single_node_rainfall_daily.bin'),
    "Relative_Humidity_Filename": os.path.join('Namawala', 'Namawala_single_node_relative_humidity_daily.bin')
})

"""Optional update other parameters (explorative)"""
cb.update_params({
    'x_Base_Population': 1,
    'x_Birth': 1,
    'x_Temporary_Larval_Habitat': 1
})

set_species(cb, ["arabiensis", "funestus", "gambiae"])
set_larval_habitat(cb, {"arabiensis": {'TEMPORARY_RAINFALL': 7.5e9, 'CONSTANT': 1e7},
                        "funestus": {'WATER_VEGETATION': 4e8},
                        "gambiae": {'TEMPORARY_RAINFALL': 8.3e8, 'CONSTANT': 1e7}
                        })

"""CUSTOM REPORTS"""
add_summary_report(cb, start=1, interval=365,
                   age_bins=[0.25, 2, 5, 10, 15, 20, 100, 120],
                   description='Annual_Agebin')

# run_sim_args is what the `dtk run` command will look for
user = os.getlogin()  # user initials
expt_name = f'{user}_FE_2022_example_w2_quest'

run_sim_args = {
    'exp_name': expt_name,
    'config_builder': cb,
}

# If you prefer running with `python example_sim.py`, you will need the following block
if __name__ == "__main__":
    SetupParser.init()
    exp_manager = ExperimentManagerFactory.init()
    exp_manager.run_simulations(**run_sim_args)

    if SetupParser.default_block == 'HPC':
        # Wait for the simulations to be done
        exp_manager.wait_for_finished(verbose=True)
        assert (exp_manager.succeeded())
    else:
        # Create and submit job to run analyzer after simulations finished
        expt_id = exp_manager.experiment.exp_id
        job_id = exp_manager.load_job_id_for_experiment(exp_manager.experiment)
        analyzer_script_name = create_analyzer_submission_script(expt_name=expt_name, expt_id=expt_id)
        submit_dependent_job(job_id=job_id, sh_fname=analyzer_script_name)
