


source ~/anaconda3/etc/profile.d/conda.sh # to source the conda command. Check directory if it doesn't work.
conda activate tf
printf "[optimize_ICA_inpdim.sh ] "
conda env list	# it should be visible in the log-textfile. I'm not saving it to anything else. 

mkdir logs



PCA_output="../inputs/baseline_data/scaPCA_output/"
output="../outputs/optimization/"

numbers=(010 013 014 016 017 018 019 021 022 023 024 025 026 028 035 045 065 070 080 090 095)
#numbers=(003 005 008 012 015 020 030 040 050 060 085 100)
#numbers=(2 10 100)
#numbers=(2 3 4 5 6 7 8 9 10 12 14 16 18 20 24 28 32 36 40 45 50 55 60 65 70 75 80 85 90 95 100)



logfile="logs/5_optimize_ICA_inDs.log"

foldername="ica_nimput/"
folderdata="ica_data/"
folderclust="ica_kmclresult/"
foldertree="ica_treeresult/"
folderdbs="ica_dbscanresults/"

printf "\n\n" #for the logtxt
printf "############################################################################\n################### " &>> $logfile
echo -n START: `date` |& tee -a $logfile
printf " ###################\n############################################################################\n\n" &>> $logfile
start=`date +%s`



ntrees=100

(
for limit in ${numbers[@]}; do

	(
	python ../2_Baseline_Scripts/sca_ICA.py --mode complete --num_components 100 --input_dims $limit --input_dir $PCA_output --output_dir "${output}${foldername}${folderdata}${limit}/" --outputplot_dir "${output}${foldername}${folderdata}${limit}/" |& tee -a $logfile


	(
	python ../4_Evaluation/sca_kmcluster.py --title "${limit[$i]}inDs" --k 10 --limit_dims 0 --verbosity 0 --input_dir "${output}${foldername}${folderdata}${limit}/" --output_dir ${output}${foldername}${folderclust} |& tee -a $logfile
	) & (
	python ../4_Evaluation/sca_randforest.py --title "${limit[$i]}inDs" --n_trees $ntrees --input_dir "${output}${foldername}${folderdata}${limit}/" --output_dir ${output}${foldername}${foldertree} |& tee -a $logfile
	) & (
	python ../4_Evaluation/sca_dbscan.py  --title "${limit[$i]}inDs" --verbosity 0 --eps 17 --min_samples 3 --input_dir "${output}${foldername}${folderdata}${limit}/" --output_dir ${output}${foldername}${folderdbs} |& tee -a $logfile
	)
	wait
	)


done
wait
)

echo "I got here"

(
python ../4_Evaluation/visualize.py  --title "ICA"  --output_dir ${output}${foldername} --random_forest_results ${output}${foldername}${foldertree} --kmcluster_results ${output}${foldername}${folderclust} --dbscan_results ${output}${foldername}${folderdbs} |& tee -a $logfile
)
wait

end=`date +%s`
printf "\nICA optimization took %d minutes\n" `echo "($end-$start)/60" | bc` |& tee -a $logfile
printf "\n################### " |& tee -a $logfile
echo -n DONE: `date` |& tee -a $logfile
printf " ####################\n############################################################################\n\n\n\n\n\n" |& tee -a $logfile

