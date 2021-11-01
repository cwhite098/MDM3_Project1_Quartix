# -*- coding: utf-8 -*-
"""
Created on Mon Nov  1 12:20:21 2021

@author: kiera
"""
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm
import pickle
import os
from tsfresh import extract_features

json_filename='data/uncategorised.json'
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

#incident=get_datum(json_filename, 1)
#print(incident)
def keyword_time_checker(incident,keyword="Ignition-Off"):
    
    data = incident[2]
    ignition_time_off = 0

    event_series = data['event']
    time_offset = data['timeoffset']
    length_events = len(event_series)

    for event in range(length_events):
        if event_series[event] == keyword and time_offset[event] > 0:
            ignition_time_off = time_offset[event]
            break 
   #print("ignition time off"+str(ignition_time_off))    
    
   
    return ignition_time_off

def displacement_till_stop(incident):#returns distance from incident to ignition off
    data=incident[2]
    
    
    time=keyword_time_checker(incident)
    print(time)
    #print(time)
    
    #print(data.head)
    ids = data.index[data['timeoffset'] == time].tolist()[0]
    gridx=0
    gridy=0
    #gridz=0
    gridx=data.loc[data.index[ids], 'gridx']
    gridy=data.loc[data.index[ids], 'gridy']
    #gridz=incident.loc[incident.index[ids], 'gridz']
    #coordinates of stop
    #displacement_till_stop(incident)
    mag = gridx**2+gridy**2#+gridz**2
    mag=mag**(1/2)
    return mag
    
    
#print(get_datum(json_filename, 1))
#print(get_datum(json_filename, 1)[2])
#displacement_till_stop(get_datum(json_filename, 1)))

for i in range(20):
    datum=get_datum(json_filename, i)
    #print(keyword_time_checker(datum))
    #time =keyword_time_checker(datum)
    #print(time)
    print((displacement_till_stop(datum),keyword_time_checker(datum)))
    #print(datum)
    #print(datum==displacement_till_stop(datum))
    #print(str(keyword_time_checker(datum))+"     "+str(i))