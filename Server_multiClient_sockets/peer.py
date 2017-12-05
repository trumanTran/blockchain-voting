import socket
import threading

#----------------------------------------------------------------------------------------------------------------------#
#----------------------------- These identifiers will be hard coded onto each machine ---------------------------------#
MY_MACHINE_ID = "Machine1"
MY_PRIVATE_KEY = "12345"
#MAX_NUMBER_OF PEERS = 10
HOST = "localhost"
PORT_NUMBER = 1000
SERVER_PORT = 999
#----------------------------------------------------------------------------------------------------------------------#
#------------------------------List of peer info and list of peer socket connections-----------------------------------#
peers = []
registered_peers = []

#-- Block Chain will replace this list --#
block_chain = []
#----------------------------------------------------------------------------------------------------------------------#
#----------------------------------------------------------------------------------------------------------------------#
#-- Lock to prevent race conditions --#
lock = threading.Lock()
#------------------------------------------ Class for holding client info ---------------------------------------------#
class Peer_Info:
    #-- Constructor --#
    def __init__(self, machineID, privateKey, portNumber, ipAddress):
        self.machineID = machineID
        self.privateKey = privateKey
        self.portNumber = portNumber
        self.ipAddress = ipAddress

    def change_ip_address(self, ipAddress):
        self.ipAddress = ipAddress

    def change_port_number(self, portNumber):
        self.portNumber = portNumber
#----------------------------------------------------------------------------------------------------------------------#
#----------------------------------------------------------------------------------------------------------------------#
'''The first thing this program does is attempt to connect to the central server to get copies of the peer machine names
and key, along with a copy of the peers who have already joined the network. Once it does this the program will move on
to running an infinite loop to listen for connections, and an infinite loop to send updates to the blockchain. It will
iplement this by utilizing multi-threading'''
#----------------------------------------------------------------------------------------------------------------------#
#----------------------- Connects to server and requests peer list and registered peer list ---------------------------#
def initialize_peer_list(host, server_port):

    global peers

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, server_port))

    data = s.recv(2048)
    print(data.decode())

    #outgoing_message = input("->")
    outgoing_message = str(MY_MACHINE_ID) + " " + str(MY_PRIVATE_KEY)
    print(outgoing_message)
    s.send(outgoing_message.encode("utf-8"))

    data = s.recv(2048)
    data = data.decode()

    #-- If connection is confirmed --#
    if data == "CONF":

        #-- ****Need to add security protocol to make sure message is from server**** --#

        print("connection confirmed")
        print("request list of peers from server\n")

        #-- Send command to server to initialize peer table and registered peer table --#
        s.send("INIT".encode("utf-8"))
        data = s.recv(2048)
        data = data.decode()

        #-- Call Function to populate peer list --#
        get_list(peers, data)

        #-- Confirm peer list was recieved and now ready to receive registered peer list --#
        s.send("CONF".encode("utf-8"))
        data = s.recv(2048)
        data = data.decode()

        #-- Call Function to populate registered peers table
        get_list(registered_peers, data)

    else:
        print ("Failed to connect to server")
#----------------------------------------------------------------------------------------------------------------------#
#-------------------------- Function to parse string and modify specified list ----------------------------------------#
def get_list(list, data):
    data_length = len(data)
    index = 0

    #-- loop to parse through string and create Peer_Info objects to add to peers list --#
    while index < data_length:

        machineID = ""
        key = ""
        ipAddress = ""
        port = ""

        while data[index] != " ":
            machineID += data[index]
            index +=1
        index +=1

        while data[index] != " ":
            key += data[index]
            index +=1
        index += 1

        while data[index] != " ":
            ipAddress += data[index]
            index +=1
        index +=1

        while (data[index] != " ") and (index < data_length):
            port += data[index]
            index +=1
        index +=1

        list.append(Peer_Info(machineID, key, port, ipAddress))

    for x in list:
        print(str(x.machineID) + " " + str(x.privateKey) + " " + str(x.ipAddress) + " " + str(x.portNumber) + "\n")
#----------------------------------------------------------------------------------------------------------------------#
#----------------- This function creates a server socket, binds it and returns the object -----------------------------#
def makeserversocket(portNumber, backlog=5):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #-- allows us to reuse socket immediately after it is closed --#
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    #-- binds to whatever IP Address the peer is assigne --#
    s.bind(("", portNumber))
    print("binding peer server socket to port %s" %((PORT_NUMBER)))
    s.listen(backlog)
    print("Listening for connections...")
    return s
