import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm
import pickle
import os

def get_datum(json_filename, incident_number):

    df_categorised = pd.read_json(json_filename)

    # Get status of incident
    status = df_categorised['status']
    status = status[incident_number]

    # Get detailed info
    accel_df = df_categorised['detail']
    detail_dict = accel_df[incident_number]

    # Less detailed data
    gps_df = df_categorised['journey']
    journey_dict = gps_df[incident_number]

    # Zoomed out data, has long term speed and accelerometer data
    zoomed_out_df = pd.DataFrame.from_dict(journey_dict)

    # Zoomed in data, use to get the speed in smaller interval
    zoomed_in_df = pd.DataFrame.from_dict(detail_dict)

    # Extract the higher resolution accelerometer data for the crash
    forces = zoomed_in_df['forces']
    zoomed_in_tilts = []
    for second in forces:
        force_1 = pd.DataFrame.from_dict(second)
        zoomed_in_tilts.append(force_1)

    zoomed_in_tilts = pd.concat(zoomed_in_tilts)
    zoomed_in_tilts = zoomed_in_tilts.rename(columns={'index':'timeoffset'})

    linspace_1 = np.linspace(-6, 2.875, 72)
    zoomed_in_tilts['timeoffset'] = linspace_1

    # Changed zoomed_in_df to include t=0 and the other variables
    if str(json_filename) == 'data/uncategorised.json' or json_filename == 'data/categorised.json':
        zoomed_in_df = zoomed_out_df[zoomed_out_df['event'] == 'CDistance']
        alert_row = zoomed_out_df[zoomed_out_df['event'] == 'Alert']
        zoomed_in_df = zoomed_in_df.append(alert_row)
        zoomed_in_df = zoomed_in_df.sort_index()
    elif str(json_filename) == 'data/unlinked.json':
        zoomed_in_df = []

    return [zoomed_in_df, zoomed_out_df, zoomed_in_tilts, status]


def get_data(json_filename):
    df = pd.read_json(json_filename)
    all_data = []
    for i in tqdm(range(len(df))):
        data = get_datum(json_filename, i)
        all_data.append(data)

    return all_data


###########################################################
### PICKLE FUNCTIONS                                    ###
### Used to save and load python data structs to file   ###
###########################################################
def save_list(list_to_save, folder_name, file_name):
    if not os.path.isdir(folder_name):
        os.mkdir(folder_name)
        print('Making Directory:' + str(folder_name))
    with open(folder_name + '/' + file_name, 'wb') as fp:
        pickle.dump(list_to_save, fp)

def load_list(folder_name, file_name):
    with open(folder_name + '/' + file_name, 'rb') as fp:
        return pickle.load(fp)
###########################################################