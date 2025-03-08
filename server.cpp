#include <iostream>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netinet/tcp.h>
#include <unistd.h>
#include <cstring>
#include <errno.h>

#define PORT 4999
#define BUFFER_SIZE 40

bool DELAYED_ACK = false;  // Set to false to disable Delayed-ACK
bool NAGLE_ENABLED = true;  // Set to false to disable Nagle's algorithm

int main() {
    int server_fd, new_socket;
    struct sockaddr_in address;
    socklen_t addrlen = sizeof(address);
    char buffer[BUFFER_SIZE] = {0};

    // Create socket
    server_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (server_fd < 0) {
        perror("Socket failed");
        exit(EXIT_FAILURE);
    }

    // Set socket options
    int opt = 1;
    if (setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt)) < 0) {
        perror("setsockopt(SO_REUSEADDR) failed");
        close(server_fd);
        exit(EXIT_FAILURE);
    }

    // Disable Delayed ACK if needed
    if (!DELAYED_ACK) {
        int flag = 1;
        if (setsockopt(server_fd, IPPROTO_TCP, TCP_QUICKACK, &flag, sizeof(flag)) < 0) {
            perror("setsockopt(TCP_QUICKACK) failed");
            close(server_fd);
            exit(EXIT_FAILURE);
        }
    }

    // Disable Nagle's algorithm if needed
    if (!NAGLE_ENABLED) {
        int flag = 1;
        if (setsockopt(server_fd, IPPROTO_TCP, TCP_NODELAY, &flag, sizeof(flag)) < 0) {
            perror("setsockopt(TCP_NODELAY) failed");
            close(server_fd);
            exit(EXIT_FAILURE);
        }
    }

    address.sin_family = AF_INET;
    address.sin_addr.s_addr = INADDR_ANY;
    address.sin_port = htons(PORT);

    // Bind
    if (bind(server_fd, (struct sockaddr *)&address, sizeof(address)) < 0) {
        perror("Bind failed");
        close(server_fd);
        exit(EXIT_FAILURE);
    }

    // Listen
    if (listen(server_fd, 3) < 0) {
        perror("Listen failed");
        close(server_fd);
        exit(EXIT_FAILURE);
    }

    std::cout << "Listening on port " << PORT << "...\n";

    // Accept connection
    new_socket = accept(server_fd, (struct sockaddr *)&address, &addrlen);
    if (new_socket < 0) {
        perror("Accept failed");
        close(server_fd);
        exit(EXIT_FAILURE);
    }

    std::cout << "Client connected!\n";

    // Disable Nagle's algorithm on the new socket if needed
    if (!NAGLE_ENABLED) {
        int flag = 1;
        if (setsockopt(new_socket, IPPROTO_TCP, TCP_NODELAY, &flag, sizeof(flag)) < 0) {
            perror("setsockopt(TCP_NODELAY) failed");
            close(new_socket);
            close(server_fd);
            exit(EXIT_FAILURE);
        }
    }

    // Receive data
    int bytes_received;
    int total_bytes = 0;
    while ((bytes_received = recv(new_socket, buffer, BUFFER_SIZE, 0)) > 0) {
        total_bytes += bytes_received;
        // If you want to see the received data:
        std::cout.write(buffer, bytes_received);
    }

    if (bytes_received < 0) {
        perror("Receive failed");
    }

    std::cout << "Received file of size: " << total_bytes << " bytes\n";

    close(new_socket);
    close(server_fd);
    return 0;
}
