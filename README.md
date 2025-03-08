This assignment includes three major tasks:
1. **TCP Congestion Control Experiments** 
2. **SYN Flood Attack Implementation & Mitigation** 
3. **Analysis of Nagle’s Algorithm on TCP Performance** 

# Task 1: TCP Congestion Control Experiments with Mininet

This repository contains scripts to evaluate different TCP congestion control algorithms (HighSpeed, YeAH, and BBR) under various network conditions using Mininet.

## Prerequisites

- Linux operating system (Ubuntu recommended)
- Python 3.x
- Git

## Installation

1. **Clone this repository**:
   ```bash
   git clone https://github.com/yourusername/tcp-congestion-control
   cd tcp-congestion-control
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


## For ease. we have created a "Results" folder listing teh summary of all the experiments.
It doesn't contain the "pcap files" due to memory issues on github.

## File Structure

- `mininet_topology.py`: Creates the network topologies and runs the experiments
- `run_experiments.sh`: Main script that automates all experiments
- `traffic_analyzer.py`: Analyzes captured traffic and generates graphs


# Task 2: SYN Flood Attack Implementation & Mitigation

## Overview
This project focuses on the implementation and mitigation of a TCP SYN flood attack in a controlled, virtual environment. The objective is to simulate an attack, analyze its impact on TCP connections, and then apply mitigation techniques to observe the difference.

## Task Breakdown
### **Task 1: Implementation of SYN Flood Attack**
In this part, we modify the server's Linux kernel parameters to make it more vulnerable to a SYN flood attack. Then, we generate legitimate traffic followed by a SYN flood attack, capture the network traffic, and analyze the results.

### **Task 2: SYN Flood Attack Mitigation**
After performing the attack, we implement mitigation techniques such as SYN cookies and rate limiting. The same attack experiment is repeated, and the results are compared with the initial scenario.

---

## **Environment Setup**
We use two virtual machines:
- **Attacker:** Kali Linux (IP: 192.168.200.133)
- **Victim Server:** Any Linux-based VM or host

### **Required Tools**
Install necessary tools on both machines:
```bash
sudo apt update && sudo apt install tcpdump tshark hping3 iproute2 net-tools
```

---

## **Task 1: Implementing SYN Flood Attack**

### **1. Configuring the Victim Server**
To make the server vulnerable, we modify kernel parameters:
```bash
sudo sysctl -w net.ipv4.tcp_max_syn_backlog=4096
sudo sysctl -w net.ipv4.tcp_syncookies=0
sudo sysctl -w net.ipv4.tcp_synack_retries=2
```
To make these changes persistent:
```bash
echo "net.ipv4.tcp_max_syn_backlog=4096" | sudo tee -a /etc/sysctl.conf
echo "net.ipv4.tcp_syncookies=0" | sudo tee -a /etc/sysctl.conf
echo "net.ipv4.tcp_synack_retries=2" | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```

### **2. Running the TCP Server**
Using Netcat:
```bash
nc -l -p 4999
```
Or using Python:
```python
import socket

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("0.0.0.0", 4999))
server.listen(5)
print("Server listening on port 4999...")

while True:
    conn, addr = server.accept()
    print(f"Connection from {addr}")
    conn.close()
