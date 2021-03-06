# -*- coding: utf-8 -*-
"""
Created on Sat Jul 18 20:03:52 2020

@author: Mike Toreno II
"""




import argparse


parser = argparse.ArgumentParser(description = "evaluation")  #required
parser.add_argument("-i","--input_dir", help="input directory", default = "../inputs/baselines/baseline_data/scaPCA_output/")
parser.add_argument("-o","--output_dir", help="output directory", default = "../outputs/optimization/dbscan_gridsearch/")

parser.add_argument('-e', '--eps', nargs='+', type = float, default = [10, 15.5, 30], help="pass the number of components to try like this: python script.py --num_components 5 10 20 40")
parser.add_argument('-m', '--minpts', nargs='+', type = int, default = [1, 2], help="pass the number of components to try like this: python script.py --num_components 5 10 20 40")

args = parser.parse_args() #required









##############################################################################
##### Main

def dbscan_gridsearch(input_dir,
             output_dir,
             eps = [20, 22.5, 23],
             min_pts = [1, 2]
             ):

    from datetime import datetime

    print(datetime.now().strftime("%H:%M:%S>"), "Starting dbscan_gridsearch_pca.py")
    
    eps.sort()
    min_pts.sort()

    
    # %%
    import sys
    import os
    
    try:
        os.chdir(os.path.dirname(sys.argv[0]))
    except:
        pass
       
    

    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd
    
    import subprocess
    
    
         
    # %% 

    
    purities = np.zeros((len(eps), len(min_pts)))
    num_clusters = np.zeros((len(eps), len(min_pts)))
    outlier_fraction = np.zeros((len(eps), len(min_pts)))

    totals = len(min_pts) * len(eps)
    runcounter = 1

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)



    file = open(output_dir + "dbscan_clustering_results.txt", "w")
    file.write("DBScan Gridsearch:\n###############################\n\n")    
    file.close()
                        
    
    for i in range(len(eps)):
        ep = eps[i]
        
        for j in range(len(min_pts)):
            minp = min_pts[j]
            
            print(datetime.now().strftime("%H:%M:%S>"), "Starting dbscan with eps = {eps} and minpts = {minpts}. ({idx}/{total})".format(eps = ep, minpts = minp, idx = runcounter, total = totals))
            runcounter = runcounter + 1



            outputplot_dir = output_dir + "eps{0}_minpts{1}/".format(ep, minp)
            if not os.path.exists(outputplot_dir):
                os.makedirs(outputplot_dir)
            
            command = "python ../4_Evaluation/sca_dbscan.py --eps {eps} --min_samples {minpts} --title {title:s} --verbosity 0 --dimensions 0 --input_dir {inp:s} --output_dir {outp:s} --outputplot_dir {outplot:s}".format(eps = ep, minpts = minp, inp = input_dir, outp = output_dir, outplot = outputplot_dir, title = "DBScan_with_eps{eps}_minpts{minpts}".format(eps = ep, minpts = minp))
            print(command)
            
            p2 = subprocess.run(args = command, shell = True, capture_output = True, text = True, check = False)


            print(p2.stdout)
            print(p2.stderr)
            
            
            idx_of_purity = p2.stdout.find("average purity: ")
            purity = p2.stdout[idx_of_purity+16:idx_of_purity+24]
            purity = float(purity)
            purities[i,j] = purity
            
            
            idx_of_nclust = p2.stdout.find("number of clusters found: ")
            n_clusters = p2.stdout[idx_of_nclust+26:idx_of_nclust+28]
            n_clusters = int(n_clusters)            
            num_clusters[i,j] = n_clusters
            


            idx_of_outfrac = p2.stdout.find("Outlier Fraction is ")
            outfrac = p2.stdout[idx_of_outfrac+20:idx_of_outfrac+26]
            outfrac = float(n_clusters)            
            outlier_fraction[i,j] = outfrac            

            
            
            
            plt.close('all')
            
            
    purities = pd.DataFrame(data = purities, index = eps, columns = min_pts)        
    num_clusters = pd.DataFrame(data = num_clusters, index = eps, columns = min_pts)                
    outlier_fraction = pd.DataFrame(data = outlier_fraction, index = eps, columns = min_pts)      


    purities.to_csv(output_dir + "purity_table.tsv", sep = "\t", index = True, header = True)
    num_clusters.to_csv(output_dir + "n_clusters_table.tsv", sep = "\t", index = True, header = True)
    outlier_fraction.to_csv(output_dir + "outlier_fraction.tsv", sep = "\t", index = True, header = True)
    # np.savetxt(output_dir + "purity_table.tsv", purities, delimiter = "\t")
    # np.savetxt(output_dir + "n_clusters_table.tsv", num_clusters, delimiter = "\t")




# %%

    
    fig, ax = plt.subplots(1,1)
    
    plt.title("purities per combination\n(axis NOT evenly spaced)")
    img = ax.imshow(purities, interpolation = "bilinear", origin = "lower", cmap = "RdYlGn")
    fig.colorbar(img)
    
    ax.set_xlabel("min_pts")
    ax.set_ylabel("eps")
    
    plt.xticks(np.arange(len(min_pts)), min_pts)   
    plt.yticks(np.arange(len(eps)), eps)
    
    plt.savefig(output_dir + "purities.png")
    
    
    
    
    
    
    
    plt.figure()
    plt.title("number of found clusters per combination\n(axis NOT evenly spaced)")
    img2 = plt.imshow(num_clusters, interpolation = "bilinear", origin = "lower", cmap = "ocean")
    plt.colorbar(img2)
    
    plt.xlabel("min_pts")
    plt.ylabel("eps")    
    
    plt.xticks(np.arange(len(min_pts)), min_pts)   
    plt.yticks(np.arange(len(eps)), eps)    

    plt.savefig(output_dir + "num_clusters.png")
    






    fig, ax = plt.subplots(1,1)
    
    plt.title("outlier fraction per combination\n(axis NOT evenly spaced)")
    img = ax.imshow(outlier_fraction, interpolation = "bilinear", origin = "lower", cmap = "jet")
    fig.colorbar(img)
    
    ax.set_xlabel("min_pts")
    ax.set_ylabel("eps")
    
    plt.xticks(np.arange(len(min_pts)), min_pts)   
    plt.yticks(np.arange(len(eps)), eps)
    
    plt.savefig(output_dir + "outlier_fraction.png")






    print(datetime.now().strftime("%H:%M:%S>"), "Gridsearch terminated successfully")

# %%


if __name__ == "__main__":
    
    dbscan_gridsearch(input_dir = args.input_dir, output_dir = args.output_dir, eps = args.eps, min_pts= args.minpts)


