# -*- coding: utf-8 -*-
"""
Created on Tue Oct 26 11:04:46 2021

@author: kiera
"""

import numpy as np
import pandas as pd
from tsfresh import extract_features

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
#print(get_data('data/categorised.json',incidentnum)[0]["speed"])
#data = get_data('data/categorised.json',incidentnum)[0]
#print(data.head)

def check_keyword(incidentnum,data0,keyword="Ignition-Off"):
    r=0
    data0=data0["event"].values
    c=0
    for i in data0:
        c+=1
        if data0==keyword and c>7:
            return 2 #key word after t=0
        elif data0==keyword:#if key word found but not after 0
            r=1
    return r#returns 0 if no keyword found



def get_max_vel_chng(incidentnum,data0):
    current=0
    data0 =data0["speed"].values
    #print(data0[-1])
    #print(data0)
    #print(type(data0))
    
    for i in range(8):
        #print(i)
        if(i<7):
            #print(i)
            print(abs(data0[i]-data0[i+1]))
            if abs(data0[i]-data0[i+1])>current:
               # print(abs(data0[i]-data0[i+1]))
                current = abs(data0[i]-data0[i+1])
    return current    

data = get_data('data/categorised.json',incidentnum)[2]
print(data.head)

def get_max_acc(incidentnum,data2):
    current=0
    x = data2["tiltx"].values
    y = data2["tilty"].values
    z = data2["tiltz"].values
    for i in range(8):
        if(x**2+y**2+z**2>current):
            current = x**2+y**2+z**2
    return current


    
    
    
    