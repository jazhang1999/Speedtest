
// Server side implementation of UDP client-server model 
#include <stdio.h> 
#include <stdlib.h> 
#include <unistd.h> 
#include <string.h> 
#include <sys/types.h> 
#include <sys/socket.h> 
#include <arpa/inet.h> 
#include <netinet/in.h> 
  
#define PORT    8080 
#define MAXLINE 1024 
  
// Driver code 
int main() { 
    int sockfd; 
    char buffer[MAXLINE] = {0}; 
    char *reply = "Server has recieved greetings"; 
    struct sockaddr_in servaddr = {0};
    struct sockaddr_in cliaddr = {0}; 
      
    /* Creating socket file descriptor. Using Af_INET for communication 
     * domain IPv4 and SOCK_DGRAM to do UDP. 0 is used to specify we 
     * want to use the default protocol for the address family. If socket
     * creation returns a negative value, terminate with error */
    if ((sockfd = socket(AF_INET, SOCK_DGRAM, 0)) < 0 ) { 
        perror("socket creation failed"); 
        exit(EXIT_FAILURE); 
    } 
      
    /* Fill in server information */
    servaddr.sin_family = AF_INET; // IPv4 
    servaddr.sin_addr.s_addr = INADDR_ANY; //UDP
    servaddr.sin_port = htons(PORT); // Convert int to something protocol can use
      
    /* Bind with sockfd from before. Cast servaddr to be a sockaddr for added
     * measure, and include size of servaddr for third parameter. Once again,
     * check to see if there is a need to exit prematurely */
    if ( bind(sockfd, (const struct sockaddr *)&servaddr, sizeof(servaddr)) < 0 ) 
    { 
        perror("Failed to bind"); 
        close(sockfd);
        exit(EXIT_FAILURE); 
    } 
    
    int val = sizeof(cliaddr);    

    int n = recvfrom(sockfd, (char *)buffer, MAXLINE, MSG_WAITALL, 0, &val);
    buffer[n] = '\n';
    printf("Message from client: %s", buffer);

    int check = sendto(sockfd, (const char *)reply, strlen(reply), 0,
                (const struct sockaddr *)&cliaddr, val);
    if (check < 0)
    {
        perror("Server failed to send");
    }
    
    printf("Message has been sent back to client\n");
    close(sockfd);
    return 0; 
} 
