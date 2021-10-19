import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm
import pickle
import os

def get_datum(json_filename, incident_number):

    df_categorised = pd.read_json(json_filename)
    linspace_1 = np.linspace(-6, 2.875, 72)

    # Changed zoomed_in_df to include t=0 and the other variables
    if str(json_filename) == 'data/uncategorised.json' or json_filename == 'data/categorised.json':

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

        zoomed_in_tilts['timeoffset'] = linspace_1

        zoomed_in_df = zoomed_out_df[zoomed_out_df['event'] == 'CDistance']
        alert_row = zoomed_out_df[zoomed_out_df['event'] == 'Alert']
        zoomed_in_df = zoomed_in_df.append(alert_row)
        zoomed_in_df = zoomed_in_df.sort_index()

        return [zoomed_in_df, zoomed_in_tilts, zoomed_out_df, status]

    elif str(json_filename) == 'data/unlinked.json':

        zoomed_in_df = []
        accel_df = df_categorised['detail']
        detail_dict = accel_df[incident_number]
        # Zoomed in data, use to get the speed in smaller interval
        zoomed_in_df = pd.DataFrame.from_dict(detail_dict)

        zoomed_in_df = zoomed_in_df.sort_values(by=['timeoffset'])

        forces = zoomed_in_df['forces']
        zoomed_in_tilts = []
        for second in forces:
            force_1 = pd.DataFrame.from_dict(second)
            zoomed_in_tilts.append(force_1)

        zoomed_in_tilts = pd.concat(zoomed_in_tilts)
        zoomed_in_tilts = zoomed_in_tilts.rename(columns={'index':'timeoffset'})

        zoomed_in_tilts['timeoffset'] = linspace_1

        return [zoomed_in_df, zoomed_in_tilts]


def get_data(json_filename):
    df = pd.read_json(json_filename)
    all_data = []
    for i in tqdm(range(len(df))):
        data = get_datum(json_filename, i)
        all_data.append(data)

    return all_data


def get_timeseries(tilts):
    tilts = np.array(tilts)
    tilts = tilts[:,1:]
    tilt_timeseries = tilts.transpose()
    tilt_timeseries = tilt_timeseries.astype('float')
    tilt_timeseries = np.reshape(tilt_timeseries,(1,72,3))

    return tilt_timeseries


def get_tilt_timeseries(data):
    # Extracts timeseries of tilts for whole dataset (output shape = (no_ts, len_ts, axes))

    X = []
    for i in tqdm(range(len(data))):
        incident = data[i]
        tilts = incident[1]
        tilt_timeseries = get_timeseries(tilts)
        X.append(tilt_timeseries)
    X = np.array(X)
    X = np.reshape(X, (X.shape[0], 72, 3))

    return X

def get_labels(cat_data):
    y_test = []
    for i in range(len(cat_data)):
        incident = cat_data[i]
        if 'Correct' in incident[3]:
            y_test.append(1)
        else:
            y_test.append(0)

    return y_test

def get_mags(X):
    mag_X = np.empty((len(X), 72))
    for i in range(len(X)):
        for k in range(72):
            vector = np.array(X[i,k,:])
            vector = [float(i) for i in vector]
            mag = np.linalg.norm(vector[:])
            #if mag < 0:
            #   mag*-1
            mag_X[i,k] = mag
    return mag_X

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