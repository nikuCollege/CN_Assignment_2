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

