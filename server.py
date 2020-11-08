import socket
import sys
import signal
from _thread import *
import os

# not_stopped = True
# s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# id = 0
# max_size = 524


def parse_header(msg):
    print("I'm header received", msg)
    sequenceNumber = int((msg[0:4]).decode())
    print("I am sequence number", sequenceNumber)
    acknowledgementNumber = int(msg[4:8].decode())
    connectionID = int(msg[8:10].decode())
    t = int((msg[10:12]).decode())
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
    print("Returning data")
    return header_data


def create_header(sequenceNumber, acknowledgementNumber, connectionID, A, S, FIN):
    s_n = str(sequenceNumber)
    s_n = '0' * (4-len(s_n)) + s_n

    a_n = str(acknowledgementNumber)
    a_n = '0' * (4-len(a_n)) + a_n

    con_id = str(connectionID)
    con_id = '0' * (2 - len(con_id)) + con_id

    t = '0'+str((A*4)+(S*2)+(FIN*1))
    header = (s_n + a_n + con_id + t).encode()
    return header


connectionID = 0

if len(sys.argv) < 3:
    sys.stderr.write("ERROR: Not enough input args.!\n")
    sys.exit(1)

# input handling
try:
    host = "0.0.0.0"
    port = int(sys.argv[1])
    fileDir = str(sys.argv[2])
except:
    sys.stderr.write("ERROR: Invalid command line args.!\n")
    sys.exit(1)

path = os.getcwd()
path = path + '/' + fileDir
if os.path.exists(path) != True:
    os.mkdir(path)

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as serverSocket:
    serverSocket.bind((host, port))
    print("UDP server up and listening")
    connectionID += 1

    fileName = path + '/' + str(connectionID) + '.file'
    sequenceNumber = 4321
    acknowledgementNumber = 0
    # open file as write bite format
    f = open(fileName, 'wb')
    try:

        msg, address = serverSocket.recvfrom(1024)
        print("I'm in main, received data:", msg)
        msg_header = parse_header(msg)
        if msg_header['S']:
            acknowledgementNumber = msg_header['sequenceNumber']
        header = create_header(
            sequenceNumber, acknowledgementNumber, connectionID, 1, 1, 0)
        print("I'm in main, create new header: ", header)
        sequenceNumber += 1
        serverSocket.sendto(header, (address))
        print("i'm in main, sent data to client", header)
        fin = False
        while fin != True:
            msg2, address = serverSocket.recvfrom(1024)
            print("I am inside while loop, received data from client: ", msg2)
            msg_header = parse_header(msg2[:12])
            acknowledgementNumber = msg_header['sequenceNumber']
            if msg_header['FIN']:
                print("File Received successfully.")
                fin = True
            data = msg2[12:]
            f.write(data)

        header = create_header(
            sequenceNumber, acknowledgementNumber, connectionID, 1, 0, 1)
        sequenceNumber += 1
        serverSocket.sendto(header, (address))
    except socket.timeout:
        # if timeout detected, flush the file and write single "ERROR" string in the file.
        f.flush()
        f.write(b"ERROR")
        # close the file and connection.

        sys.stderr.write("ERROR: File receiving timeout.!\n")


# def exit_gracefully(signalNumber, frame):
#     print('\nSignal caught!')

#     global not_stopped, s

#     not_stopped = False
#     print('Shutting down the server..!')
#     s.shutdown(socket.SHUT_RD)
#     s.close()
#     return


# def client_thread(conn, path, connectionID, host, port):
#     # set filename accoding to the id.
#     fileName = path + '/' + str(connectionID) + '.file'
#     sequenceNumber = 4321
#     acknowledgementNumber = 0
#     # open file as write bite format
#     f = open(fileName, 'wb+')
#     try:

#         msg = conn.recvfrom(1024)
#         msg_header = parse_header(msg[:12])
#         if msg_header['S']:
#             acknowledgementNumber = msg_header['sequenceNumber']
#         header = create_header(
#             sequenceNumber, acknowledgementNumber, connectionID, 1, 1, 0)
#         sequenceNumber += 1
#         conn.send(header)
#         fin = False
#         while fin != True:
#             msg = conn.recvfrom(1024)
#             msg_header = parse_header(msg[:12])
#             acknowledgementNumber = msg_header['sequenceNumber']
#             if msg_header['FIN']:
#                 print("File Received successfully.")
#                 fin = True
#             data = msg[12:]
#             f.write(data)

#         header = create_header(
#             sequenceNumber, acknowledgementNumber, connectionID, 1, 0, 1)
#         sequenceNumber += 1
#         conn.sendto(header, (host, port))
#     except socket.timeout:
#         # if timeout detected, flush the file and write single "ERROR" string in the file.
#         f.flush()
#         f.write(b"ERROR")
#         # close the file and connection.

#         sys.stderr.write("ERROR: File receiving timeout.!\n")
#     finally:
#         f.close()
#         conn.close()


# # register to the SIGINT,SIGTERM signal.
# signal.signal(signal.SIGINT, exit_gracefully)
# signal.signal(signal.SIGTERM, exit_gracefully)


# def main():
#     global id

#     # Command line input args handling
#     if len(sys.argv) < 3:
#         sys.stderr.write("ERROR: Not enough input args.!\n")
#         sys.exit(1)

#     # input handling
#     try:
#         host = "0.0.0.0"
#         port = int(sys.argv[1])
#         fileDir = str(sys.argv[2])
#     except:
#         sys.stderr.write("ERROR: Invalid command line args.!\n")
#         sys.exit(1)

#     # handle incorrect port number
#     if port in range(0, 1023):
#         sys.stderr.write(
#             "ERROR: Please enter valid port number (not in range 1-1023).!\n")
#         sys.exit(1)

#     # Starting server on [PORT]
#     try:
#         s.bind((host, port))
#         print("server started at port ", port)
#     except:
#         sys.stderr.write("ERROR: Socket creation failed...!\n")
#         sys.exit(1)

#     # server only listen upto 10 connections.
#     # s.listen(10)

#     # make directory to save files
#     path = os.getcwd()
#     path = path + '/' + fileDir
#     if os.path.exists(path) != True:
#         os.mkdir(path)

#     # accepting connections
#     while not_stopped:

#         try:
#             # accept incoming connection
#             # conn, addr = s.accept()
#             # print(addr, "has connected to the server!")
#             # set timeout to 10s
#             # conn.settimeout(10)
#             # set id
#             id = id + 1
#             start_new_thread(client_thread, (s, path, id, host, port))
#         except OSError:
#             pass
#     # after all exit from the main function with exit code of 0
#     return 0


# if __name__ == "__main__":
#     main()
