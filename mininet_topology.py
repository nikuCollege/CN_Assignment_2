#!/usr/bin/env python3

from mininet.net import Mininet
from mininet.node import Controller, OVSKernelSwitch
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.log import setLogLevel
import argparse
import time
import os
import sys

def create_network(option, congestion_control, link_loss=0):
    """Create the Mininet topology based on the specified option."""
    
    # Create network with OVS switches
    net = Mininet(controller=Controller, switch=OVSKernelSwitch, link=TCLink)
    
    # Add controller
    c0 = net.addController('c0')
    
    # Add switches
    s1 = net.addSwitch('s1')
    s2 = net.addSwitch('s2')
    s3 = net.addSwitch('s3')
    s4 = net.addSwitch('s4')
    
    # Add hosts
    h1 = net.addHost('h1')
    h2 = net.addHost('h2')
    h3 = net.addHost('h3')
    h4 = net.addHost('h4')
    h5 = net.addHost('h5')
    h6 = net.addHost('h6')
    h7 = net.addHost('h7')
    
    # Default bandwidth for links (10Mbps)
    bw_default = 10
    
    # Connect hosts to switches
    net.addLink(h1, s1)
    net.addLink(h2, s1)
    net.addLink(h3, s2)
    net.addLink(h4, s2)
    net.addLink(h5, s3)
    net.addLink(h6, s3)
    net.addLink(h7, s4)
    
    # Connect switches based on option
    if option == 'a' or option == 'b':
        # Default topology for options a and b
        net.addLink(s1, s2)
        net.addLink(s2, s3)
        net.addLink(s3, s4)
    elif option == 'c' or option == 'd':
        # Bandwidth configuration for options c and d
        link_s1_s2 = net.addLink(s1, s2, bw=100)
        
        # For option d, add link loss parameter to s2-s3
        if option == 'd':
            link_s2_s3 = net.addLink(s2, s3, bw=50, loss=link_loss)
        else:
            link_s2_s3 = net.addLink(s2, s3, bw=50)
            
        link_s3_s4 = net.addLink(s3, s4, bw=100)
        
        # Additional links for options c and d
        net.addLink(s2, s4)  # Link S2-S4
        net.addLink(s1, s4)  # Link S1-S4
    
    # Start network
    net.build()
    c0.start()
    s1.start([c0])
    s2.start([c0])
    s3.start([c0])
    s4.start([c0])
    
    # Configure TCP congestion control algorithm for all hosts
    for host in net.hosts:
        host.cmd(f'sysctl -w net.ipv4.tcp_congestion_control={congestion_control}')
    
    # Start iperf3 server on h7
    h7.cmd('iperf3 -s -p 5201 &')
    
    # Run experiments based on option
    if option == 'a':
        # Single client on h1
        h1.cmd(f'iperf3 -c {h7.IP()} -p 5201 -b 10M -P 10 -t 150 -C {congestion_control} &')
        print(f"Started client on h1 connecting to server at {h7.IP()}")
        
    elif option == 'b':
        # Staggered clients on h1, h3, h4
        h1.cmd(f'iperf3 -c {h7.IP()} -p 5201 -b 10M -P 10 -t 150 -C {congestion_control} &')
        print(f"Started client on h1 connecting to server at {h7.IP()}")
        
        time.sleep(15)
        h3.cmd(f'iperf3 -c {h7.IP()} -p 5201 -b 10M -P 10 -t 120 -C {congestion_control} &')
        print(f"Started client on h3 connecting to server at {h7.IP()}")
        
        time.sleep(15)
        h4.cmd(f'iperf3 -c {h7.IP()} -p 5201 -b 10M -P 10 -t 90 -C {congestion_control} &')
        print(f"Started client on h4 connecting to server at {h7.IP()}")
        
    elif option == 'c':
        # Case 1: Link S2-S4 with client on h3
        if len(sys.argv) >= 4 and sys.argv[3] == '1':
            h3.cmd(f'iperf3 -c {h7.IP()} -p 5201 -b 10M -P 10 -t 150 -C {congestion_control} &')
            print(f"Started client on h3 connecting to server at {h7.IP()}")
            
        # Case 2a: Link S1-S4 with clients on h1, h2
        elif len(sys.argv) >= 4 and sys.argv[3] == '2a':
            h1.cmd(f'iperf3 -c {h7.IP()} -p 5201 -b 10M -P 10 -t 150 -C {congestion_control} &')
            h2.cmd(f'iperf3 -c {h7.IP()} -p 5201 -b 10M -P 10 -t 150 -C {congestion_control} &')
            print(f"Started clients on h1 and h2 connecting to server at {h7.IP()}")
            
        # Case 2b: Link S1-S4 with clients on h1, h3
        elif len(sys.argv) >= 4 and sys.argv[3] == '2b':
            h1.cmd(f'iperf3 -c {h7.IP()} -p 5201 -b 10M -P 10 -t 150 -C {congestion_control} &')
            h3.cmd(f'iperf3 -c {h7.IP()} -p 5201 -b 10M -P 10 -t 150 -C {congestion_control} &')
            print(f"Started clients on h1 and h3 connecting to server at {h7.IP()}")
            
        # Case 2c: Link S1-S4 with clients on h1, h3, h4
        elif len(sys.argv) >= 4 and sys.argv[3] == '2c':
            h1.cmd(f'iperf3 -c {h7.IP()} -p 5201 -b 10M -P 10 -t 150 -C {congestion_control} &')
            h3.cmd(f'iperf3 -c {h7.IP()} -p 5201 -b 10M -P 10 -t 150 -C {congestion_control} &')
            h4.cmd(f'iperf3 -c {h7.IP()} -p 5201 -b 10M -P 10 -t 150 -C {congestion_control} &')
            print(f"Started clients on h1, h3, and h4 connecting to server at {h7.IP()}")
            
    elif option == 'd':
        # Same as option c but with link loss configured
        # Case 1: Link S2-S4 with client on h3
        if len(sys.argv) >= 4 and sys.argv[3] == '1':
            h3.cmd(f'iperf3 -c {h7.IP()} -p 5201 -b 10M -P 10 -t 150 -C {congestion_control} &')
            print(f"Started client on h3 connecting to server at {h7.IP()}")
            
        # Case 2a: Link S1-S4 with clients on h1, h2
        elif len(sys.argv) >= 4 and sys.argv[3] == '2a':
            h1.cmd(f'iperf3 -c {h7.IP()} -p 5201 -b 10M -P 10 -t 150 -C {congestion_control} &')
            h2.cmd(f'iperf3 -c {h7.IP()} -p 5201 -b 10M -P 10 -t 150 -C {congestion_control} &')
            print(f"Started clients on h1 and h2 connecting to server at {h7.IP()}")
            
        # Case 2b: Link S1-S4 with clients on h1, h3
        elif len(sys.argv) >= 4 and sys.argv[3] == '2b':
            h1.cmd(f'iperf3 -c {h7.IP()} -p 5201 -b 10M -P 10 -t 150 -C {congestion_control} &')
            h3.cmd(f'iperf3 -c {h7.IP()} -p 5201 -b 10M -P 10 -t 150 -C {congestion_control} &')
            print(f"Started clients on h1 and h3 connecting to server at {h7.IP()}")
            
        # Case 2c: Link S1-S4 with clients on h1, h3, h4
        elif len(sys.argv) >= 4 and sys.argv[3] == '2c':
            h1.cmd(f'iperf3 -c {h7.IP()} -p 5201 -b 10M -P 10 -t 150 -C {congestion_control} &')
            h3.cmd(f'iperf3 -c {h7.IP()} -p 5201 -b 10M -P 10 -t 150 -C {congestion_control} &')
            h4.cmd(f'iperf3 -c {h7.IP()} -p 5201 -b 10M -P 10 -t 150 -C {congestion_control} &')
            print(f"Started clients on h1, h3, and h4 connecting to server at {h7.IP()}")
    
    # Start CLI
    # CLI(net)
    
    # Stop network
    net.stop()

if __name__ == '__main__':
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Run TCP congestion control experiments')
    parser.add_argument('--option', type=str, choices=['a', 'b', 'c', 'd'], required=True,
                        help='Experiment option to run')
    parser.add_argument('--congestion', type=str, choices=['highspeed', 'yeah', 'bbr'], required=True,
                        help='TCP congestion control algorithm')
    parser.add_argument('--case', type=str, choices=['1', '2a', '2b', '2c'], 
                        help='Specific test case for options c and d')
    parser.add_argument('--loss', type=float, default=0,
                        help='Link loss percentage for option d (1 or 5)')
    
    args = parser.parse_args()
    
    # Set log level
    setLogLevel('info')
    
    # Run the network
    create_network(args.option, args.congestion, args.loss)
