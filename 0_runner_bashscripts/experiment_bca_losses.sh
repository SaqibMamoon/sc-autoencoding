
source ~/anaconda3/etc/profile.d/conda.sh # to source the conda command. Check directory if it doesn't work.
conda activate tf
printf "[BCA experiment losses] " 
conda env list	# it should be visible in the log-textfile. I'm not saving it to anything else.



mkdir logs
logfile="logs/6_exBCA_losses.log"

preprocessed_ctdata="../inputs/data/preprocessed_data_autoencoder/"
outdir="../outputs/experiments/losses/"


#"cosine_proximity" "categorical_crossentropy"
#losses=("poisson_loss" "poisson" "mse" "mae" "mape" "msle" "squared_hinge" "hinge" "binary_crossentropy" "categorical_crossentropy" "kld")
#losses=("poisson" "mse" "poisson_loss")
losses=("poisson" "mse" "poisson_loss" "mae" "mape" "msle" "squared_hinge" "hinge" "binary_crossentropy"  "kld")






start=`date +%s`
printf "############################################################################\n################### " &>> $logfile
echo -n START: `date` |& tee -a $logfile
printf " ###################\n############################################################################\n\n" &>> $logfile


(
for loss in ${losses[@]}; do
echo $loss

	(
	python ../3_Autoencoder/bca_autoencoder.py --mode complete --loss $loss --activation relu --optimizer Adam --input_dir $preprocessed_ctdata --output_dir "${outdir}bca_data/${loss}/" --outputplot_dir "${outdir}bca_data/${loss}/"  |& tee -a $logfile
	
	(
	python ../4_Evaluation/sca_kmcluster.py --title ${loss} --k 8 --limit_dims 0 --verbosity 0 --input_dir "${outdir}bca_data/${loss}/" --output_dir "${outdir}cluster_result/" |& tee -a $logfile
	) & (
	python ../4_Evaluation/sca_randforest.py --title ${loss} --n_trees 100 --input_dir "${outdir}bca_data/${loss}/" --output_dir "${outdir}randomforest_result/" |& tee -a $logfile
	) & (
	python ../4_Evaluation/sca_dbscan.py  --title ${loss} --verbosity 0 --eps 17 --min_samples 3 --input_dir "${outdir}bca_data/${loss}/" --output_dir "${outdir}dbscan_result/" |& tee -a $logfile
	)
	
	wait
	)

done
wait
)


(
python ../4_Evaluation/visualize.py  --title "BCAloss"  --output_dir ${outdir} --random_forest_results "${outdir}randomforest_result/" --kmcluster_results "${outdir}cluster_result/" --dbscan_results "${outdir}dbscan_result/" |& tee -a $logfile
)



end=`date +%s`
printf "\nExperiment losses took %d minutes\n" `echo "($end-$start)/60" | bc` |& tee -a $logfile
printf "\n################### " &>> $logfile
echo -n DONE: `date` |& tee -a $logfile
printf " ####################\n############################################################################\n\n\n\n\n\n" &>> $logfile




