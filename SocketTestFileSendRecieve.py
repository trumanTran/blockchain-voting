#Sending Code
import socket
import sys

def send_file(filename, host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
    s.connect((host, port))
    except socket.error as e:
        print(str(e))
        break;
    try:
        file = open(filename, "rb")
        bstream = file.read(1024)
        while (bstream):
            s.send(bstream)
            bstream = file.read(1024)
        s.close()
    
def recieve_file(filename, port):
    #Filename should be written as a set of chars or a string.
    host = '' #We want to accept incoming requests from all kinds of things, not just one.
    #Triggers the code to have sockets always checking for incoming file transfers, which it then decodes.
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind((host, port))
    except socket.error as e:
        print(str(e))
    s.listen(10)
    #Now we 'recieve' and decypher a file into another file, which is written.
    conn, addr = s.accept()
    file = open(filename, 'wb') #Open file and write in byte format to properly reconstitute data.
    while True:
        bstream = conn.recv(1024) #Retrieve incoming data in packets of size 1024.
        while(bstream): #Keep reading.
            file.write(bstream) #Protocol already set for file writing beforehand.
            bstream = conn.recv(1024) #Load next set of data.
    file.close() #Done writing file.
    conn.close()
    s.close() #Close everything.