#----------------------------------------------------------------------------------------------------------------------#
# --------------------------------------------- Authentication Function -----------------------------------------------#
def verify_peer(connection):
    # -- Update peer info and add to registered_peers --#
    global peers
    global registered_peers

    # -- Bool variable for determining if a client exists in table --#
    found_match = False

    connection.send("Please enter your machine ID number and key.".encode("utf-8"))

    login_info = connection.recv(2048)
    login_info = login_info.decode("utf-8")

    host = connection.getpeername()

    machineID = ""
    privateKey = ""
    ipAddress = host[0]
    portNumber = host[1]

    # ----------------- 2 While loops for parsing incoming message to obtain machineID and Key ---------------------#
    message_length = len(login_info)
    index = 0
    # -- Parse login_info string to get machine name --#
    while (login_info[index] != " ") and (index < message_length):
        machineID += login_info[index]
        index +=1

    # --  Increase index to skip blank space --#
    index +=1

    # -- Parse login_info string to get private key --#
    # while(login_info[index] != " ") and (index < length):
    while (index < message_length):
        privateKey += login_info[index]
        index +=1

    print("Machine login info is: %s %s %s %s" % (machineID, privateKey, ipAddress, portNumber))
    # -------------------------------------------------------------------------------------------------------------#

    # -------------- Loop through list of clients and see if a match with login info is found -------------------#
    for x in peers:
        # -- Client's machine id and private key match so it is confirmed to connect --#
        if (x.machineID == machineID) and (x.privateKey == privateKey):
            print("match found!")

            # -- Client's IP address does not match so we update it in the Client list --#
            if (x.ipAddress != ipAddress):
                x.change_ip_address(ipAddress)
                print("Updated IP Address: " + ipAddress)

            if (x.portNumber != portNumber):
                x.change_port_number(portNumber)
                print("Updated Port Number: " + str(portNumber))

            # -- Match found so update variable --#
            found_match = True
            break
        # -----------------------------------------------------------------------------------------------------#

    # --------------------------------------------------------------------------------------------------------------#
    # ------------------------------------------- Peer failed to connect to ----------------------------------------#
    if found_match is False:
        print("Client failed to provide a valid machine name and/or key.")

        connection.send("Sorry you failed to connect".encode("utf-8"))
        connection.close()
        return False
    # -----------------------------------------------------------------------------------------------------------------#
    # -------------------------------------- Client successfully connected --------------------------------------------#
    else:
        # -- Add socket to list of connections --#
        with lock:
            registered_peers.append(Peer_Info(machineID, privateKey, ipAddress, portNumber))
            print("Added to list of registered peers.")

        connection.send("CONF".encode("utf-8"))
        return True
# ---------------------------------------------------------------------------------------------------------------------#
# ------------------ Command Handler takes commands from peer and performs necessary operation ------------------------#
def command_handler(connection, command, incoming_message):

    # -- Sever sends list of peers connected to peer to peer network --#
    if command == "LIST":
        outgoing_message = ""
        for x in registered_peers:
            outgoing_message += (str(x.machineID) + " " + str(x.privateKey) + " " + str(x.ipAddress) + " " + str(x.portNumber) + " ")

        print(outgoing_message)
        connection.send(outgoing_message.encode("utf-8"))
        return True

    # -- Server receives command to add to blockchain --#
    elif command == "ADDB":
        block_chain.append(incoming_message)
        print("block chain updated")
        connection.send("CONF".encode("utf-8"))
        return True

   # elif command == "QUIT"
        #remove_peer()
    # -- Undefined command --#
    else:
        print("Invalid Command!")
        connection.send("NOPE".encode("utf-8"))
        return False


# ----------------------------------------------------------------------------------------------------------------------#
# -- Handle connection --#
def handle_peer(connection):

    #-- First verify that peer attempting to connect can do so --#
    if verify_peer(connection):
        data = connection.recv(2048)
        data = data.decode()
        data_length = len(data)

        command = ""
        message = ""
        index = 0

        #-- Command consists of four upper case characters --#
        while index < 4:
            command += data[index]
            index += 1

        #-- Make sure command is upper case to prevent errors --#
        command = command.upper()

        while index < data_length:
            message += data[index]
            index += 1

        command_handler(connection, command, message)
#----------------------------------------------------------------------------------------------------------------------#
#----------------------------------------- Loop to Listen for connections ---------------------------------------------#
def listen_loop():
    server_socket = makeserversocket(PORT_NUMBER)
    #server_socket.settimeout(2)

    while True:
        peersock, peeraddr = server_socket.accept()
        handle_peer(peersock)
        peersock.close()
#----------------------- Loop to take in votes, then request to update the blockchain ---------------------------------#
def send_loop():
    print("What would you like to ask the peers to do: send a copy of the peer list(LIST), update the blockchain(ADDB)")
    command = input("->")
    for s in registered_peers:
        s.connect((s.ipAddress, s.portNumber))
        s.send(command)

        message = s.recv(2048)
        message = message.decode
        print(message)

#----------------------------------------------------------------------------------------------------------------------#
#------------------------------------------------ Main body of program ------------------------------------------------#
initialize_peer_list(HOST, SERVER_PORT)
# ---------------------------------------------------------------------------------------------------------------------#
# ---------------------------------- Create new thread to handle listen function --------------------------------------#
t = threading.Thread(target=listen_loop)
t.daemon = True
t.start()
# ---------------------------------------------------------------------------------------------------------------------#
send_loop()
# ---------------------------------------------------------------------------------------------------------------------#


#server_socket = makeserversocket(PORT_NUMBER)
#server_socket.settimeout(2)
#----------------------------------------------------------------------------------------------------------------------#
#----------------------------- Infinite Loop listens for connections from peers ---------------------------------------#

'''
while not shutdown:
    try:
        clientsock, clientaddr = server_socket.accept()
        clientsock.settimeout(None)

        t = threading.Thread(target = , args = [clientsock])
        t.start()

    except KeyboardInterrupt: #by pressing CTRL "c" user can break out of loop
        shutdown = True
        continue

print("Exiting Main Loop")
s.close()
'''
