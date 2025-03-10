# Task 1: TCP Congestion Control Experiments with Mininet

This repository contains scripts to evaluate different TCP congestion control algorithms (HighSpeed, YeAH, and BBR) under various network conditions using Mininet.

## Prerequisites

- Linux operating system (Ubuntu recommended)
- Python 3.x
- Git

## Installation

1. **Clone this repository**:
   ```bash
   git clone https://github.com/nikuCollege/CN_Assignment_2
   ```

2. **Install Mininet from source with Python 3 support**:
   ```bash
   git clone https://github.com/mininet/mininet
   cd mininet
   git checkout -b 2.3.0
   PYTHON=python3 sudo -E ./util/install.sh -a
   cd ..
   ```

3. **Install required Python packages**:
   ```bash
   sudo pip3 install matplotlib pandas numpy scapy
   ```

4. **Install tcpdump for packet capture**:
   ```bash
   sudo apt-get install -y tcpdump
   ```

5. **Ensure TCP congestion control modules are available**:
   ```bash
   sudo modprobe tcp_highspeed
   sudo modprobe tcp_yeah
   sudo modprobe tcp_bbr
   ```

## Setup

1. **Make the scripts executable**:
   ```bash
   chmod +x mininet_topology.py
   chmod +x run_experiments.sh
   chmod +x traffic_analyzer.py
   ```

2. **Create results directory**:
   ```bash
   mkdir -p congestion_control_results
   ```

## Running the Experiments

Execute the main script with sudo privileges:

```bash
sudo ./run_experiments.sh
```

This script will:
- Run all experiments with HighSpeed, YeAH, and BBR congestion control algorithms
- Capture network traffic using tcpdump
- Analyze traffic and generate graphs
- Save results to the `congestion_control_results` directory

Note: The complete execution of all experiments will take several hours.

## Experiment Structure

The experiments test the following scenarios:

- **Part (a)**: Single client on h1
- **Part (b)**: Staggered clients on h1, h3, h4
- **Part (c)**: Different bandwidth configurations with various client combinations
- **Part (d)**: Link loss configurations (1% and 5% loss) with various client combinations

## Results

After completion, results will be organized in the `congestion_control_results` directory with the following structure:

```
congestion_control_results/
├── a_highspeed/
│   ├── capture.pcap
│   ├── throughput_highspeed.png
│   ├── window_size_highspeed.png
│   └── summary_highspeed.txt
├── a_yeah/
│   ├── ...
├── a_bbr/
│   ├── ...
└── ...
```

Each experiment directory contains:
- A pcap file with captured packets
- Throughput graph (PNG)
- Window size graph (PNG) 
- Summary text file with metrics (goodput, packet loss rate, maximum window size)

## Viewing Results

To examine the results:

```bash
cd congestion_control_results
```

The PNG files can be viewed with any image viewer, and the summary text files contain the key metrics for each experiment.


## For ease, we have created a "Results" folder listing the summary of all the experiments.
It doesn't contain the "pcap files" due to memory issues on github.

## File Structure

- `mininet_topology.py`: Creates the network topologies and runs the experiments
- `run_experiments.sh`: Main script that automates all experiments
- `traffic_analyzer.py`: Analyzes captured traffic and generates graphs
