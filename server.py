import socket
import sys
import signal
from _thread import *
import os

not_stopped = True
s = socket.socket()
id = 0

# this function will call when a SIGINT,SIGQUIT,SIGTERM signal receives!


def exit_gracefully(signalNumber, frame):
    print('\nSignal caught!')

    global not_stopped, s

    not_stopped = False
    print('Shutting down the server..!')
    s.shutdown(socket.SHUT_RD)
    s.close()
    return


def client_thread(conn, path):
    # set filename accoding to the id.
    fileName = path + '/' + str(id) + '.file'
    # open file as write bite format
    f = open(fileName, 'wb+')
    try:
        # send "accio" command
        conn.send(b"accio\r\n")

        # receive file from client
        chunk = conn.recv(1024)

        length = len(chunk)
        f.write(chunk)

        while chunk:
            chunk = conn.recv(1024)
            length = length + len(chunk)
            f.write(chunk)
        # after receiving the file, close the file and connection.
        print(length, " Bytes received!")

    except socket.timeout:
        # if timeout detected, flush the file and write single "ERROR" string in the file.
        f.flush()
        f.write(b"ERROR")
        # close the file and connection.

        sys.stderr.write("ERROR: File receiving timeout.!\n")
    finally:
        f.close()
        conn.close()


# register to the SIGINT,SIGTERM signal.
signal.signal(signal.SIGINT, exit_gracefully)
signal.signal(signal.SIGTERM, exit_gracefully)


def main():
    global id

    # Command line input args handling
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

    # handle incorrect port number
    if port in range(0, 1023):
        sys.stderr.write(
            "ERROR: Please enter valid port number (not in range 1-1023).!\n")
        sys.exit(1)

    # Starting server on [PORT]
    try:
        s.bind((host, port))
        print("server started at port ", port)
    except:
        sys.stderr.write("ERROR: Socket creation failed...!\n")
        sys.exit(1)

    # server only listen upto 10 connections.
    s.listen(10)

    # make directory to save files
    path = os.getcwd()
    path = path + '/' + fileDir
    if os.path.exists(path) != True:
        os.mkdir(path)

    # accepting connections
    while not_stopped:

        try:
            # accept incoming connection
            conn, addr = s.accept()
            print(addr, "has connected to the server!")
            # set timeout to 10s
            conn.settimeout(10)
            # set id
            id = id + 1
            start_new_thread(client_thread, (conn, path, ))
        except OSError:
            pass
    # after all exit from the main function with exit code of 0
    return 0


if __name__ == "__main__":
    main()
