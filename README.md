# Transport Protocol over UDP

A data transfer protocol, including connection establishment and congestion control. 
A client transmits a file as soon as the connection is established

The client application MUST be written in client.py file (you are allowed to create other .py files and modules), accepting three command-line arguments:

$ python3 ./client.py <HOSTNAME-OR-IP> <PORT> <FILENAME>

<HOSTNAME-OR-IP>: hostname or IP address of the server to connect (send UDP datagrams)
<PORT>: port number of the server to connect (send UDP datagrams)
<FILENAME>: name of the file to transfer to the server after the connection is established.
For example, the command below should result in connection to a server on the same machine listening on port 5000 and transfer content of file.txt:

$ python3 ./client.py localhost 5000 file.txt



The client must open a UDP socket and initiate 3-way handshake to the specified hostname/ip and port

Send UDP packet src-ip=DEFAULT, src-port=DEFAULT, dst-ip=HOSTNAME-OR-IP, dst-port=PORT with SYN flag set, 
Connection ID initialized to 0, Sequence Number set to 42, and Acknowledgement Number set to 0

Expect response from server with SYN | ACK flags. The client must record the returned Connection ID and use it in all subsequent packets.

Send UDP packet with ACK flag including the first part of the specified file.

The client should gracefully process incorrect hostname and port number and exist with a non-zero exit code (you can assume that the specified file is always correct). In addition to exit, the client must print out on standard error (using sys.stderr.write()) an error message that starts with ERROR: string.

After file is successfully transferred file (all bytes acknowledged), the client should gracefully terminate the connection

Send UDP packet with FIN flag set

Expect packet with ACK flag

Wait for 2 seconds for incoming packet(s) with FIN flag (FIN-WAIT)

During the wait, respond to each incoming FIN with an ACK packet; drop any other non-FIN packet.

Close connection and terminate with code zero