```

### **3. Capturing Network Traffic**
On the attacker machine, start capturing packets:
```bash
sudo tcpdump -i eth0 port 4999 -w syn_flood.pcap
```

### **4. Generating Legitimate Traffic**
```bash
hping3 -S -p 4999 -c 50 192.168.200.133
```
Wait 20 seconds before launching the attack.

### **5. Launching the SYN Flood Attack**
```bash
hping3 -S -p 4999 --flood 192.168.200.133
```
Let it run for 100 seconds, then stop it with `Ctrl+C`.

### **6. Stopping Traffic Capture**
```bash
sudo pkill -f tcpdump
```

### **7. Analyzing the PCAP File**
Extract unique connection details:
```bash
tshark -r syn_flood.pcap -Y "tcp.flags.syn==1" -T fields -e ip.src -e ip.dst -e tcp.srcport -e tcp.dstport -e frame.time_epoch > connections.txt
```
Extract connection closures (FIN-ACK or RESET packets):
```bash
tshark -r syn_flood.pcap -Y "tcp.flags.reset==1 || tcp.flags.fin==1" -T fields -e ip.src -e ip.dst -e tcp.srcport -e tcp.dstport -e frame.time_epoch > closures.txt
```

### **8. Visualizing the Attack Impact**
A Python script processes the data and generates graphs showing connection durations before, during, and after the attack.

---

## **Task 2: SYN Flood Mitigation**
### **1. Applying Mitigation Techniques**

#### **Enabling SYN Cookies**
```bash
sudo sysctl -w net.ipv4.tcp_syncookies=1
```

#### **Rate Limiting SYN Packets**
```bash
sudo iptables -A INPUT -p tcp --syn -m limit --limit 10/s --limit-burst 20 -j ACCEPT
sudo iptables -A INPUT -p tcp --syn -j DROP
```

#### **Dropping Invalid Packets**
```bash
sudo iptables -A INPUT -m state --state INVALID -j DROP
```

### **2. Re-running the Experiment**
The same attack is performed again, and the results are analyzed.

---

## **Results & Analysis**
The PCAP files are analyzed to extract connection start times and durations. A Python script processes the data and generates:
- **Scatter plot** of connection duration vs. start time
- **Box plot** comparing connection durations before, during, and after attack

### **Key Observations:**
- Without mitigation, many connections fail, or their duration is significantly reduced.
- With mitigation, the system remains more resilient, handling connections more effectively.

---

## **Deliverables**
- `syn_flood.pcap` (Captured network traffic)
- `syn_flood_analysis.png` (Graph: Connection Duration vs. Start Time)
- `connection_durations_by_period.png` (Graph: Boxplot Comparison)
- Wireshark screenshots (showing attack success & mitigation effectiveness)
- Python script for data analysis

---

## **Conclusion**
This experiment successfully demonstrates the impact of a SYN flood attack and evaluates the effectiveness of mitigation strategies. The results highlight the importance of proactive security measures to protect servers from denial-of-service attacks.


# Task 3: Analysis of Nagle’s Algorithm on TCP Performance
### Task Description
For this task, a 4 KB file was transmitted over a TCP connection for a duration of ~2 minutes with a transfer rate of 40 bytes/second. The following four combinations were tested by enabling/disabling Nagle’s Algorithm and Delayed-ACK on both the client and server sides:

1. Nagle’s Algorithm enabled, Delayed-ACK enabled.
2. Nagle’s Algorithm enabled, Delayed-ACK disabled.
3. Nagle’s Algorithm disabled, Delayed-ACK enabled.
4. Nagle’s Algorithm disabled, Delayed-ACK disabled.

For each configuration, the following performance metrics were measured and compared:
- Throughput
- Goodput
- Packet loss rate
- Maximum packet size achieved

### Environment Setup
- **Client:** Windows system running `client.cpp`
- **Server:** Kali Linux VM running `server.cpp`
- **Port Used:** 4999
- **Transfer Rate:** 40 bytes/sec
- **File Size:** 4 KB

### Implementation Details
- The **client** (`client.cpp`) runs on Windows and establishes a connection with the server on the specified port. It reads a file (`file.txt`) and transmits it in chunks of 40 bytes per second.
- The **server** (`server.cpp`) listens on the same port, receives data, and prints the received bytes.
- Nagle’s Algorithm and Delayed-ACK settings were configured using `TCP_NODELAY` and `TCP_QUICKACK` socket options, respectively.

### Observations and Analysis
- The impact of enabling/disabling Nagle’s Algorithm and Delayed-ACK on throughput, goodput, packet loss rate, and maximum packet size was analyzed.
- Results were compared to understand the effect on TCP performance.

This setup helped in understanding the behavior of TCP under different conditions and analyzing how these configurations influence network efficiency.

### Additional Notes
- This task was performed using the provided `client.cpp` and `server.cpp` files.
- The **client code** was executed on Windows, while the **server code** was executed on Kali Linux VM.
- Testing was done by modifying Nagle’s Algorithm and Delayed-ACK settings on both client and server sides and measuring the corresponding network performance metrics.

