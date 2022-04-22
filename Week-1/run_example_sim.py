import os
from dtk.utils.core.DTKConfigBuilder import DTKConfigBuilder
from simtools.SetupParser import SetupParser
from simtools.ExperimentManager.ExperimentManagerFactory import ExperimentManagerFactory
from simtools.ModBuilder import ModBuilder, ModFn
from dtk.interventions.input_EIR import add_InputEIR, monthly_to_daily_EIR
from malaria.interventions.health_seeking import add_health_seeking
from malaria.reports.MalariaReport import add_summary_report

if os.name == "posix":
    SetupParser.default_block = 'NUCLUSTER'
else:
    SetupParser.default_block = 'HPC'

cb = DTKConfigBuilder.from_defaults('MALARIA_SIM')

"""Setup experiment"""
user = 'MR'  # user initials
expt_name = f"{user}_FE_2022_example_w1"
numseeds = 10
years = 7

cb = DTKConfigBuilder.from_defaults('MALARIA_SIM')

cb.update_params({'Simulation_Duration': years * 365})

"""Change default for Demographics input"""
cb.update_params({'Demographics_Filenames': ['my_demographics.json'],
                  'Age_Initialization_Distribution_Type': 'DISTRIBUTION_SIMPLE'})

"""Change default for vector and climate parameter when using forced EIR"""
cb.update_params({
    "Vector_Species_Names": [],
    'x_temporary_Larval_Habitat': 0,
    'Climate_Model': 'CLIMATE_CONSTANT'
})

"""Add campaigns"""
monthly_site_EIR = [15.99, 5.41, 2.23, 10.33, 7.44, 11.77, 79.40, 85.80, 118.59, 82.97, 46.62, 33.49]
daily_EIR = monthly_to_daily_EIR(monthly_site_EIR)
EIRscale_factor = 1

add_InputEIR(cb, start_day=0, EIR_type='DAILY', dailyEIRs=daily_EIR, scaling_factor=EIRscale_factor)

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

"""Add custom reports"""
for year in range(years):
    add_summary_report(cb, start=year * 365, interval=30,
                       age_bins=[0.25, 5, 100],
                       description=f'Monthly_{year}')

"""Build experiments"""
builder = ModBuilder.from_list([[ModFn(DTKConfigBuilder.set_param, 'Run_Number', x)
                                 ]
                                for x in range(numseeds)
                                ])

if __name__ == "__main__":
    """Run experiments"""

    run_sim_args = {
        'exp_name': expt_name,
        'config_builder': cb,
        'exp_builder': builder
    }

    SetupParser.init()
    exp_manager = ExperimentManagerFactory.init()
    exp_manager.run_simulations(**run_sim_args)
