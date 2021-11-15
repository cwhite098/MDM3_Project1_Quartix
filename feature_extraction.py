from extract_data import *
from sklearn.metrics import confusion_matrix
from numpy.fft import rfft,rfftfreq,fft
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import spectrum

""" vvv KEYWORD FUNCTIONS vvv """

def keyword_freq(incident, keyword): # returns the frequency of a given keyword

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

""" vvv DISTANCE AND SPEED FUNCTIONS vvv """

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

def get_vel_change(incident): # returns the change in speed between the alert and t = 3
    
    data = incident[0]
    data = data['speed'].values
    d_v = data[6]-data[9]
    
    return d_v

def get_max_vel_chng(incident): # returns the largest change in speed in the zoomed in data
    
    current = 0
    data0 = incident[0]
    data0 =data0["speed"].values

    for i in range(8):
        if(i<7):
            if abs(data0[i]-data0[i+1])>current:
                current = abs(data0[i]-data0[i+1])
    return current 

def distance_till_ig_off(incident): # returns distance from alert to first ignition off
    data=incident[2]    
    
    time=keyword_time_offset(incident, 'Ignition-Off')
    
    ids = data.index[data['timeoffset'] == time].tolist()[0]
    gridx=0
    gridy=0
    
    gridx=data.loc[data.index[ids], 'gridx']
    gridy=data.loc[data.index[ids], 'gridy']

    mag = gridx**2+gridy**2
    mag = mag**(1/2)
    return mag

def distance_travelled(incident):  # returns the distance travelled after the alert 
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

""" ^^^ DISTANCE AND SPEED FUNCTIONS ^^^ """

""" vvv TILT FUNCTIONS (all use calibrated tilts) vvv """

def mag_spike_difference(tilts_no_z): # returns the difference between the highest spike in acceleration and the average of the next 4 highest
    
    # magnitude at each time step
    mags = np.linalg.norm(tilts_no_z, axis=1)

    # get top 5 mags
    sorted_mags = np.argsort(mags)
    top_5 = sorted_mags[-5:]
    
    # calculate the difference between the max mag and the average of the next 4 highest
    average = np.average(top_5[1:])
    difference = top_5[0]-average

    return difference            

def get_std_xtilt(tilts_no_z): # returns standard deviation of x tilts
    return np.std(tilts_no_z[:,0])

def get_std_ytilt(tilts_no_z): # returns standard deviation of y tilts
    return np.std(tilts_no_z[:,1])

def get_max_acc(tilts_no_z): # returns the max acceleration 
    accs = []
    x = tilts_no_z[:,0]
    y = tilts_no_z[:,1]

    for i in range(len(x)):
        # Get the acceleration in the horizontal plane
        acc = np.linalg.norm([x[i], y[i]])
        accs.append(acc)

    return np.max(accs)

def periodogram_feauture_extractor(tilts_no_z,x_or_y): # returns four largest powers and corresponding frequencies in x or y 
    number_data_points = 72
    s_s = 1/8 #sample spacing
    sum_tilts = tilts_no_z[:,x_or_y]
    fourier_freqs = rfftfreq(number_data_points,d=s_s)
    periodogram_data = spectrum.speriodogram(sum_tilts,NFFT=number_data_points)
    sorted_periodogram_data = sorted(periodogram_data,reverse=True)
    largest_powers = sorted_periodogram_data[0:6]
    corresponding_frequencies = []
    for power in range(6):
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
    power_5 = largest_powers[4]
    power_6 = largest_powers[5]
    frequency_1 = corresponding_frequencies[0]
    frequency_2 = corresponding_frequencies[1]
    frequency_3 = corresponding_frequencies[2]
    frequency_4 = corresponding_frequencies[3]
    frequency_5 = corresponding_frequencies[4]
    frequency_6 = corresponding_frequencies[5]
    
    

    return power_1,power_2,power_3,power_4,power_5,power_6,frequency_1,frequency_2,frequency_3,frequency_4,frequency_5,frequency_6

def total_spectral_energy(tilts_no_z,x_or_y): # returns the total spectral energy in x or y
    number_data_points = 72
    tilts = tilts_no_z[:,x_or_y]
    periodogram_data = spectrum.speriodogram(tilts,NFFT=number_data_points)
    total_spectral_energy = np.sum(periodogram_data)
    return total_spectral_energy


""" ^^^ TILT FUNCTIONS (all use calibrated tilts) ^^^ """

feature_count = 39

