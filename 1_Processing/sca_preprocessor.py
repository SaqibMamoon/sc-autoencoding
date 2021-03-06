# -*- coding: utf-8 -*-
"""
Created on Wed Jul  8 15:07:08 2020

@author: Mike Toreno II
"""


import os
import sys
import argparse
from datetime import datetime

import numpy as np
import pandas as pd
import scanpy as sc
import matplotlib.pyplot as plt

import scipy.io
from sklearn.model_selection import train_test_split



print(datetime.now().strftime("%H:%M:%S>"), "Starting sca_preprocessor.py")


try:
    os.chdir(os.path.dirname(sys.argv[0]))
except:
    pass



parser = argparse.ArgumentParser(description = "program to preprocess the raw singlecell data")
parser.add_argument("-i","--input_dir", help="input directory", default = "../inputs/data/raw_input_combined/filtered_matrices_mex/hg19/")
parser.add_argument("-o","--output_dir", help="output directory", default = "../inputs/data/preprocessed_data/")
parser.add_argument("-p","--outputplot_dir", help="plot directory", default = "../outputs/preprocessing/preprocessed_data/")
parser.add_argument("-v","--verbosity", help="level of verbosity", default = 3, choices = [0, 1, 2, 3], type = int)
parser.add_argument("-e", "--plotsonly", help="for the first run, one should only run it with this flag, where no output gets saved, only the plots to look at and get reasonable values", action="store_true")
parser.add_argument("--test_fraction", help="enter a float between 0-1. This will be the fraction of the data, that is marked as test data.", default = 0.25, type = float)

parser.add_argument("--n_splits", help="number of split", default = 3, type = int)

parser.add_argument("--saveobject", help="hitting this flag allows will save the adata object, so it can be evaluated with other techniques", action="store_true")

parser.add_argument("--mingenes", help="minimal amount of genes per cell", default = 200, type = int)
parser.add_argument("--mincells", help="minimal number of cells for a gene", default = 5, type = int)
parser.add_argument("--maxfeatures", help="maximal number of genes per cell (check plot)", default = 1500, type = int)
parser.add_argument("--maxmito", help="maximal percentage of mitochondrial counts", default = 5, type = int)
parser.add_argument("--features", help="number of highly variable features to catch", default = 2000, type = int)
args = parser.parse_args() #required



input_dir = args.input_dir
output_dir = args.output_dir
outputplot_dir = args.outputplot_dir
test_fraction = float(args.test_fraction)

min_genes_per_cell = args.mingenes
min_cells_per_gene = args.mincells
max_num_features = args.maxfeatures
max_mt_perc = args.maxmito
num_top_genes = args.features 





if not os.path.exists(output_dir):
    print(datetime.now().strftime("%H:%M:%S>"), "Creating Output Directory...")
    os.makedirs(output_dir)
    
    
if not os.path.exists(outputplot_dir):
    print(datetime.now().strftime("%H:%M:%S>"), "Creating Output Plot Directory...")
    os.makedirs(outputplot_dir)    






# %% Load Data

print(datetime.now().strftime("%H:%M:%S>"), "reading input data...")


### Get Matrix
coomatrix = scipy.io.mmread(input_dir + "matrix.mtx")
coomatrix = np.transpose(coomatrix) # samples must be rows, variables = columns

genes = pd.read_csv(input_dir + "genes.tsv", delimiter = "\t", header = None)

barcodes = pd.read_csv(input_dir + "barcodes.tsv", delimiter = "\t", header = None)






# %% ScanPy Setup

print(datetime.now().strftime("%H:%M:%S>"), "Launching Scanpy")

sc.settings.verbosity = args.verbosity             # verbosity: errors (0), warnings (1), info (2), hints (3)
sc.logging.print_versions()
sc.settings.set_figure_params(dpi=80, facecolor='white')

results_file = 'write/pbmc3k.h5ad'  # the file that will store the analysis results


# %% Read data into anndata object (holds slots for annotation etc)

AnnData = sc.read_10x_mtx(path = input_dir, var_names = "gene_ids", cache = False)


# %% Plot 20 top detected genes

sc.pl.highest_expr_genes(AnnData, n_top=20, )
plt.savefig(outputplot_dir + "top_20_detected_genes.png")






# %% basic filtering
print(datetime.now().strftime("%H:%M:%S>"), "Filtering Data with min_genes= {a:d} and min_cells= {b:d}...".format(a = min_genes_per_cell, b=min_cells_per_gene))

sc.pp.filter_cells(AnnData, min_genes = min_genes_per_cell) # only keep cells with at least 200 genes detecte
# could also pass counts instead of genes

sc.pp.filter_genes(AnnData, min_cells=min_cells_per_gene) # and only keep genes that are present in at least # cells




# %% Calculate numbers

# flag each gene if mitochondrial
AnnData.var['mt'] = AnnData.var['gene_symbols'].str.startswith(('MT-', 'MT.', 'MT\\'))  # annotate the group of mitochondrial genes as 'mt'
# only finds like 13 genes :/ But technically they do the same as seurat, so must be same?

sc.pp.calculate_qc_metrics(AnnData, qc_vars=['mt'], percent_top=None, log1p=False, inplace=True)
# adds(for each gene) n_cells_by_count, mean counts, pct_dropbout by counts, total counts
# the qc_vars = ['mt'] does not influence the calculations of AnnData.var,
# but instead the percentage calculation is made into AnnData.obs



# %% Violinplots

sc.pl.violin(AnnData, ['n_genes_by_counts', 'total_counts', 'pct_counts_mt'], jitter=0.4, multi_panel=True)
plt.savefig(outputplot_dir + "Violin_plot.png")

sc.pl.scatter(AnnData, x='total_counts', y='pct_counts_mt')
plt.savefig(outputplot_dir + "mt_percentage.png")

