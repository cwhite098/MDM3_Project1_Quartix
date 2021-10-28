# -*- coding: utf-8 -*-
"""
Created on Tue Oct 26 11:04:46 2021

@author: kiera
"""
import numpy as np
import pandas as pd
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from extract_data import *
from sklearn.metrics import confusion_matrix

def check_keyword(data2, keyword="Ignition-Off"):
    # Returns the number of ignition-off events for an incident
    r = 0
    data2 = data2["event"].values

    for i in range(len(data2)):
        if data2[i] == keyword:
            r += 1

    return r #returns 0 if no keyword found


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


def get_max_acc(incidentnum, data1):
    current=0

    x = data1["tiltx"].values
    y = data1["tilty"].values
    z = data1["tiltz"].values

    for i in range(8):
        if(x**2+y**2+z**2>current):
            current = x**2+y**2+z**2

    return current



cat_data = load_list('pickle_data', 'cat_data')

ignition_event_list = []
for incident in cat_data:
    r = check_keyword(incident[2], keyword='Ignition-Off')

    ignition_event_list.append(r)

print(ignition_event_list)
y_pred = np.nonzero(ignition_event_list)

y = get_labels(cat_data)
print(y)

print(confusion_matrix(y, ignition_event_list))


    
    
    
    
