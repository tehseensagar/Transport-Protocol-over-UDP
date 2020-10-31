import socket
import sys
import time


# define chunk size
CHUNK_SIZE = 1024

# Input handlling
if len(sys.argv) < 4:
    sys.stderr.write("ERROR: Not enough input args.!\n")
    sys.exit(1)

# socket creation.
try :
    s = socket.socket()

except Exception:
    sys.stderr.write("ERROR: Socket creation failed...!\n")
    sys.exit(1)

# get host,port & filename from arguments
try :
    host  = str(sys.argv[1])
    port = int(sys.argv[2])
    fileName = str(sys.argv[3])
except :
    sys.stderr.write("ERROR: Invalid command line args.!\n")
    sys.exit(1)

# set timeout of the socket
s.settimeout(10)


try:

    s.connect((host,port))
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

wMsg = b"accio\r\n"
rMsg = b""


try :
    # start receiving "accio" command
    while(rMsg!=wMsg):
        chunk = s.recv(CHUNK_SIZE)
        rMsg = rMsg + chunk
    # if command received successfully, start sending the file
    if(rMsg==wMsg) :
        # open file and read as bytes.
        with open(fileName, 'rb') as f:
            # get start time
            t = time.time()
            # set time limit
            tEnd = 10 + t

            # send file over the socket.
            try:
                s.sendfile(f, 0)
            except Exception:
                sys.stderr.write("ERROR: File send failed..!\n")
                sys.exit(1)
            
        print("File send successfully.")
        # close socket connection
        s.close()
        # exit with success
        sys.exit(0)
    else:
        # print err msg
        sys.stderr.write("ERROR: Something went wrong..exiting..!\n")
        # exit with error
        sys.exit(1)
except socket.timeout:
    # print err msg
    sys.stderr.write("ERROR: connetion timeout..!\n")
    # exit with error
    sys.exit(1)