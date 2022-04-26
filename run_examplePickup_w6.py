import os
from dtk.utils.core.DTKConfigBuilder import DTKConfigBuilder
from dtk.vector.species import set_species, set_larval_habitat
from simtools.ExperimentManager.ExperimentManagerFactory import ExperimentManagerFactory
from simtools.SetupParser import SetupParser
from simtools.Utilities.Experiments import retrieve_experiment
from simtools.ModBuilder import ModBuilder, ModFn
# This block will be used unless overridden on the command-line
SetupParser.default_block = 'HPC'
burnin_id = <ExperimentID> # UPDATE with burn-in experiment
pull_year = 50 # year of burn-in to pick-up from

if __name__ == "__main__":
    SetupParser.init()
    cb = DTKConfigBuilder.from_defaults('MALARIA_SIM')
    expt = retrieve_experiment(burnin_id) # Identifies the desired burn-in experiment
    # Loop through unique "tags" to distinguish between burn-in scenarios (ex. varied historical coverage levels)
    ser_df = pd.DataFrame([x.tags for x in expt.simulations])
    ser_df["outpath"] = pd.Series([sim.get_path() for sim in expt.simulations])

    cb.update_params({
      'Demographics_Filenames': [os.path.join('Namawala', 'Namawala_single_node_demographics.json')],
      "Air_Temperature_Filename": os.path.join('Namawala', 'Namawala_single_node_air_temperature_daily.bin'),
      "Land_Temperature_Filename": os.path.join('Namawala', 'Namawala_single_node_land_temperature_daily.bin'),
      "Rainfall_Filename": os.path.join('Namawala', 'Namawala_single_node_rainfall_daily.bin'),
      "Relative_Humidity_Filename": os.path.join('Namawala', 'Namawala_single_node_relative_humidity_daily.bin')
      'Serialized_Population_Reading_Type': 'READ',
      'Serialized_Population_Filenames': ['state-%05d.dtk' % (pull_year*365)], # Pull last day of <pull_year> to be used as a starting point.
      'Enable_Random_Generator_From_Serialized_Population': 0,
      'Serialization_Mask_Node_Read': 0,
      'Enable_Default_Reporting' : 0
    })

    set_species(cb, ["arabiensis", "funestus", "gambiae"])
    set_larval_habitat(cb, {"arabiensis": {'TEMPORARY_RAINFALL': 7.5e9, 'CONSTANT': 1e7},
                        "funestus": {'WATER_VEGETATION': 4e8},
                        "gambiae": {'TEMPORARY_RAINFALL': 8.3e8, 'CONSTANT': 1e7}
                        })

    builder = ModBuilder.from_list([[ModFn(DTKConfigBuilder.set_param,'Serialized_Population_Path',os.path.join(row['outpath'], 'output'))],
                                # Run pick-up from each unique burn-in scenario
                                for r,row in ser_df.iterrows()
                              ])

    # run_sim_args is what the `dtk run` command will look for
    user = os.getlogin()  # user initials
    run_sim_args = {
           'exp_name': f'{user}_FE_2022_examplePickup_w6',
            'config_builder': cb,
           'exp_builder': builder
        }
    exp_manager = ExperimentManagerFactory.init()
    exp_manager.run_simulations(**run_sim_args)

