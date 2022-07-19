import os
import pandas as pd
import json
from dtk.tools.demographics.DemographicsGeneratorConcern import WorldBankBirthRateConcern, \
    EquilibriumAgeDistributionConcern, DefaultIndividualAttributesConcern
from dtk.tools.demographics.DemographicsGenerator import DemographicsGenerator
from dtk.tools.climate.ClimateGenerator import ClimateGenerator
from add_properties_to_demographics import generate_demographics_properties


def generate_demographics(demo_df, demo_fname):
    # Get WorldBank birth rate estimate
    # UPDATE country and birthrate_year if needed
    br_concern = WorldBankBirthRateConcern(country="Ghana", birthrate_year=2016)

    chain = [
        DefaultIndividualAttributesConcern(),
        br_concern,
        EquilibriumAgeDistributionConcern(default_birth_rate=br_concern.default_birth_rate),
    ]

    current = DemographicsGenerator.from_dataframe(demo_df,
                                                   population_column_name='population',
                                                   nodeid_column_name='nodeid',
                                                   node_id_from_lat_long=False,
                                                   concerns=chain,
                                                   load_other_columns_as_attributes=True,
                                                   include_columns=['Village'])  # Add any "optional" columns

    with open(demo_fname, 'w') as fout:
        json.dump(current, fout, sort_keys=True, indent=4, separators=(',', ': '))


def generate_climate(demo_fname):
    from simtools.SetupParser import SetupParser

    if not SetupParser.initialized:
        SetupParser.init('HPC')

    cg = ClimateGenerator(demographics_file_path=demo_fname, work_order_path='./wo.json',
                          climate_files_output_path=inputs_path,
                          climate_project='IDM-Ghana',
                          start_year='2001', num_years='16')
    cg.generate_climate_files()


def add_IPs(demo_fname):
    """Add VaccineStatus IP"""
    IPs = [{'Property': 'Access',
            'Values': ['Low', 'High'],
            'Initial_Distribution': [0.5, 0.5],
            'Transitions': []}
           ]

    adf = pd.DataFrame({'Property': 'Access',
                        'Property_Value': ['Low', 'High'],
                        'Initial_Distribution': [0.5, 0.5]}
                       )
    adf['Property_Type'] = 'IP'
    adf['node'] = 1

    IP_demo_fname = os.path.join(demo_fname.replace('.json', '_wIP.json'))
    generate_demographics_properties(refdemo_fname=demo_fname,
                                     output_filename=IP_demo_fname,
                                     as_overlay=False,
                                     IPs=IPs,
                                     df=adf)


if __name__ == '__main__':
    inputs_path = os.path.join('./', 'input/Namawala')  #Ghana
    if not os.path.exists(inputs_path):
        os.mkdir(inputs_path)

    df = pd.DataFrame(data={'nodeid': [1], 'population': [1400], 'Village': ['Obom'],
                            'lat': [5.760759295941768], 'lon': [-0.4473415119456551]})

    demo_fname = os.path.join(inputs_path,'Namawala_single_node_demographics.json')  # 'Ghana_demographics.json')
    #demo_fname = os.path.join(inputs_path,'Ghana_2.5arcmin_demographics.json')  # 'Ghana_demographics.json')

    # generate_demographics(df, demo_fname)
    # generate_climate(demo_fname)  # no need to generate a 2nd time
    add_IPs(demo_fname)
