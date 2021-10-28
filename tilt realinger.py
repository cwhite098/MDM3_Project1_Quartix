# -*- coding: utf-8 -*-
"""
Created on Tue Oct 26 12:16:50 2021

@author: kiera
"""
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


def get_data(json_filename, incident_number):

    df_categorised = pd.read_json(json_filename)
    df_uncategorised = pd.read_json('data/uncategorised.json')

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
    zoomed_in_df = zoomed_out_df[zoomed_out_df['event'] == 'CDistance']
    alert_row = zoomed_out_df[zoomed_out_df['event'] == 'Alert']
    zoomed_in_df = zoomed_in_df.append(alert_row)
    zoomed_in_df = zoomed_in_df.sort_index()
    

    return [zoomed_in_df, zoomed_out_df, zoomed_in_tilts, status]
incidentnum = 0
def re_align_tiltdata(incidentnum):   
    data2 = get_data('data/categorised.json',incidentnum)[2]
    x = data2["tiltx"].values
    y = data2["tilty"].values
    z = data2["tiltz"].values
    print(x)
    print(type(x))
    x=list(np.float_(x))
    y=list(np.float_(y))
    z=list(np.float_(z))
    print(type(x))
    xdif= abs(1-np.mean(x))
    ydif= abs(1-np.mean(y))
    zdif= abs(1-np.mean(z))
    if zdif>xdif or zdif>ydif:
        if ydif<xdif:#ysmallest difference from 1 therefor y = z
            temp=z
            z=y
            y=temp
        else:#xdiff smallest
            temp =z
            z=x
            x=temp
incidentcount= len(get_data('data/categorised.json',incidentnum)[2])
X={}
Y={}
Z={}
#Y=[[][]]
#Z=[[][]]
for i in range(incidentcount):
    data = re_align_tiltdata(incidentnum)
    X.update({str(i):data[0]})
    Y.update({str(i):data[1]})
    Z.update({str(i):data[2]})
print(X)