def extract_features(data, desired_features = range(39), unlinked = False): # returns features

    """ vvv initialise lists and get calibrated tilts vvv """

    # keyword (4 features)
    ignition_freq_list = []
    stop_freq_list = []
    ignition_times_list = []
    stop_time_list = []
    
    # distance and speed (5 features)
    max_stop_times_list = []
    vel_change_list = []
    max_vel_change_list = []
    distance_till_ig_off_list = []
    distance_travelled_list = []
    
    # tilts (4 features)
    mag_spike_difference_list = []
    x_std_dev_list = []
    y_std_dev_list = []   
    max_acc_list = []   
    
    # periodogram (24 features)
    x_power_1_list = []
    x_power_2_list= []
    x_power_3_list = []
    x_power_4_list = []
    x_power_5_list = []
    x_power_6_list = []
    
    x_frequency_1_list = []
    x_frequency_2_list = []
    x_frequency_3_list = []
    x_frequency_4_list = []
    x_frequency_5_list = [] 
    x_frequency_6_list = []
    
    y_power_1_list = []
    y_power_2_list= []
    y_power_3_list = []
    y_power_4_list = []
    y_power_5_list = []
    y_power_6_list = []
    
    y_frequency_1_list = []
    y_frequency_2_list = []
    y_frequency_3_list = []
    y_frequency_4_list = []
    y_frequency_5_list = []
    y_frequency_6_list = [] 
    
    # total spectral energy (2 features)
    
    x_total_spectral_energy_list = []
    y_total_spectral_energy_list = []
    
    
    # calibrate tilts
    tilts = get_tilt_timeseries(data)
    tilts_no_z = calibrate_remove_z(tilts)

    """ ^^^ initialise lists and get calibrated tilts ^^^ """

    """ vvv fill lists with data vvv """
    
    for incident in range(len(data)):
        
        # extract periodogram data for current incident
        x_power_1,x_power_2,x_power_3,x_power_4,x_power_5,x_power_6,x_frequency_1,x_frequency_2,x_frequency_3,x_frequency_4,x_frequency_5,x_frequency_6 = periodogram_feauture_extractor(tilts_no_z[incident],0)
        y_power_1,y_power_2,y_power_3,y_power_4,y_power_5,y_power_6,y_frequency_1,y_frequency_2,y_frequency_3,y_frequency_4,y_frequency_5,y_frequency_6 = periodogram_feauture_extractor(tilts_no_z[incident],1)
        
        #extract total spectral energy for current incident
        x_total_spectral_energy = total_spectral_energy(tilts_no_z,0)
        y_total_spectral_energy = total_spectral_energy(tilts_no_z,1)
        
        # update keyword lists
        if unlinked == False:
            ignition_freq_list.append(keyword_freq(data[incident], 'Ignition-Off'))
            stop_freq_list.append(keyword_freq(data[incident], 'Stop'))
            ignition_times_list.append(keyword_time_offset(data[incident], 'Ignition-Off'))
            stop_time_list.append(keyword_time_offset(data[incident], 'Stop'))
        
        # update distance and speed lists
        max_stop_times_list.append(max_stop_time(data[incident]))

        if unlinked == False:
            vel_change_list.append(get_vel_change(data[incident]))
            max_vel_change_list.append(get_max_vel_chng(data[incident]))

        if unlinked == False:    
            distance_till_ig_off_list.append(distance_till_ig_off(data[incident]))
            distance_travelled_list.append(distance_travelled(data[incident]))
        
        # update tilts lists
        mag_spike_difference_list.append(mag_spike_difference(tilts_no_z[incident]))
        x_std_dev_list.append(get_std_xtilt(tilts_no_z[incident]))
        y_std_dev_list.append(get_std_ytilt(tilts_no_z[incident]))
        max_acc_list.append(get_max_acc(tilts_no_z[incident]))
        
        # update periodogram lists
        x_power_1_list.append(x_power_1)
        x_power_2_list.append(x_power_2)
        x_power_3_list.append(x_power_3)
        x_power_4_list.append(x_power_4)
        x_power_5_list.append(x_power_5)
        x_power_6_list.append(x_power_6)
        
        x_frequency_1_list.append(x_frequency_1)
        x_frequency_2_list.append(x_frequency_2)
        x_frequency_3_list.append(x_frequency_3)
        x_frequency_4_list.append(x_frequency_4)
        x_frequency_5_list.append(x_frequency_5)
        x_frequency_6_list.append(x_frequency_6)
        
        y_power_1_list.append(y_power_1)
        y_power_2_list.append(y_power_2)
        y_power_3_list.append(y_power_3)
        y_power_4_list.append(y_power_4)
        y_power_5_list.append(y_power_5)
        y_power_6_list.append(y_power_6)
        
        y_frequency_1_list.append(y_frequency_1)
        y_frequency_2_list.append(y_frequency_2)
        y_frequency_3_list.append(y_frequency_3)
        y_frequency_4_list.append(y_frequency_4)
        y_frequency_5_list.append(y_frequency_5)
        y_frequency_6_list.append(y_frequency_6)
        
        #update spectral energy lists
        x_total_spectral_energy_list.append(x_total_spectral_energy)
        y_total_spectral_energy_list.append(y_total_spectral_energy)


    """ ^^^ fill lists with data ^^^ """    

    # add each list to features array    
    features_list = [ignition_freq_list, stop_freq_list, ignition_times_list, stop_time_list,
                    max_stop_times_list, vel_change_list, max_vel_change_list, distance_till_ig_off_list, distance_travelled_list,
                    mag_spike_difference_list, x_std_dev_list, y_std_dev_list, max_acc_list,
                    x_power_1_list, x_power_2_list, x_power_3_list, x_power_4_list, x_power_5_list, x_power_6_list,
                    x_frequency_1_list, x_frequency_2_list, x_frequency_3_list, x_frequency_4_list,x_frequency_5_list, x_frequency_6_list,
                    y_power_1_list, y_power_2_list, y_power_3_list, y_power_4_list,y_power_5_list,y_power_6_list,
                    y_frequency_1_list, y_frequency_2_list, y_frequency_3_list, y_frequency_4_list,y_frequency_5_list,y_frequency_6_list,
                    x_total_spectral_energy_list,y_total_spectral_energy_list]

    desired_feature_list = [features_list[i] for i in desired_features]

    features = np.transpose(np.array(desired_feature_list))
                                
    return features
