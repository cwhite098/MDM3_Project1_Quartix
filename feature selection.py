# -*- coding: utf-8 -*-
"""
Created on Tue Oct 26 11:04:46 2021

@author: kiera
"""

import numpy as np
import pandas as pd
from tsfresh import extract_features

def get_data(json_filename, incident_number):#chris's function

    df_categorised = pd.read_json(json_filename)
    df_uncategorised = pd.read_json('data/uncategorised.json')

    # Get status of incident
    status = df_categorised['status']
    status = status[:]

    # Get detailed info
    accel_df = df_categorised['detail']
    detail_dict = accel_df[:]

    # Less detailed data
    gps_df = df_categorised['journey']
    journey_dict = gps_df[:]

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
    zoomed_in_df = zoomed_out_df[zoomed_out_df['event'] == 'CDistance']
    alert_row = zoomed_out_df[zoomed_out_df['event'] == 'Alert']
    zoomed_in_df = zoomed_in_df.append(alert_row)
    zoomed_in_df = zoomed_in_df.sort_index()
    

    return [zoomed_in_df, zoomed_out_df, zoomed_in_tilts, status]
incidentnum =0
print(get_data('data/categorised.json',incidentnum)[0])

#def get_max_vel_chng(incidentnum,data0):
    
    
    
    
    