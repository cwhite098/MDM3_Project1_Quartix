from extract_data import *
from sklearn.metrics import confusion_matrix
from numpy.fft import rfft,rfftfreq,fft
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import spectrum

""" vvv KEYWORD FUNCTIONS vvv """

def keyword_freq(incident, keyword): # returns the frequency count of a given keyword

    freq = 0    # frequency of keyword
    data = incident[2]
    data = data["event"].values

    for i in range(len(data)):
        if data[i] == keyword:
            freq += 1

    return freq 

def keyword_time_offset(incident, keyword): # returns the time offset between the alert and a given keyword

    data = incident[2]
    time = 0    # time offset between keyword and alert (can only be positive i.e. keyword must be after alert)

    event_series = data['event']
    time_offset = data['timeoffset']
    length_events = len(event_series)

    for event in range(length_events):
        if event_series[event] == keyword and time_offset[event] > 0:
            time = time_offset[event]
            break 

    return time

""" ^^^ KEYWORD FUNCTIONS ^^^ """

""" vvv DISPLACEMENT, VELOCITY, ACCELERATION FUNCTIONS vvv """

def max_stop_time(incident): # returns the longest time the car is at rest for

    speed = incident[0]["speed"].values
    found = False
    count = 0
    maximum =0
    for i in speed:
        if i == 0:
            found = True
            count+=1
        if i != 0 and found:
            found=False
            
            if count>maximum:
                maximum=count
            count = 0
                
    return maximum

def get_vel_change(incident): # returns the change in velocity between the alert and t = 3
    
    data = incident[0]
    data = data['speed'].values
    d_v = data[6]-data[9]
    
    return d_v

def get_max_vel_chng(incident): # UNFINISHED
    current = 0
    data0 = incident[0]
    data0 =data0["speed"].values

    for i in range(8):
        if(i<7):
            print(abs(data0[i]-data0[i+1]))
            if abs(data0[i]-data0[i+1])>current:
                current = abs(data0[i]-data0[i+1])
    return current 

def displacement_till_stop(incident):#returns distance from incident to first ignition off
    data=incident[2]
    
    
    time=keyword_time_offset(incident, 'Ignition-Off')
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

def distance_travelled(incident):  # calculates the distance travelled after the alert 
    # grab zoomed out data
    data = incident[2]

    # find x and y position of where the car ends up 
    xpos = data['gridx'].iloc[-1]
    ypos = data['gridy'].iloc[-1]
    xpos = xpos.item()
    ypos = ypos.item()

    # create vector of that position and find magnitude of it (distance)
    pos = np.array([xpos,ypos])
    distance = np.linalg.norm(pos)

    return distance

""" ^^^ DISPLACEMENT, VELOCITY, ACCELERATION FUNCTIONS ^^^ """

""" vvv TILTS FUNCTIONS vvv """

def mag_spike_difference(tilts): # a measure which captures whether or not there are a few spikes in acceleration or just one big one
    
    # magnitude at each time step
    mags = np.linalg.norm(tilts, axis=1)

    # get top 5 mags
    sorted_mags = np.argsort(mags)
    top_5 = sorted_mags[-5:]
    
    # calculate the difference between the max mag and the average of the next 4 highest
    average = np.average(top_5[1:])
    difference = top_5[0]-average

    return difference            

def get_std_xtilt(tilts):    
    return np.std(tilts[:,0])

def get_std_ytilt(tilts):
    return np.std(tilts[:,1])

def get_max_acc(tilts):
    accs = []
    x = tilts[:,0]
    y = tilts[:,1]

    for i in range(len(x)):
        # Get the acceleration in the horizontal plane
        acc = np.linalg.norm([x[i], y[i]])
        accs.append(acc)

    return np.max(accs)

#function to return four largest powers and corresponding frequencies
#usage: x_or_y = 0 for x values, 1 for y values
def periodogram_feauture_extractor(tilts_no_z,x_or_y):
    number_data_points = 72
    s_s = 1/8 #sample spacing
    sum_tilts = tilts_no_z[:,x_or_y]
    fourier_freqs = rfftfreq(number_data_points,d=s_s)
    periodogram_data = spectrum.speriodogram(sum_tilts,NFFT=number_data_points)
    sorted_periodogram_data = sorted(periodogram_data,reverse=True)
    largest_powers = sorted_periodogram_data[0:4]
    corresponding_frequencies = []
    for power in range(4):
        index = []
        if largest_powers[power] == 0:
            corresponding_frequencies.append(0) #if the power is 0 we return a frequency of 0
        else:
            #if we have multiple frequncies with the same exact powers we return the smallest frequency
            index = np.where(periodogram_data == largest_powers[power])
            corresponding_frequencies.append(fourier_freqs[index[0][0]])

    power_1 = largest_powers[0]
    power_2 = largest_powers[1]
    power_3 = largest_powers[2]
    power_4 = largest_powers[3]
    frequency_1 = corresponding_frequencies[0]
    frequency_2 = corresponding_frequencies[1]
    frequency_3 = corresponding_frequencies[2]
    frequency_4 = corresponding_frequencies[3]
    
    

    return power_1,power_2,power_3,power_4,frequency_1,frequency_2,frequency_3,frequency_4

