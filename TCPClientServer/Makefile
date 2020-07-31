
CC = gcc
CFLAGS = 

# Target all: will make all possible executables
all: server.x client.x

# Create the server-side executable
server.x: TCPserver.o 
	$(CC) TCPserver.o -o server.x

# Create the client-side executable
client.x: TCPclient.o 
	$(CC) TCPclient.o -o client.x

# Create all the object files needed:
TCPserver.o: TCPserver.c 
	$(CC) $(CFLAGS) -c TCPserver.c

TCPclient.o: TCPclient.c
	$(CC) $(CFLAGS) -c TCPclient.c

# Remove all object files and executables:
clean:
	rm -f *.x
	rm -f *.o

