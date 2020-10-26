


source ~/anaconda3/etc/profile.d/conda.sh # to source the conda command. Check directory if it doesn't work.
conda activate tf
printf "[do evaluation.sh ] "
conda env list	# it should be visible in the log-textfile. I'm not saving it to anything else. 



directories=(
"../inputs/baseline_data/scaPCA_output/"
"../inputs/baseline_data/scaICA_output/"
"../inputs/baseline_data/scaLSA_output/"
"../inputs/baseline_data/scaTSNE_output/"
"../inputs/baseline_data/scaUMAP_output/"
"../inputs/data/preprocessed_data/"
"../inputs/autoencoder_data/DCA_output/"
)

titles=(
"PCA"
"ICA"
"LSA"
"tSNE"
"UMAP"
"original_data"
"DCA"
)


mkdir logs
errfile="../ERROR_ERROR_ERROR_ERROR_ERROR_ERROR_ERROR.error"

# make sure titles and directories have the same length
if [ ${#directories[@]} = ${#titles[@]} ]; then 
range=$(eval echo "{0..$[${#directories[@]}-1]}")
else
exit
fi



(
tech=random_forest
output_dir=../outputs/$tech/
ntrees=100

for i in $range; do
	(
	input_dir=${directories[$i]}
	logfile=logs/4_${tech}_${titles[$i]}.log

	printf "############################################################################\n################### " &>> $logfile
	echo -n START: `date` &>> $logfile
	start=`date +%s`
	printf " ###################\n############################################################################\n\n" &>> $logfile

	python ../4_Evaluation/sca_randforest.py --title ${titles[$i]} --n_trees $ntrees --input_dir $input_dir --output_dir $output_dir |& tee -a $logfile


	end=`date +%s`
	printf "\n$tech took %d minutes\n" `echo "($end-$start)/60" | bc` &>> $logfile
	printf "\n################### " &>> $logfile
	echo -n DONE: `date` &>> $logfile
	printf " ####################\n############################################################################\n\n\n\n\n\n" &>> $logfile
	) &
done
wait # we ABSOLUTELY need a wait within the brackets, and a "&" outside of it in order to ensure the last echo to wait for all commands
) &

(
tech=kmcluster
output_dir=../outputs/$tech/

for i in $range; do
	(
	input_dir=${directories[$i]}
	logfile=logs/4_${tech}_${titles[$i]}.log

	printf "############################################################################\n################### " &>> $logfile
	echo -n START: `date` &>> $logfile
	start=`date +%s`
	printf " ###################\n############################################################################\n\n" &>> $logfile

	python ../4_Evaluation/sca_kmcluster.py --title ${titles[$i]} --k 10 --dimensions 0 --verbosity 0 --input_dir $input_dir --output_dir $output_dir |& tee -a $logfile

	end=`date +%s`
	printf "\n$tech took %d minutes\n" `echo "($end-$start)/60" | bc` &>> $logfile
	printf "\n################### " &>> $logfile
	echo -n DONE: `date` &>> $logfile
	printf " ####################\n############################################################################\n\n\n\n\n\n" &>> $logfile
	) &
done
wait # we ABSOLUTELY need a wait within the brackets, and a "&" outside of it in order to ensure the last echo to wait for all commands before ending the script
) &



(
tech=dbscan
output_dir=../outputs/$tech/

# titles=("PCA" "ICA" "LSA" "tSNE" "UMAP" "original_data" )
minpts=(3 3 3 3 3 3 3)
eps=(20 20 20 20 20 20 20)

# sanity check to see if we have the right number of parameters supplied.
if [ ${#minpts[@]} == ${#eps[@]} ] && [ ${#minpts[@]} == ${#titles[@]} ]; then 

	for i in $range; do
		(
		input_dir=${directories[$i]}
		logfile=logs/4_${tech}_${titles[$i]}.log

		printf "############################################################################\n################### " &>> $logfile
		echo -n START: `date` &>> $logfile
		start=`date +%s`
		printf " ###################\n############################################################################\n\n" &>> $logfile

		python ../4_Evaluation/sca_dbscan.py  --title ${titles[$i]} --verbosity 3 --eps ${eps[$i]} --min_samples ${minpts[$i]} --input_dir $input_dir --output_dir $output_dir |& tee -a $logfile
		
		end=`date +%s`
		printf "\n$tech took %d minutes\n" `echo "($end-$start)/60" | bc` &>> $logfile
		printf "\n################### " &>> $logfile
		echo -n DONE: `date` &>> $logfile
		printf " ####################\n############################################################################\n\n\n\n\n\n" &>> $logfile
		) &
	done
	wait # we ABSOLUTELY need a wait within the brackets, and a "&" outside of it in order to ensure the last echo to wait for all commands before ending the script
else
	echo `date` |& tee -a $errfile
	echo "ERROR ERROR ERROR ERROR ERROR ERROR. ERROR ERROR ERROR ERROR" |& tee -a $errfile
	echo `date`
	echo "ERROR: Incorrect number of parameters supplied. DBScan could not run" |& tee -a $errfile
	echo "" &>> $errfile
fi
) &



wait
echo "All Done - " `date`






