import os
import json

user = os.getlogin()  # user initials
expt_name = f'{user}_FE_2022_example_w3a'  ## change expt_name
expt_id = '2022_04_29_04_26_46_512944'  ## change expt_id

exp_path = os.path.join('./', 'experiments', f'{expt_name}___{expt_id}')
os.path.exists(exp_path)

fname = 'ReportEventCounter.json'  # select json file name

## Load json file
sim_name = os.listdir(os.path.join(exp_path))[0]
with open(os.path.join(exp_path, sim_name, 'output', fname), 'r') as f:
    data = json.load(f)


## -> See the first level dictionary keys
print(data.keys())

## -> See the next level dictionary keys, type of channels in this example
print(data['Channels'].keys())
selected_channel = list(data['Channels'].keys())[0]
print(selected_channel)

## -> See the next level dictionary keys, name of keys per channel
print(data['Channels'][selected_channel].keys())

## -> Inspect data from channel
dlen = len(data['Channels'][selected_channel]['Data'])
print(f'Number of data values: {dlen}')

# Select data from channel
data['Channels'][selected_channel]['Data'][:10]  # show only first 10 values

data['Channels'][selected_channel]['Data'][-10:] # show only last 10 values


