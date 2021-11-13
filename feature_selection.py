# method for feature selection is from the following sources
# idea: http://venom.cs.utsa.edu/dmz/techrep/2007/CS-TR-2007-011.pdf
# python implementation: https://stats.stackexchange.com/questions/108743/methods-in-r-or-python-to-perform-feature-selection-in-unsupervised-learning 

from PFA import *
from feature_extraction import *
import numpy as np

# load data and features list
uncat_data = load_list('pickle_data', 'uncat_data')
features = extract_features(uncat_data)

# run pfa many times and collect matrix of indices which pfa suggests through the given iterations are most important features
iterations = 100
n_features=10
count = 0
column_indices_mat = np.empty([iterations, n_features])

while count < iterations:
    # create pfa 
    pfa = PFA(n_features)
    pfa.fit(features)
    X = pfa.features_
    column_indices = pfa.indices_
    column_indices_mat[count,:] = column_indices
    count += 1

# see which features are most commonly suggested as the most important ones
column_indices_mat = column_indices_mat.astype(int)
freq = np.bincount(column_indices_mat.flatten())
freq = np.asarray(freq)
top_features = []

count = 0

while count < n_features:
    idx = np.argmax(freq)
    top_features.append(idx)
    freq[idx] = 0
    count += 1

# print a list of which features are the most important 
top_features.sort()
print([x+1 for x in top_features])
