
concurrencies=(1 2 4 8 16 32 64)
samples=(1 10 100 1000 10000)
read_path="/g/g13/bay1/null_results"
DATA=my_data2.yaml


touch ${DATA}

for c in "${concurrencies[@]}"
    do
    for s in "${samples[@]}"
        do
        echo "c${c}_s${s} : " >> ${DATA}
        python3 task_script.py ${read_path}/c_$c/s_$s/*.log >> ${DATA}
        done
    done
perl -pi -e 's/ : \n/ : /g' ${DATA}
