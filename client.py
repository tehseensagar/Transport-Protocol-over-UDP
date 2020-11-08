import socket
from socket import MSG_CTRUNC
import sys
import time
import os


def parse_header(header):
    sequenceNumber = int(header[0:4].decode())
    acknowledgementNumber = int(header[4:8].decode())
    connectionID = int(header[8:10].decode())
    t = int(header[10:12].decode())
    A = 1 if int(t/4) == 1 else 0
    S = 1 if int((t % 4)/2) == 1 else 0
    FIN = 1 if (t % 2) != 0 else 0

    header_data = {
        'sequenceNumber': sequenceNumber,
        'acknowledgementNumber': acknowledgementNumber,
        'connectionID': connectionID,
        'A': A,
        'S': S,
        'FIN': FIN
    }
    return header_data


def create_header(sequenceNumber, acknowledgementNumber, connectionID, A, S, FIN):
    s_n = str(sequenceNumber)
    print("Return header")
    s_n = '0' * (4-len(s_n)) + s_n

    a_n = str(acknowledgementNumber)
    a_n = '0' * (4-len(a_n)) + a_n

    con_id = str(connectionID)
    con_id = '0' * (2 - len(con_id)) + con_id

    t = '0'+str((A*4)+(S*2)+(FIN*1))
    header = (s_n + a_n + con_id + t).encode()

    return header


# Input handlling
if len(sys.argv) < 4:
    sys.stderr.write("ERROR: Not enough input args.!\n")
    sys.exit(1)

try:
    host = str(sys.argv[1])
    port = int(sys.argv[2])
    fileName = str(sys.argv[3])
except:
    sys.stderr.write("ERROR: Invalid command line args.!\n")
    sys.exit(1)

sequenceNumber = 42
acknowledgementNumber = 0
connectionID = 0

header = create_header(
    sequenceNumber, acknowledgementNumber, connectionID, 0, 1, 0)

sequenceNumber += 1
data_chunks = []

data_chunks = []

# Openning file
file = open(fileName, 'rb')

for i in range(0, os.path.getsize(fileName), 512):
    # reading data from file in chunks
    bytes = file.read(512)
    data_chunks.append(bytes)

with socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM) as clientSocket:
    clientSocket.sendto(header, (host, port))
    print(header)
    print("Header sent")
    msg, address = clientSocket.recvfrom(1024)
    print("Header received ", msg)
    header = parse_header(msg[:12])
    if header['S'] and header['A']:
        connectionID = header['connectionID']
        acknowledgementNumber = header['sequenceNumber']

    for data in data_chunks:
        header = create_header(
            sequenceNumber, acknowledgementNumber, connectionID, 1, 0, 0)

        acknowledgementNumber += 1
        sequenceNumber += 1
        frame = header + data
        clientSocket.sendto(frame, (host, port))
        time.sleep(1)
    print("File send successfully.")
    header = create_header(
        sequenceNumber, acknowledgementNumber, connectionID, 1, 0, 1)
    sequenceNumber += 1
    acknowledgementNumber += 1
    print("End header created", header)
    clientSocket.sendto(header, (host, port))
    print("End header sent to server")
    while 1:
        msg, address = clientSocket.recvfrom(1024)
        print("Last message received from server", msg)
        header = parse_header(msg[:12])
        if header['A']:
            print("Closing Connection.")
            clientSocket.close()
            sys.exit(0)


# socket creation.
# try:
#     s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# except Exception:
#     sys.stderr.write("ERROR: Socket creation failed...!\n")
#     sys.exit(1)

# get host,port & filename from arguments
# try:
#     host = str(sys.argv[1])
#     port = int(sys.argv[2])
#     fileName = str(sys.argv[3])
# except:
#     sys.stderr.write("ERROR: Invalid command line args.!\n")
#     sys.exit(1)

# max_size = 524
# # set timeout of the socket
# s.settimeout(10)

# # Validating connection
# try:
#     s.connect((host, port))
#     print("connected to the server!")
# except socket.timeout:
#     # if timeout
#     sys.stderr.write("ERROR: Socket connetion time exceed.!\n")
#     sys.exit(1)
# except ConnectionRefusedError:
#     # if server is not connected
#     sys.stderr.write("ERROR: Connection refused from the server..!\n")
#     sys.exit(1)
# except socket.gaierror:
#     # if host name is invalid
#     sys.stderr.write("ERROR: Hostname or service not known..!\n")
#     sys.exit(1)
# except OverflowError:
#     # if invalid port number
#     sys.stderr.write("ERROR: Invalid port number..!\n")
#     sys.exit(1)

# # Dividing data in chunks
# data_chunks = []

# # Openning file
# file = open(fileName, 'rb')

# for i in range(0, os.path.getsize(fileName), 512):
#     # reading data from file in chunks
#     bytes = file.read(512)
#     data_chunks.append(bytes)

# # Setting sequenceNum, acknowledge and connectionId
# sequenceNumber = 42
# acknowledgementNumber = 0
# connectionID = 0
# try:
#     # Creating header with ack, connId, A(set to 0), S(set to 1), FIN(set to 0)
#     print("Three way handshake\nStep 1: SYN = 1, ACK = 0, FIN = 0")
#     header = create_header(
#         # flag = SYN, first step in 3way handshake
#         sequenceNumber, acknowledgementNumber, connectionID, 0, 1, 0)
#     sequenceNumber += 1

#     # sending header to server

#     s.sendto(header, (host, port))
#     print("Sent")
#     # output whatever it sends to server

#     msg = s.recvfrom(1024)
#     print("Received")
#     # output whatever it receives from server

#     # new header received from server
#     header = parse_header(msg[:12])

#     # if SYN and ACK are set to 1
#     if header['S'] and header['A']:
#         print("Step 2 verified!")
#         connectionID = header['connectionID']
#         acknowledgementNumber = header['sequenceNumber']

#     for data in data_chunks:
#         print("Step 3, S = 0, A = 1, FIN = 0")
#         header = create_header(
#             sequenceNumber, acknowledgementNumber, connectionID, 1, 0, 0)

#         acknowledgementNumber += 1
#         sequenceNumber += 1
#         frame = header + data
#         s.send(frame)
#         time.sleep(1)
#     print("File send successfully.")
#     header = create_header(
#         sequenceNumber, acknowledgementNumber, connectionID, 1, 0, 1)
#     sequenceNumber += 1
#     acknowledgementNumber += 1
#     s.send(header)
#     while 1:
#         msg = s.recv(max_size)
#         header = parse_header(msg[:12])
#         if header['A']:
#             print("Closing Connection.")
#             s.close()
#             sys.exit(0)
# except socket.timeout:
#     # print err msg
#     sys.stderr.write("ERROR: connetion timeout..!\n")
#     # exit with error
#     sys.exit(1)

# s.close()
