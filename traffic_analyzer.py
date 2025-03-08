#!/usr/bin/env python3

import argparse
import os
import subprocess
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from scapy.all import rdpcap, TCP

def capture_traffic(interface, output_file, duration):
    """Capture network traffic using tcpdump"""
    cmd = f"tcpdump -i {interface} -w {output_file} -G {duration} -W 1"
    subprocess.run(cmd, shell=True)

def analyze_throughput(pcap_file):
    """Analyze throughput from pcap file"""
    packets = rdpcap(pcap_file)
    
    # Initialize data structures
    timestamps = []
    packet_sizes = []
    
    # Extract timestamps and packet sizes for TCP packets
    for packet in packets:
        if TCP in packet:
            timestamps.append(float(packet.time))
            packet_sizes.append(len(packet))
    
    if not timestamps:
        print("No TCP packets found in the capture file.")
        return None, None
    
    # Convert to numpy arrays for efficient operations
    timestamps = np.array(timestamps)
    packet_sizes = np.array(packet_sizes)
    
    # Normalize timestamps to start from 0
    timestamps = timestamps - timestamps[0]
    
    # Calculate throughput over time (1-second intervals)
    max_time = int(timestamps[-1]) + 1
    throughput = []
    time_points = []
    
    for i in range(max_time):
        mask = (timestamps >= i) & (timestamps < i+1)
        bytes_in_interval = sum(packet_sizes[mask])
        throughput.append(bytes_in_interval * 8 / 1e6)  # Convert bytes to megabits
        time_points.append(i)
    
    return time_points, throughput

def calculate_goodput(pcap_file):
    """Calculate goodput (application-level throughput)"""
    packets = rdpcap(pcap_file)
    
    # Extract payload sizes and timestamps
    payload_sizes = []
    timestamps = []
    
    for packet in packets:
        if TCP in packet and packet[TCP].payload:
            payload_sizes.append(len(packet[TCP].payload))
            timestamps.append(float(packet.time))
    
    if not timestamps:
        print("No TCP packets with payload found in the capture file.")
        return 0
    
    # Calculate goodput (total payload bytes / total time)
    total_bytes = sum(payload_sizes)
    total_time = max(timestamps) - min(timestamps)
    
    if total_time == 0:
        return 0
    
    goodput = (total_bytes * 8) / total_time / 1e6  # in Mbps
    return goodput

def calculate_packet_loss(pcap_file):
    """Calculate packet loss rate from pcap file"""
    packets = rdpcap(pcap_file)
    
    # Extract sequence numbers and acknowledgment numbers
    seq_nums = {}
    ack_nums = {}
    
    for packet in packets:
        if TCP in packet:
            if packet[TCP].flags & 0x02:  # SYN flag
                seq_nums[packet[TCP].seq] = 1
            if packet[TCP].flags & 0x10:  # ACK flag
                ack_nums[packet[TCP].ack] = 1
    
    # Count unique sequence numbers and acknowledgments
    unique_seqs = len(seq_nums)
    unique_acks = len(ack_nums)
    
    if unique_seqs == 0:
        return 0
    
    # Calculate packet loss rate
    loss_rate = 1 - (unique_acks / unique_seqs)
    return max(0, loss_rate)  # Ensure non-negative

def find_max_window_size(pcap_file):
    """Find maximum window size from pcap file"""
    packets = rdpcap(pcap_file)
    
    # Extract window sizes
    window_sizes = []
    timestamps = []
    
    for packet in packets:
        if TCP in packet:
            # Default window scaling factor
            wscale_factor = 0
            
            # Ensure packet[TCP].options exists and is a list
            if hasattr(packet[TCP], "options") and isinstance(packet[TCP].options, list):
                for option in packet[TCP].options:
                    if isinstance(option, tuple) and option[0] == "WScale":
                        wscale_factor = option[1]  # Extract window scaling value
            
            # Calculate actual window size
            window_size = packet[TCP].window * (2 ** wscale_factor)
            window_sizes.append(window_size)
            timestamps.append(float(packet.time))
    
    if not window_sizes:
        print("No TCP packets found in the capture file.")
        return 0, [], []
    
    # Normalize timestamps to start from 0
    timestamps = np.array(timestamps) - timestamps[0]
    
    max_window = max(window_sizes) if window_sizes else 0
    return max_window, timestamps, window_sizes

def plot_throughput(time_points, throughput, congestion_scheme, output_file):
    """Plot throughput over time"""
    plt.figure(figsize=(10, 6))
    plt.plot(time_points, throughput)
    plt.xlabel('Time (seconds)')
    plt.ylabel('Throughput (Mbps)')
    plt.title(f'Throughput over Time - {congestion_scheme}')
    plt.grid(True)
    plt.savefig(output_file)
    plt.close()

def plot_window_size(timestamps, window_sizes, congestion_scheme, output_file):
    """Plot window size over time"""
    plt.figure(figsize=(10, 6))
    plt.plot(timestamps, window_sizes)
    plt.xlabel('Time (seconds)')
    plt.ylabel('Window Size (bytes)')
    plt.title(f'Window Size over Time - {congestion_scheme}')
    plt.grid(True)
    plt.savefig(output_file)
    plt.close()

def main():
    parser = argparse.ArgumentParser(description='Analyze TCP traffic data')
    parser.add_argument('--pcap', type=str, required=True,
                        help='Path to the pcap file')
    parser.add_argument('--congestion', type=str, choices=['highspeed', 'yeah', 'bbr'], required=True,
                        help='TCP congestion control algorithm')
    parser.add_argument('--output_dir', type=str, default='results',
                        help='Directory to save results')
    
    args = parser.parse_args()
    
    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Analyze throughput
    time_points, throughput = analyze_throughput(args.pcap)
    if time_points and throughput:
        plot_throughput(time_points, throughput, args.congestion, 
                        f"{args.output_dir}/throughput_{args.congestion}.png")
    
    # Calculate goodput
    goodput = calculate_goodput(args.pcap)
    print(f"Goodput: {goodput:.2f} Mbps")
    
    # Calculate packet loss rate
    loss_rate = calculate_packet_loss(args.pcap)
    print(f"Packet Loss Rate: {loss_rate:.4f}")
    
    # Find maximum window size
    max_window, window_timestamps, window_sizes = find_max_window_size(args.pcap)
    if len(window_timestamps) > 0 and len(window_sizes) > 0:
        plot_window_size(window_timestamps, window_sizes, args.congestion,
                        f"{args.output_dir}/window_size_{args.congestion}.png")
    
    print(f"Maximum Window Size: {max_window} bytes")
    
    # Save summary to a file
    with open(f"{args.output_dir}/summary_{args.congestion}.txt", 'w') as f:
        f.write(f"Congestion Control: {args.congestion}\n")
        f.write(f"Goodput: {goodput:.2f} Mbps\n")
        f.write(f"Packet Loss Rate: {loss_rate:.4f}\n")
        f.write(f"Maximum Window Size: {max_window} bytes\n")

if __name__ == "__main__":
    main()
