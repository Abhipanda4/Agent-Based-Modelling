#!/bin/bash

sed -ie "s/MEAN_RESERVE = .*/MEAN_RESERVE = ${1}/g" config.py
declare -a intra_levels=("low" "high")
declare -a inter_levels=("low" "high")

LOW=0.2
HIGH=0.8

for intra in "${intra_levels[@]}"
do
    for inter in "${inter_levels[@]}"
    do
        if [ ${intra} = "low" ]
        then
            sed -ie "s/INTRA_COMMUNICATION_PROB = .*/INTRA_COMMUNICATION_PROB = ${LOW}/g" config.py
        else
            sed -ie "s/INTRA_COMMUNICATION_PROB = .*/INTRA_COMMUNICATION_PROB = ${HIGH}/g" config.py
        fi

        if [ ${inter} = "low" ]
        then
            sed -ie "s/INTER_COMMUNICATION_PROB = .*/INTER_COMMUNICATION_PROB = ${LOW}/g" config.py
        else
            sed -ie "s/INTER_COMMUNICATION_PROB = .*/INTER_COMMUNICATION_PROB = ${HIGH}/g" config.py
        fi

        # adjust dir name
        dir_name="$intra-$inter"
        sed -ie "s/comm_level = .*/comm_level = \'${dir_name}\'/g" plot_graphs.py

        # run the actual program
        python main.py
        python plot_graphs.py
    done
done
