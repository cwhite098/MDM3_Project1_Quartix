# -*- coding: utf-8 -*-
"""
Created on Mon Nov  1 16:39:58 2021

@author: kiera
"""

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

    return ignition_time_off