""" ^^^ TILTS FUNCTIONS ^^^ """

def extract_features(data):
    # Give data (cat/uncat), returns features array

    ignition_freq_list = []
    stop_freq_list = []
    ignition_times_list = []
    stop_time_list = []
    
    d_v_list = []
    max_acc_list = []
    distance_list = []
    xstd = []
    ystd = []
    times_of_0_vel = []
    x_power_1_list = []
    x_power_2_list= []
    x_power_3_list = []
    x_power_4_list = []
    mag_spike_difference_list = []
    x_frequency_1_list = []
    x_frequency_2_list = []
    x_frequency_3_list = []
    x_frequency_4_list = [] 
    y_power_1_list = []
    y_power_2_list= []
    y_power_3_list = []
    y_power_4_list = []
    y_frequency_1_list = []
    y_frequency_2_list = []
    y_frequency_3_list = []
    y_frequency_4_list = [] 
    max_vel_changes = []

    tilts = get_tilt_timeseries(data)
    tilts_no_z = calibrate_remove_z(tilts)

    for incident in range(len(data)):
        
        ignition_freq = keyword_freq(data[incident], 'Ignition-Off')
        stop_freq = keyword_freq(data[incident], 'Stop')
        ignition_time = keyword_time_offset(data[incident], 'Ignition-Off')
        stop_time = keyword_time_offset(data[incident], 'Stop')
        
        d_v = get_vel_change(data[incident])
        max_acc = get_max_acc(tilts_no_z[incident])
        
        distance = distance_travelled(data[incident])
        x_power_1,x_power_2,x_power_3,x_power_4,x_frequency_1,x_frequency_2,x_frequency_3,x_frequency_4 = periodogram_feauture_extractor(tilts_no_z[incident],0)
        y_power_1,y_power_2,y_power_3,y_power_4,y_frequency_1,y_frequency_2,y_frequency_3,y_frequency_4 = periodogram_feauture_extractor(tilts_no_z[incident],1)

        difference = mag_spike_difference(tilts_no_z[incident])
        
        
        ignition_freq_list.append(ignition_freq)
        stop_freq_list.append(stop_freq)
        ignition_times_list.append(ignition_time)
        stop_time_list.append(stop_time)
        
        max_vel_changes.append(get_max_vel_chng(data[incident]))
        d_v_list.append(d_v)
        max_acc_list.append(max_acc)
        
        distance_list.append(distance)
        xstd.append(get_std_xtilt(tilts_no_z[incident]))
        ystd.append(get_std_ytilt(tilts_no_z[incident]))
        times_of_0_vel.append(max_stop_time(data[incident]))
        x_power_1_list.append(x_power_1)
        x_power_2_list.append(x_power_2)
        x_power_3_list.append(x_power_3)
        x_power_4_list.append(x_power_4)
        mag_spike_difference_list.append(difference)
        x_frequency_1_list.append(x_frequency_1)
        x_frequency_2_list.append(x_frequency_2)
        x_frequency_3_list.append(x_frequency_3)
        x_frequency_4_list.append(x_frequency_4)
        y_frequency_1_list.append(y_frequency_1)
        y_frequency_2_list.append(y_frequency_2)
        y_frequency_3_list.append(y_frequency_3)
        y_frequency_4_list.append(y_frequency_4)
        y_power_1_list.append(y_power_1)
        y_power_2_list.append(y_power_2)
        y_power_3_list.append(y_power_3)
        y_power_4_list.append(y_power_4)
        
        
    features = np.transpose(np.array([ignition_freq_list, stop_freq_list, d_v_list, max_acc_list, ignition_times_list, stop_time_list, 
                                        distance_list, xstd, ystd, times_of_0_vel,x_power_1_list,x_power_2_list ,x_power_3_list, x_power_4_list, 
                                        mag_spike_difference_list, x_frequency_1_list, x_frequency_2_list, x_frequency_3_list, x_frequency_4_list,
                                        y_power_1_list, y_power_2_list, y_power_3_list, y_power_4_list, y_frequency_1_list, y_frequency_2_list, 
                                        y_frequency_3_list, y_frequency_4_list, max_vel_changes]))

    return features

# load in the data
cat_data = load_list('pickle_data', 'cat_data')

# get the features 
features = extract_features(cat_data)