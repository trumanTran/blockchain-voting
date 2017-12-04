#Sending Code
import blockchain
import socket
import sys

def send_file(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((host, port))
    except socket.error as e:
        print(str(e))
        #break;
    try:
        sample = test_chain[0]
        bstream = str.encode(sample.hash_block())
        while (bstream):
            s.send(bstream)
            break;
        s.close()
    except socket.error as e:
        print(str(e))
        #break;
    
def receive_file(filename, port):
    #Filename should be written as a set of chars or a string.
    host = '' #We want to accept incoming requests from all kinds of things, not just one.
    #Triggers the code to have sockets always checking for incoming file transfers, which it then decodes.
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind((host, port))
    except socket.error as e:
        print(str(e))
    s.listen(10)
    #Now we 'receive' and decypher a file into another file, which is written.
    conn, addr = s.accept()
    file = open(filename, 'wb') #Open file and write in byte format to properly reconstitute data.
    while True:
        bstream = conn.recv(1024) #Retrieve incoming data in packets of size 1024.
        while(bstream): #Keep reading.
            file.write(bstream) #Protocol already set for file writing beforehand.
            bstream = conn.recv(1024) #Load next set of data.
            print(".")
            if not bstream:
                print("File received!")
                break;
        break;
    file.close() #Done writing file.
    print("File saved!")
    conn.close()
    s.close() #Close everything.

if __name__ == "__main__":
    test_chain = [blockchain.create_genesis_block()]
    Selection = input("What do you want to do? ")
    if (Selection == "send"):
        send_file("146.95.41.123", 12345)
    elif (Selection == "receive"):
        File = input("What are you expecting to receive? ")
        receive_file (File, 12345)
