# -*- coding: utf-8 -*-
"""
Created on Wed Nov 10 17:10:00 2021

@author: kiera
"""


from feature_selection import *
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler, RobustScaler, MinMaxScaler
from sklearn.manifold import TSNE
from sklearn.cluster import KMeans
from metrics import *
from sklearn.metrics import confusion_matrix
import numpy as np
from scipy.cluster.hierarchy import dendrogram, linkage

# Init scaler
scaler = StandardScaler()
cat_data = get_data('data/categorised.json')
save_list(cat_data, 'pickle_data', 'cat_data')
uncat_data = get_data('data/uncategorised.json')
save_list(uncat_data, 'pickle_data', 'uncat_data')
# Load data and labels
cat_data = load_list("C:\\Users\\kiera\\Documents\\university\\3rd year\\mdm 3\\quartix\\MDM3_Project1_Quartix\\pickle_data", 'cat_data')
uncat_data = load_list("C:\\Users\\kiera\\Documents\\university\\3rd year\\mdm 3\\quartix\\MDM3_Project1_Quartix\\pickle_data", 'uncat_data')
labels = np.array(get_labels(cat_data))

# Get features from data and scale
train_x = extract_features(uncat_data)
train_x = scaler.fit_transform(train_x)
print(train_x.shape)
test_x = extract_features(cat_data)
test_x = scaler.transform(test_x)

pca = PCA(n_components=4)
train_pca = pca.fit_transform(train_x)
test_pca = pca.transform(test_x)

linked = linkage(test_pca, 'single')

labelList = range(1, 11)

plt.figure(figsize=(10, 7))
dendrogram(linked,
            orientation='top',
            labels=labelList,
            distance_sort='descending',
            show_leaf_counts=True)
plt.show()