sc.pl.scatter(AnnData, x='total_counts', y='n_genes_by_counts')
plt.savefig(outputplot_dir + "genes_percentage.png")




#%% Filter Mitochondrial Genes and those with too many genes
print(datetime.now().strftime("%H:%M:%S>"), "Filtering Data with n_genes_by_count < {a:d} and pct_counts_mt < {b:d}...".format(a = max_num_features, b = max_mt_perc))

# slicing
AnnData = AnnData[AnnData.obs.n_genes_by_counts < max_num_features, :]
AnnData = AnnData[AnnData.obs.pct_counts_mt < max_mt_perc, :]




# %% Normalize
print(datetime.now().strftime("%H:%M:%S>"), "Normalizing...")
sc.pp.normalize_total(AnnData, target_sum=1e4)


# %% Logarithmize
print(datetime.now().strftime("%H:%M:%S>"), "Logarithmizing...")
sc.pp.log1p(AnnData)



# %% Feature Selection
print(datetime.now().strftime("%H:%M:%S>"), "Doing feature selection with {a:d} highly variable genes...".format(a = num_top_genes))
# fs_min_mean = 0.0125
# fs_max_mean = 3
# fs_min_disp = 0.5
#sc.pp.highly_variable_genes(AnnData, min_mean=fs_min_mean, max_mean=fs_max_mean, min_disp=fs_min_disp)
sc.pp.highly_variable_genes(AnnData, n_top_genes = num_top_genes + 1)



# %% plot highly variable genes
sc.pl.highly_variable_genes(AnnData)
plt.savefig(outputplot_dir + "highly_variable_genes.png")


# %% freeze the state of the object, by setting the .raw to the normalized/logarithmized
AnnData.raw = AnnData
# to reverse: .raw.to_adata()



# %% remove non variable features
AnnData = AnnData[:, AnnData.var.highly_variable]



# %% Regress out effects of total_counts_per_cell and pt_mitoch
print(datetime.now().strftime("%H:%M:%S>"), "Regress out effects of total counts per cell / pt_mito...")
sc.pp.regress_out(AnnData, ['total_counts', 'pct_counts_mt'])

# Scaling each gene unit to variance
print(datetime.now().strftime("%H:%M:%S>"), "Scaling each gene unit to variance...")
sc.pp.scale(AnnData, max_value=10)



# %% Exporting

if not args.plotsonly: 
    print(datetime.now().strftime("%H:%M:%S>"), "Generating Output...")
    # those are useless, only mean and dispersion etc
    # AnnData.write_csvs("filename2", skip_data=False)
    
    

    genes = pd.DataFrame(AnnData.var_names)
    genes["symbols"] = list(AnnData.var["gene_symbols"])
    
    panda = pd.DataFrame(AnnData.X) #obs*vars
    
    
    barcodelist = list(AnnData.obs_names)
    # alright, I give up. Lets' do it cavemen style
    bc_names = [item.split('\t')[0] for item in barcodelist]
    bc_types = [item.split('\t')[1] for item in barcodelist]

    barcodes = pd.DataFrame(data = bc_names)
    barcodes["type"] = bc_types
    
    ''' the reason why i wrote this ugly blcok is, if i just panda'd the AnnData.obs_name, it would
    write it out with quotatation marks around it, probably due to the inclusion of the \t, that forces 
    it to somehow keep the object as one (what i understand but don't want here). I've tried to just disable quotation marks
    with quotin=csv.QUOTE_NONE, but then it wanted anothe rescape character, and I gave up. And then I've tried
    to split an array of strings in two in a nice manner, but had to give up, and do it with these for items now
    I think this equals to 2 loops, so awesome for runtime (not that it matters) 
    anyway, this is a bad solution, but it fixes the problem, so meh'''
    
    
    
    
    
    
# %% Save whole thing for clustering:

    complete_dir = output_dir + "no_split/"
    os.makedirs(complete_dir, exist_ok=True)


    panda.to_csv(complete_dir + "matrix.tsv", sep = "\t", index = False, header = False)
    genes.to_csv(complete_dir + "genes.tsv", sep = "\t", index = False, header = False)
    barcodes.to_csv(complete_dir + "barcodes.tsv", sep = "\t", index = False, header = False)



    
    # %% Train Test Split
  
    for j in range(args.n_splits):
        i = j+1
        print(datetime.now().strftime("%H:%M:%S>"), "Creating Train Test Split for split", i)
  
        fold_dir = output_dir + "split_" + str(i) + "/"
        os.makedirs(fold_dir, exist_ok=True)
        
        
        X_train, X_test, y_train, y_test = train_test_split(panda, bc_types, test_size=test_fraction, shuffle = True)   # alternative: stratify
        # variables are unused, just extract the index from X_train
        train_indexes = list(X_train.index)
        test_indexes = list(X_test.index)
        
        
        # create boolean
        test_index = np.zeros(len(bc_types), dtype = bool)
        for i in test_indexes:
            test_index[i] = True

    
        np.savetxt(fold_dir + "test_index.tsv", test_index, fmt = "%d")
        
        
        # save the rest of the data too
        panda.to_csv(fold_dir + "matrix.tsv", sep = "\t", index = False, header = False)
        genes.to_csv(fold_dir + "genes.tsv", sep = "\t", index = False, header = False)
        barcodes.to_csv(fold_dir + "barcodes.tsv", sep = "\t", index = False, header = False)




# %%


print(datetime.now().strftime("%H:%M:%S>"), "sca_preprocessor.py terminated successfully\n")

if not args.saveobject:
    import pickle
    file = open(output_dir + "AnnData_preprocessor.obj", "wb")
    pickle.dump(AnnData, file)
    









