import socket
import sys
import time
import os

# Input handlling
if len(sys.argv) < 4:
    sys.stderr.write("ERROR: Not enough input args.!\n")
    sys.exit(1)

# socket creation.
try:
    s = socket.socket()

except Exception:
    sys.stderr.write("ERROR: Socket creation failed...!\n")
    sys.exit(1)

# get host,port & filename from arguments
try:
    host = str(sys.argv[1])
    port = int(sys.argv[2])
    fileName = str(sys.argv[3])
except:
    sys.stderr.write("ERROR: Invalid command line args.!\n")
    sys.exit(1)


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
    s_n = '0' * (4-len(s_n)) + s_n

    a_n = str(acknowledgementNumber)
    a_n = '0' * (4-len(a_n)) + a_n

    con_id = str(connectionID)
    con_id = '0' * (2 - len(con_id)) + con_id

    t = '0'+str((A*4)+(S*2)+(FIN*1))
    header = (s_n + a_n + con_id + t).encode()
    return header


max_size = 524
# set timeout of the socket
s.settimeout(10)


try:

    s.connect((host, port))
    print("connected to the server!")
except socket.timeout:
    sys.stderr.write("ERROR: Socket connetion time exceed.!\n")
    sys.exit(1)
except ConnectionRefusedError:
    sys.stderr.write("ERROR: Connection refused from the server..!\n")
    sys.exit(1)
except socket.gaierror:
    sys.stderr.write("ERROR: Hostname or service not known..!\n")
    sys.exit(1)
except OverflowError:
    sys.stderr.write("ERROR: Invalid port number..!\n")
    sys.exit(1)

data_chunks = []
file = open(fileName, 'rb')

for i in range(0, os.path.getsize(fileName), 512):
    bytes = file.read(512)

    data_chunks.append(bytes)
sequenceNumber = 42
acknowledgementNumber = 0
connectionID = 0
try:
    header = create_header(
        sequenceNumber, acknowledgementNumber, connectionID, 0, 1, 0)
    sequenceNumber += 1
    s.send(header)
    msg = s.recv(max_size)
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
        s.send(frame)
        time.sleep(1)
    print("File send successfully.")
    header = create_header(
        sequenceNumber, acknowledgementNumber, connectionID, 1, 0, 1)
    sequenceNumber += 1
    acknowledgementNumber += 1
    s.send(header)
    while 1:
        msg = s.recv(max_size)
        header = parse_header(msg[:12])
        if header['A']:
            print("Closing Connection.")
            s.close()
            sys.exit(0)
except socket.timeout:
    # print err msg
    sys.stderr.write("ERROR: connetion timeout..!\n")
    # exit with error
    sys.exit(1)
