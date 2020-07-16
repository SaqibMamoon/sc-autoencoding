# -*- coding: utf-8 -*-
"""
Created on Wed Jul  8 15:11:23 2020

@author: Mike Toreno II
"""

'''Please note, the clustering is based on all the received dimensions, however, plotted are only the first 2 (of course)'''



import sys
import os
import argparse
from datetime import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
import statistics





print(datetime.now().strftime("%H:%M:%S>"), "Starting sca_kmcluster.py")


try:
    os.chdir(os.path.dirname(sys.argv[0]))
except:
    pass
         


parser = argparse.ArgumentParser(description = "clustering data")  #required
parser.add_argument("-k","--k", default = 6, help="the number of clusters to find", type = int)
parser.add_argument("-d","--dimensions", help="enter a value here to restrict the number of input dimensions to consider", type = int, default = 0)
parser.add_argument("-i","--input_dir", help="input directory", default = "../inputs/baseline_data/scaPCA_output/")
parser.add_argument("-o","--output_dir", help="output directory", default = "../outputs/kmcluster/")
parser.add_argument("-p","--outputplot_dir", help="plot directory", default = "../outputs/kmcluster/")
parser.add_argument("-v","--verbosity", help="level of verbosity", default = 0, choices = [0, 1, 2, 3], type = int)
parser.add_argument("-e", "--elbow", help="helptext", action="store_true")
parser.add_argument("-t","--title", help="title that will be written into the output file", default = "title placeholder")
parser.add_argument("-r", "--reset", help="if this is called, the previous results file will be overwritten, otherwise results are appended", action="store_true")
args = parser.parse_args() #required



input_path = args.input_dir
output_dir = args.output_dir
outputplot_dir = args.outputplot_dir
k = args.k
verbosity = args.verbosity


tech_start = input_path.find("/sca")
tech_end = input_path.find("_output/")


technique_name = input_path[tech_start + 4 : tech_end]




# %% Read Input data
print(datetime.now().strftime("%H:%M:%S>"), "loading data...")
data = np.loadtxt(open(input_path + "matrix.tsv"), delimiter="\t")


# load barcodes
barcodes = pd.read_csv(input_path + "barcodes.tsv", delimiter = "\t", header = None)
truelabels = barcodes.iloc[:,1]


# %% Clustering

print(datetime.now().strftime("%H:%M:%S>"), "Clustering...")

if args.dimensions == 0:
    dims = data.shape[1]
    #print("dims was set to {0:d}".format(dims))
else:
    dims = args.dimensions
    #print("dims was set to {0:d}".format(dims))
    

data = data[:,range(dims)]

km = KMeans(
    n_clusters=k, init='k-means++',
    n_init=10, max_iter=300, 
    tol=1e-04, verbose = verbosity
) # default values


predicted_labels = km.fit_predict(data)




# %% Plotting first simple plot
if not os.path.exists(outputplot_dir):
    print(datetime.now().strftime("%H:%M:%S>"), "Creating Output Plot Directory...")
    os.makedirs(outputplot_dir)
    

print(datetime.now().strftime("%H:%M:%S>"), "Plotting Clusters...")

import random

import matplotlib.cm as cm 
colors = cm.rainbow(np.linspace(0, 1, k))
shapes = [".","o","v","^","<",">","8","s","p","P","*","h","H","X","D","d"]



# #plt.figure()
# for i in range(k):
#     plt.scatter(
#     x = data[predicted_labels == i, 0], 
#     y = data[predicted_labels == i, 1],
#     s=50, 
#     c=colors[i,].reshape(1,-1),
#     marker=random.choice(shapes), 
#     edgecolor='black',
#     label='cluster {0:d}'.format(i)
#     )
# plt.legend(scatterpoints=1)
# plt.title(technique_name)
# plt.xlabel = "Component 1"
# plt.ylabel = "Component 2"
# plt.grid()
# plt.show()
# plt.savefig(outputplot_dir + "clusterplot.png")

# %% Elbow

if args.elbow:
    print(datetime.now().strftime("%H:%M:%S>"), "Calculating Elbow...")
    
    # calculate distortion for a range of number of cluster
    distortions = []
    for i in range(1, 11):
        km = KMeans(
            n_clusters=k, init='k-means++',
            n_init=10, max_iter=300, 
            tol=1e-04, verbose = verbosity
        ) # default values
        km.fit(data)
        distortions.append(km.inertia_)
    
    # plot
    plt.figure()
    plt.plot(range(1, 11), distortions, marker='o')
    plt.xlabel('Number of clusters')
    plt.ylabel('Distortion')
    plt.show()
    plt.savefig(outputplot_dir + "Elbowplot.png")
    







