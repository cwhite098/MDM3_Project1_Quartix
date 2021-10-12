# -*- coding: utf-8 -*-
"""
Created on Tue Oct 12 10:45:49 2021

@author: kiera
"""

import pandas as pd
import matplotlib.pyplot as plt

df_categorised = pd.read_json('data/categorised.json')
df_uncategorised = pd.read_json('data/uncategorised.json')




gps_df = df_categorised['journey']
print(gps_df[1][0])
print(len(gps_df))
print(gps_df[0][0].get("gridx"))
coordinates=[]

for i in range(len(gps_df)):
    
    x=gps_df[i][0].get("gridx")
    y=gps_df[i][0].get("gridy")
    coordinates.append((x,y))
    
print(coordinates)
    
