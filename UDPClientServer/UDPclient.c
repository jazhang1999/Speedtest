
// Client side implementation of UDP client-server model 
#include <stdio.h> 
#include <stdlib.h> 
#include <unistd.h> 
#include <string.h> 
#include <sys/types.h> 
#include <sys/socket.h> 
#include <arpa/inet.h> 
#include <netinet/in.h> 
  
#define PORT     8080 
#define MAXLINE 1024 
  
// Driver code 
int main() { 
    int sockfd; 
    char buffer[MAXLINE]; 
    char * message = "Hello from client"; 
    struct sockaddr_in servaddr = {0}; 
  
    // Creating socket file descriptor 
    if ((sockfd = socket(AF_INET, SOCK_DGRAM, 0)) < 0 ) { 
        perror("socket creation failed"); 
        exit(EXIT_FAILURE); 
    } 
  
    /* Filling out server information */
    servaddr.sin_family = AF_INET; 
    servaddr.sin_addr.s_addr = INADDR_ANY; 
    servaddr.sin_port = htons(PORT); 
      
    int len = sendto(sockfd, (const char *)message, strlen(message), 
              0, (const struct sockaddr *)&servaddr, sizeof(servaddr)); 
    if (len < 0)
    {
        perror("Client failed to send");
    } 

    printf("Message has been sent.\n"); 
          
    int n = recvfrom(sockfd, (char *)buffer, MAXLINE, MSG_WAITALL, 0, &len); 
    buffer[n] = '\n'; 
    printf("Message from Server: %s\n", buffer); 
  
    close(sockfd); 
    return 0; 
} 

