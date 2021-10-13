# -*- coding: utf-8 -*-
"""
Created on Tue Oct 12 10:45:49 2021

@author: kiera
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
df_categorised = pd.read_json('data/categorised.json')
df_uncategorised = pd.read_json('data/uncategorised.json')


def get_data(json_filename, incident_number):#chris's function

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


incidentnum=1


gpsdata= get_data('data/categorised.json',incidentnum)[0]
xcords=pd.DataFrame(gpsdata.get("gridx")).to_numpy()
ycords=pd.DataFrame(gpsdata.get("gridy")).to_numpy()
print(gpsdata)
#print(gpsdata.get("gridx"))


#ycords = gpsdata.get("gridy")
coordinates = []
print(xcords)
print(ycords)
xcords = xcords[:,0]
ycords=ycords[:,0]
print(xcords[0])
print(ycords[0])
for i in range(len(xcords)):
    coordinates.append((xcords[i],ycords[i]))
#xcords= np.reshape(10,1)
#ycords= np.reshape(10,1)
#print(xcords)
#print(ycords)
#coordinates=zip(xcords,ycords)
print(coordinates)
"""
gpsnearcrash=[]
for i in range(len(gps_df[0])):
    print(gps_df[i][0].get("timeoffset"))
    if gps_df[i][0].get("timeoffset")>=-3 and gps_df[i][0].get("timeoffset")<= 6:
        print
        gpsnearcrash.append(i)
"""    

vectors = []
prev=coordinates[0]
for i in coordinates:
    a=(i[0]-prev[0])
    b=(i[1]-prev[1])
    prev=i
    #a=a/np.sqrt(a*a+b*b)
    #b=b/np.sqrt(a*a+b*b)
    vectors.append((a,b))#x,y for vector
    
    
#print(coordinates[0])
print(len(coordinates))
plt.quiver(*zip(*coordinates), *zip(*vectors))
plt.scatter(coordinates[0][0],coordinates[0][1])
plt.scatter(coordinates[len(coordinates)-1][0],coordinates[len(coordinates)-1][1])
plt.show()
