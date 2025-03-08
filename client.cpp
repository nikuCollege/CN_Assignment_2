#define _WIN32_WINNT 0x0600
#include <iostream>
#include <winsock2.h>
#include <ws2tcpip.h>  // This needs to be AFTER winsock2.h
#include <fstream>
#include <thread>      // Add for std::this_thread
#include <chrono>      // Add for std::chrono
#include <cstdio>      // For perror

#pragma comment(lib, "ws2_32.lib")

#define SERVER_IP "192.168.200.133"  // Change this to your Kali Linux IP
#define PORT 4999
#define FILE_PATH "file.txt"
#define BUFFER_SIZE 40
#define DELAY_MS 1000  // 40 bytes/sec = 1 second delay per 40 bytes

bool NAGLES_ALGORITHM = false;  // Set to false to disable Nagle's Algorithm

int main() {
    // Initialize Winsock
    WSADATA wsaData;
    int result = WSAStartup(MAKEWORD(2, 2), &wsaData);
    if (result != 0) {
        std::cerr << "WSAStartup failed with error: " << result << std::endl;
        return 1;
    }

    // Create socket
    SOCKET sock = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
    if (sock == INVALID_SOCKET) {
        std::cerr << "Socket creation failed with error: " << WSAGetLastError() << std::endl;
        WSACleanup();
        return 1;
    }

    // Disable Nagle's Algorithm if needed
    if (!NAGLES_ALGORITHM) {
        int flag = 1;
        if (setsockopt(sock, IPPROTO_TCP, TCP_NODELAY, (char*)&flag, sizeof(flag)) == SOCKET_ERROR) {
            std::cerr << "setsockopt failed with error: " << WSAGetLastError() << std::endl;
            closesocket(sock);
            WSACleanup();
            return 1;
        }
    }

    // Set up server address
    sockaddr_in serverAddr{};
    serverAddr.sin_family = AF_INET;
    serverAddr.sin_port = htons(PORT);
    
    // Convert IP address using different method to avoid inet_pton issues
    serverAddr.sin_addr.s_addr = inet_addr(SERVER_IP);
    if (serverAddr.sin_addr.s_addr == INADDR_NONE) {
        std::cerr << "Invalid IP address" << std::endl;
        closesocket(sock);
        WSACleanup();
        return 1;
    }

    // Connect to server
    if (connect(sock, (sockaddr*)&serverAddr, sizeof(serverAddr)) == SOCKET_ERROR) {
        std::cerr << "Connection failed with error: " << WSAGetLastError() << std::endl;
        closesocket(sock);
        WSACleanup();
        return 1;
    }

    std::cout << "Connected to server successfully!\n";

    // Open file
    std::ifstream file(FILE_PATH, std::ios::binary);
    if (!file) {
        std::cerr << "Failed to open file: " << FILE_PATH << std::endl;
        closesocket(sock);
        WSACleanup();
        return 1;
    }

    // Send file
    char buffer[BUFFER_SIZE];
    int totalBytesSent = 0;
    while (file.read(buffer, BUFFER_SIZE) || file.gcount() > 0) {
        int bytesToSend = file.gcount();
        int bytesSent = send(sock, buffer, bytesToSend, 0);
        
        if (bytesSent == SOCKET_ERROR) {
            std::cerr << "Send failed with error: " << WSAGetLastError() << std::endl;
            file.close();
            closesocket(sock);
            WSACleanup();
            return 1;
        }

        totalBytesSent += bytesSent;
        std::cout << "Sent " << bytesSent << " bytes. Total: " << totalBytesSent << " bytes\n";
        
        // Delay to achieve desired transmission rate - using Sleep instead
        Sleep(DELAY_MS);  // Windows Sleep function from windows.h
    }

    std::cout << "File sent successfully. Total bytes sent: " << totalBytesSent << std::endl;

    // Cleanup
    file.close();
    shutdown(sock, SD_SEND);  // Properly shutdown the sending side
    closesocket(sock);
    WSACleanup();
    return 0;
}