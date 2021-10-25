# -*- coding: utf-8 -*-
"""
Created on Thu Oct 21 20:07:21 2021

@author: kiera
"""


import numpy as np
import pandas as pd

from tsfresh import extract_features

def get_data(json_filename, incident_number):#chris's function mk2

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

df_categorised = pd.read_json('data/categorised.json')
all_data = []



count = int(len(df_categorised)/16)#number incidents beiug viewed



for i in range(count):
    data = get_data('data/categorised.json', i)[2]
    all_data.append(data)
"""for i in range(len(all_data)):
    # Changes labels to binary system
    if 'Correct' in all_data[i][3]:
        all_data[i][3] = 1
    else:
        all_data[i][3] = 0
"""
#print(all_data)
print("end")
"""
print(type(all_data))
print(type(all_data[0]["tiltx"].loc))
print(type(all_data[0]["tiltx"]))
"""
#.loc is evil 
#print(all_data[0].loc)
print(all_data[0]["tiltx"].to_numpy()[1])
#print(type(all_data[0]["tiltx"].tolist()))
print("end")
"""
tiltx={"tiltx":[]}
tilty={"tilty":[]}
tiltz={"tiltz":[]}
timeoffset={"timeoffset":[]}
"""
tiltx=[]
tilty=[]
tiltz=[]
timeoffset=[]

for i in range(count):   
   for j in range(8):
       print(all_data[i]["tiltx"].to_numpy()[j])
       print("appendy")
       """
       tiltx["tiltx"].append(all_data[i]["tiltx"].to_numpy()[j])
       tilty["tilty"].append(all_data[i]["tilty"].to_numpy()[j])
       tiltz["tiltz"].append(all_data[i]["tiltz"].to_numpy()[j])
       timeoffset["timeoffset"].append(all_data[i]["timeoffset"][j])
       """
       tiltx.append(all_data[i]["tiltx"].to_numpy()[j])
       tilty.append(all_data[i]["tilty"].to_numpy()[j])
       tiltz.append(all_data[i]["tiltz"].to_numpy()[j])
       timeoffset.append(all_data[i]["timeoffset"][j])
print(tiltx)
print(len(tiltx))#should be 8*count 8 datamums per incident 
df=pd.DataFrame()
arr=[]
c=-1
for i in range(count):
    c+=1
    
    
    for i in range(8):#8data points per incident
        arr.append(c)
        
        
"""        
print(arr)
print(len(arr))
print(tiltx)
print(len(tiltx))
"""

df= df.append(arr, ignore_index=True)
df = df.append(tiltx, ignore_index=True)
df = df.append(tilty, ignore_index=True)
df = df.append(tiltz, ignore_index=True)
"""
df2=pd.DataFrame()
df2 = df.append(timeoffset)
df2 = df.reset_index()
df = df.reset_index()
df =pd.concat([df,df2], axis=1)  
"""
"""
df["id"]= arr
df["tiltx"] = df.append(all_data["tiltx"], ignore_index=True)
df["tilty"] = all_data[:]["tilty"]
df["tiltz"] = all_data[0:len(all_data)]["tiltz"]
df["timeoffset"] = all_data[:]["timeoffset"]
"""

features = extract_features(all_data,column_id="id", column_sort="time", column_kind="kind", column_value="value")