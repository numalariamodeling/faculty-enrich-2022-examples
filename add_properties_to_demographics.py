import json
import pandas as pd
import numpy as np


## Script from https://github.com/InstituteforDiseaseModeling/malaria-toolbox/blob/master/input_file_generation/add_properties_to_demographics.py

def check_df_valid(df, IPs, NPs) :

    # also check that values are listed in NPs and IPs?
    def check_prop_specified(sdf, prop_list, prop_type):
        p_list = [x['Property'] for x in prop_list]
        valid = all(x in p_list for x in sdf[sdf['Property_Type'] == prop_type]['Property'].unique())
        if not valid:
            print('invalid %s' % prop_type)
            return False
        return True

    def check_prop_vals_specified(sdf, prop_list, prop_type):
        for p, gdf in sdf[sdf['Property_Type'] == prop_type].groupby('Property'):
            df_vals = gdf['Property_Value'].unique()
            for item in prop_list:
                if item['Property'] == p and not all(x in item['Values'] for x in df_vals):
                    print('invalid value for %s %s' % (prop_type, p))
                    return False
        return True

    # check all NPs specified in defaults
    if not check_prop_specified(df, NPs, 'NP') :
        return False
    # check all NP values specified in defaults
    if not check_prop_vals_specified(df, NPs, 'NP') :
        return False

    # check all IPs specified in defaults
    if not check_prop_specified(df, IPs, 'IP') :
        return False
    # check all IP values specified in defaults
    if not check_prop_vals_specified(df, IPs, 'IP') :
        return False

    # check all IP initial distributions sum to 1
    for (nodeid, prop), gdf in df[df['Property_Type'] == 'IP'].groupby(['node', 'Property']):
        if np.sum(gdf['Initial_Distribution']) != 1 :
            print('Node %d, IP %s initial distribution invalid' % (nodeid, prop))
            return False
    return True


def generate_demographics_properties(refdemo_fname, output_filename='',
                                     as_overlay=False, IPs=[], NPs=[], df=pd.DataFrame()) :
    if not output_filename :
        output_filename = refdemo_fname

    with open(refdemo_fname) as fin:
        demo = json.loads(fin.read())
    all_nodeids = [x['NodeID'] for x in demo['Nodes']]

    if not as_overlay:
        if 'IndividualProperties' in demo['Defaults'] :
            demo['Defaults']['IndividualProperties'] += IPs
        else :
            demo['Defaults']['IndividualProperties'] = IPs
    else:
        demo = { 'Metadata' : demo['Metadata']
                 }
        if IPs:
            demo['Defaults'] = {'IndividualProperties': IPs}
    if NPs:
        if 'NodeProperties' in demo :
            demo['NodeProperties'] += NPs
        else :
            demo['NodeProperties'] = NPs

    if as_overlay:
        nodeIDs_existing = []
        demo['Nodes'] = []
    elif not df.empty:
        nodeIDs_existing = df['node'].unique()

    if not df.empty and 'NP' in df['Property_Type'].unique() :
        for NP in df[df['Property_Type'] == 'NP']['Property'].unique():
            for i, row in df[df['Property'] == NP].iterrows():
                this_np = '%s:%s' % (row['Property'], row['Property_Value'])
                if row['node'] not in nodeIDs_existing:
                    demo['Nodes'].append({'NodeID': row['node'],
                                          'NodeAttributes': {
                                              'NodePropertyValues': [this_np]
                                          }})
                    nodeIDs_existing.append(row['node'])
                else:
                    for node in demo['Nodes']:
                        if node['NodeID'] == row['node']:
                            if 'NodePropertyValues' not in node['NodeAttributes']:
                                node['NodeAttributes']['NodePropertyValues'] = [this_np]
                            else:
                                node['NodeAttributes']['NodePropertyValues'].append(this_np)

    if not df.empty and 'IP' in df['Property_Type'].unique() :
        for (nodeid, prop), gdf in df[df['Property_Type'] == 'IP'].groupby(['node', 'Property']):
            this_ip = {'Property': prop,
                       'Values': list(gdf['Property_Value'].values),
                       'Initial_Distribution': list([float(x) for x in gdf['Initial_Distribution'].values])}
            if nodeid not in nodeIDs_existing:
                demo['Nodes'].append({'NodeID': int(nodeid),
                                      'IndividualProperties': [this_ip]
                                      })
                nodeIDs_existing.append(nodeid)
            else:
                for node in demo['Nodes']:
                    if node['NodeID'] == nodeid:
                        if 'IndividualProperties' not in node:
                            node['IndividualProperties'] = [this_ip]
                        else:
                            node['IndividualProperties'].append(this_ip)

    if as_overlay and not df.empty :
        missing_nodeids = [x for x in all_nodeids if x not in nodeIDs_existing]
        for node in missing_nodeids :
            demo['Nodes'].append({ 'NodeID' : node})

    def default(o):
        if isinstance(o, np.int64): return int(o)
        raise TypeError

    with open(output_filename, 'w') as fout:
        json.dump(demo, fout, sort_keys=True, indent=4, separators=(',', ': '), default=default)