# %% Evaluate Purity
from collections import Counter
print(datetime.now().strftime("%H:%M:%S>"), "Evaluate Clustering...")


clusterlabels = []
purity_per_cluster = []
recall_per_cluster = []
  
multiassigned = np.zeros(k, dtype=bool)

global_counts = Counter(truelabels)


for cluster in range(k):
    indexes = np.where(predicted_labels == cluster)[0] 

    truelabels_in_cluster = truelabels[indexes]   
    counts = Counter(truelabels_in_cluster)
    most_common_str = ((counts.most_common(2))[0])[0]
    most_common_cnt = ((counts.most_common(2))[0])[1]
    
    
    # find "multiple assigned celltypes"
    if most_common_str in clusterlabels:
        idx = clusterlabels.index(most_common_str)
        multiassigned[cluster] = True
        multiassigned[idx] = True
        
        
    clusterlabels.append(most_common_str)         
    # clusterlabels_noedit    
    
    
    # calculate purity
    purity = most_common_cnt/len(truelabels_in_cluster)
    purity_per_cluster.append(purity)
    
    # calculate recall
    # the percentage of all cells of this type, that are in the cluster
    recall = most_common_cnt / global_counts[most_common_str]
    recall_per_cluster.append(recall)

# add cluster number to multiassigneds, to mark them e.g. on the plot



# create clusterlabels dictionary for the truefalseplot
clusterlabels_dictionary = {}
for i in range(len(clusterlabels)):
    clusterlabels_dictionary[i] = clusterlabels[i]





for idx in range(len(multiassigned)):
    if multiassigned[idx]:
        clusterlabels[idx] = clusterlabels[idx] + " (Cluster " + str(idx) + ")"

purity_per_cluster = np.round(purity_per_cluster, 4)       
recall_per_cluster = np.round(recall_per_cluster, 4)  


    
# %%
# replot with labels

plt.figure()
for cluster in range(k):
    plt.scatter(
    x = data[predicted_labels == cluster, 0], 
    y = data[predicted_labels == cluster, 1],
    s=50, 
    c=colors[cluster,].reshape(1,-1),
    marker=random.choice(shapes), 
    edgecolor='black',
    label= clusterlabels[cluster],
    )
        
plt.title(technique_name + " Clustering Prediction")
plt.xlabel = "Component 1"
plt.ylabel = "Component 2"
plt.legend(scatterpoints=1)
plt.grid()
plt.show()
plt.savefig(outputplot_dir + "clusterplot_prediction.png")
    


# %%replot with true labels

predicted_labels_text = [clusterlabels_dictionary[i] for i in predicted_labels]

correct_indexes = np.array(predicted_labels_text) != np.array(truelabels).all()

print(sum(correct_indexes))

truedata = data[correct_indexes, 0]



plt.figure()

plt.scatter(
x = data[correct_indexes, 0], 
y = data[correct_indexes, 1],
s=50, 
c=np.array([1, 0, 0, 0]).reshape(1,-1),
marker="o", 
edgecolor='black',
label= "correct ones",
)

plt.scatter(
x = data[~correct_indexes, 0], 
y = data[~correct_indexes, 1],
s=50, 
c=np.array([1, 0, 0, 0.5]).reshape(1,-1),
marker="o", 
edgecolor='black',
label= "incorrect ones",
)

        
plt.title(technique_name)
plt.xlabel = "Component 1"
plt.ylabel = "Component 2"
plt.legend(scatterpoints=1)
plt.grid()
plt.show()
plt.savefig(outputplot_dir + "clusterplot_mistakes.png")
    








# %% Saving result
print(datetime.now().strftime("%H:%M:%S>"), "Saving Results...")


if not os.path.exists(output_dir):
    print(datetime.now().strftime("%H:%M:%S>"), "Creating Output Directory...")
    os.makedirs(output_dir)


if args.reset:
    file = open(output_dir + "km_clustering_results.txt", "w")
else:
    file = open(output_dir + "km_clustering_results.txt", "a")
    file.write("\n")
    file.write("\n")
    file.write("\n")
    file.write("\n")
    

file.write("######" + args.title + "######\n")
file.write("input_data from " + input_path + "\n")
file.write("\nAverage Purity: \t" + '{:.4f}'.format(statistics.mean(purity_per_cluster)))
file.write("\t(" + str(purity_per_cluster).strip("[]") + ")")

file.write("\nAverage Recall: \t" + '{:.4f}'.format(statistics.mean(recall_per_cluster)))
file.write("\t(" + str(recall_per_cluster).strip("[]") + ")")

file.write("\nCluster labels: t" + str(clusterlabels).strip("[]") + ")")

file.close()




# %%

print(datetime.now().strftime("%H:%M:%S>"), "sca_kmcluster.py terminated successfully\n")











