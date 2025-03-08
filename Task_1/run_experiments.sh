#!/bin/bash

# Directory for storing results
RESULTS_DIR="congestion_control_results"
mkdir -p $RESULTS_DIR

# List of congestion control algorithms to test
CONGESTION_SCHEMES=("highspeed" "yeah" "bbr")

# Function to run a single experiment
run_experiment() {
    local option=$1
    local congestion=$2
    local case=$3
    local loss=$4
    
    # Create directory for this experiment
    local exp_dir="${RESULTS_DIR}/${option}_${congestion}"
    if [ ! -z "$case" ]; then
        exp_dir="${exp_dir}_${case}"
    fi
    if [ ! -z "$loss" ]; then
        exp_dir="${exp_dir}_loss${loss}"
    fi
    mkdir -p $exp_dir
    
    echo "Running experiment: Option $option, Congestion $congestion"
    if [ ! -z "$case" ]; then
        echo "  Case: $case"
    fi
    if [ ! -z "$loss" ]; then
        echo "  Link Loss: $loss%"
    fi
    
    # Set the pcap file name
    local pcap_file="${exp_dir}/capture.pcap"
    
    # Start tcpdump to capture traffic
    echo "Starting packet capture..."
    sudo tcpdump -i any tcp -w $pcap_file &
    TCPDUMP_PID=$!
    
    # Run mininet experiment
    if [ -z "$case" ] && [ -z "$loss" ]; then
        sudo python3 mininet_topology.py --option=$option --congestion=$congestion
    elif [ -z "$loss" ]; then
        sudo python3 mininet_topology.py --option=$option --congestion=$congestion --case=$case
    else
        sudo python3 mininet_topology.py --option=$option --congestion=$congestion --case=$case --loss=$loss
    fi
    
    # Give some time for tcpdump to finish writing
    sleep 5
    
    # Kill tcpdump
    sudo kill $TCPDUMP_PID
    
    # Analyze the captured traffic
    echo "Analyzing traffic..."
    sudo python3 traffic_analyzer.py --pcap=$pcap_file --congestion=$congestion --output_dir=$exp_dir
    
    echo "Experiment completed. Results saved to $exp_dir"
    echo "----------------------------------------"
}

# Make sure correct modules are loaded for congestion control
echo "Loading TCP congestion control modules..."
for scheme in "${CONGESTION_SCHEMES[@]}"; do
    sudo modprobe tcp_$scheme
done

# Part (a): Single client on h1
echo "Running Part (a) experiments..."
for scheme in "${CONGESTION_SCHEMES[@]}"; do
    run_experiment "a" $scheme
done

# Part (b): Staggered clients on h1, h3, h4
echo "Running Part (b) experiments..."
for scheme in "${CONGESTION_SCHEMES[@]}"; do
    run_experiment "b" $scheme
done

# Part (c): Different bandwidth configurations
echo "Running Part (c) experiments..."
for scheme in "${CONGESTION_SCHEMES[@]}"; do
    # Case 1: Link S2-S4 with client on h3
    run_experiment "c" $scheme "1"
    
    # Case 2a: Link S1-S4 with clients on h1, h2
    run_experiment "c" $scheme "2a"
    
    # Case 2b: Link S1-S4 with clients on h1, h3
    run_experiment "c" $scheme "2b"
    
    # Case 2c: Link S1-S4 with clients on h1, h3, h4
    run_experiment "c" $scheme "2c"
done

# Part (d): Link loss configurations
echo "Running Part (d) experiments..."
for scheme in "${CONGESTION_SCHEMES[@]}"; do
    for loss in 1 5; do
        # Case 1: Link S2-S4 with client on h3
        run_experiment "d" $scheme "1" $loss
        
        # Case 2a: Link S1-S4 with clients on h1, h2
        run_experiment "d" $scheme "2a" $loss
        
        # Case 2b: Link S1-S4 with clients on h1, h3
        run_experiment "d" $scheme "2b" $loss
        
        # Case 2c: Link S1-S4 with clients on h1, h3, h4
        run_experiment "d" $scheme "2c" $loss
    done
done

echo "All experiments completed!"
