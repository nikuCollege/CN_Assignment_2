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

def create_network(option, congestion_control, link_loss=0, case=None):
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

    # Connect hosts to switches
    net.addLink(h1, s1)
    net.addLink(h2, s1)
    net.addLink(h3, s2)
    net.addLink(h4, s2)
    net.addLink(h5, s3)
    net.addLink(h6, s3)
    net.addLink(h7, s4)

    # Configure switch connections based on the option
    if option in ['a', 'b']:
        net.addLink(s1, s2)
        net.addLink(s2, s3)
        net.addLink(s3, s4)
    
    elif option in ['c', 'd']:
        print("Entered option c or d!")
        net.addLink(s1, s2, bw=100)
        
        
        # Case-specific link configurations
        if case == '1':
            net.addLink(s2, s4, bw=100)
            print("Running Case 1: Enabled link S2-S4, disabled S1-S4")
        elif case in ['2a', '2b', '2c']:
            net.addLink(s1, s4, bw=100)
            print("Running Case 2: Enabled link S1-S4, disabled S2-S4")
        
        if option == 'd':
            net.addLink(s2, s3, bw=50, loss=link_loss)
        else:
            print("entered this!")
            net.addLink(s2, s3, bw=50)

        print("atleast reached here!")
        net.addLink(s3, s4, bw=100)
            


    # Start network
    net.build()
    c0.start()
    s1.start([c0])
    s2.start([c0])
    s3.start([c0])
    s4.start([c0])

    #Add openflow rules to forward traffic between s2 and s4
    # s2.cmd('ovs-ofctl add-flow s2 in_port=2,actions=output:3')
    # s4.cmd('ovs-ofctl add-flow s4 in_port=1,actions=output:2')

    # Configure TCP congestion control algorithm for all hosts
    for host in net.hosts:
        if host != h7:  #apply congestion control only on hosts
            host.cmd(f'sysctl -w net.ipv4.tcp_congestion_control={congestion_control}')
    
    
    print ("Starting iperf3 server on h7...")
    h7.cmd('iperf3 -s -p 5201 &')
    
    time.sleep(2)
    
    print ("Server started on h7")
    
    if "iperf3" in h7.cmd("ps aux"):
        print("iperf3 server is running on h7")
    
    else:
        print("Error: iperf3 server is not running on h7. Restarting...")
        h7.cmd('iperf3 -s -p 5201 &')
        
    # print(f"sys.argv: {sys.argv}")
    
    # Run experiments based on option
    if option == 'a':
        # Single client on h1
        print("Starting iperf3 client on h1...")
        h1.cmd(f'timeout 155 iperf3 -c {h7.IP()} -p 5201 -b 10M -P 10 -t 150 -C {congestion_control}')
        # print("iperf3 client output:\n", output)
        print(f"Started client on h1 connecting to {h7.IP()}")
    
    elif option == 'b':
        # Staggered clients on h1, h3, h4
        h1.cmd(f'timeout 155 iperf3 -c {h7.IP()} -p 5201 -b 10M -P 10 -t 150 -C {congestion_control} &')
        print(f"Started client on h1 connecting to {h7.IP()}")


        time.sleep(15)
        h3.cmd(f'timeout 125 iperf3 -c {h7.IP()} -p 5201 -b 10M -P 10 -t 120 -C {congestion_control} &')
        print(f"Started client on h3 connecting to server at {h7.IP()}")
        
        time.sleep(15)
        h4.cmd(f'timeout 95 iperf3 -c {h7.IP()} -p 5201 -b 10M -P 10 -t 90 -C {congestion_control}&')
        print(f"Started client on h4 connecting to server at {h7.IP()}")
        time.sleep(150)
        
    elif option == 'c':
        # Case 1: Link S2-S4 with client on h3
        print( "entered c " )
        print("Checking if iperf3 server is running on h7...")
        print(h7.cmd("ps aux | grep '[i]perf3'"))  
        # Check if iperf3 server process is running

        #if len(sys.argv) >= 4 and sys.argv[3] == '1':
        if args.case and args.case == '1':
            h3.cmd(f'timeout 155 iperf3 -c {h7.IP()} -p 5201 -b 10M -P 10 -t 150 -C {congestion_control} &')
            print(f"Started client on h3 connecting to server at {h7.IP()}")
            time.sleep(150)
            
        # Case 2a: Link S1-S4 with clients on h1, h2
        elif args.case and args.case == '2a':
            h1.cmd(f'timeout 155 iperf3 -c {h7.IP()} -p 5201 -b 10M -P 10 -t 150 -C {congestion_control} &')
            print(f"Started client on h1 connecting to {h7.IP()}")
            h2.cmd(f'timeout 155 iperf3 -c {h7.IP()} -p 5201 -b 10M -P 10 -t 150 -C {congestion_control} &')
            print(f"Started client on h2 connecting to {h7.IP()}")
            time.sleep(150)
            
        # Case 2b: Link S1-S4 with clients on h1, h3
        elif args.case and args.case == '2b':
            h1.cmd(f'timeout 155 iperf3 -c {h7.IP()} -p 5201 -b 10M -P 10 -t 150 -C {congestion_control} &')
            print(f"Started client on h1 connecting to {h7.IP()}")
            h3.cmd(f'timeout 155 iperf3 -c {h7.IP()} -p 5201 -b 10M -P 10 -t 150 -C {congestion_control} &')
            print(f"Started client on h3 connecting to {h7.IP()}")
            time.sleep(150)
            
        # Case 2c: Link S1-S4 with clients on h1, h3, h4
        elif args.case and args.case == '2c':
            h1.cmd(f'timeout 155 iperf3 -c {h7.IP()} -p 5201 -b 10M -P 10 -t 150 -C {congestion_control} &')
            print(f"Started client on h1 connecting to {h7.IP()}")
            h3.cmd(f'timeout 155 iperf3 -c {h7.IP()} -p 5201 -b 10M -P 10 -t 150 -C {congestion_control} &')
            print(f"Started client on h3 connecting to {h7.IP()}")
            h4.cmd(f'timeout 155 iperf3 -c {h7.IP()} -p 5201 -b 10M -P 10 -t 150 -C {congestion_control} &')
            print(f"Started client on h4 connecting to {h7.IP()}")
            time.sleep(150)
            
    elif option == 'd':
        # Same as option c but with link loss configured
        # Case 1: Link S2-S4 with client on h3
        if args.case and args.case == '1':
            h3.cmd(f'timeout 155 iperf3 -c {h7.IP()} -p 5201 -b 10M -P 10 -t 150 -C {congestion_control} &')
            print(f"Started client on h3 connecting to server at {h7.IP()}")
            time.sleep(150)
            
        # Case 2a: Link S1-S4 with clients on h1, h2
        elif args.case and args.case == '2a':
            h1.cmd(f'timeout 155 iperf3 -c {h7.IP()} -p 5201 -b 10M -P 10 -t 150 -C {congestion_control} &')
            print(f"Started client on h1 connecting to {h7.IP()}")
            h2.cmd(f'timeout 155 iperf3 -c {h7.IP()} -p 5201 -b 10M -P 10 -t 150 -C {congestion_control} &')
            print(f"Started client on h2 connecting to {h7.IP()}")
            time.sleep(150)
            
        # Case 2b: Link S1-S4 with clients on h1, h3
        elif args.case and args.case == '2b':
            h1.cmd(f'timeout 155 iperf3 -c {h7.IP()} -p 5201 -b 10M -P 10 -t 150 -C {congestion_control} &')
            print(f"Started client on h1 connecting to {h7.IP()}")
            h3.cmd(f'timeout 155 iperf3 -c {h7.IP()} -p 5201 -b 10M -P 10 -t 150 -C {congestion_control} &')
            print(f"Started client on h3 connecting to {h7.IP()}")
            time.sleep(150)
            
        # Case 2c: Link S1-S4 with clients on h1, h3, h4
        elif args.case and args.case == '2c':
            h1.cmd(f'timeout 155 iperf3 -c {h7.IP()} -p 5201 -b 10M -P 10 -t 150 -C {congestion_control} &')
            print(f"Started client on h1 connecting to {h7.IP()}")
            h3.cmd(f'timeout 155 iperf3 -c {h7.IP()} -p 5201 -b 10M -P 10 -t 150 -C {congestion_control} &')
            print(f"Started client on h3 connecting to {h7.IP()}")
            h4.cmd(f'timeout 155 iperf3 -c {h7.IP()} -p 5201 -b 10M -P 10 -t 150 -C {congestion_control} &')
            print(f"Started client on h4 connecting to {h7.IP()}")
            time.sleep(150)
    
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
    create_network(args.option, args.congestion, args.loss, args.case)
    

