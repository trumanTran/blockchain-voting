'''
The format of any messsage sent between peers is as follows:
XXXXYYYYYYYYYZZZZZM*
Where x is the 4 character UPPER CASE command being sent, y is the ten character machineID, Z is the 5 characer key,
and M is a message of any length
'''

import socket
import threading

#----------------------------------------------------------------------------------------------------------------------#
#----------------------------- These identifiers will be hard coded onto each machine ---------------------------------#
MY_MACHINE_ID = "Machine001"
MY_PRIVATE_KEY = "12345"

#MAX_NUMBER_OF PEERS = 10

HOST = "localhost"
SERVER_PORT = 999

PORT_NUMBER = 1000
COMMAND_LENGTH = 4
MACHINE_ID_LENGTH = 10
KEY_LENGTH = 5
#----------------------------------------------------------------------------------------------------------------------#
#------------------------------List of peer info and list of peer socket connections-----------------------------------#
peers = []
registered_peers = []
#---------------------------------------- Block Chain will replace this list ------------------------------------------#
block_chain = []
#----------------------------------------------------------------------------------------------------------------------#
#----------------------------------------- Lock to prevent race conditions --------------------------------------------#
lock = threading.Lock()
#----------------------------------------------------------------------------------------------------------------------#
#----------------------------------------------------------------------------------------------------------------------#
#----------------------------------------------------------------------------------------------------------------------#
#------------------------------------------ Class for holding client info ---------------------------------------------#
class Peer_Info:
    #-- Constructor --#
    def __init__(self, machineID, privateKey, ipAddress, portNumber):
        self.machineID = machineID
        self.privateKey = privateKey
        self.ipAddress = ipAddress
        self.portNumber = portNumber

    def change_ip_address(self, ipAddress):
        self.ipAddress = ipAddress

    def change_port_number(self, portNumber):
        self.portNumber = portNumber
#----------------------------------------------------------------------------------------------------------------------#
#----------------------------------------------------------------------------------------------------------------------#
'''The first thing this program does is attempt to connect to the central server to get copies of the peer machine names
and key, along with a copy of the peers who have already joined the network. Once it does this the program will move on
to running an infinite loop to listen for connections, and an infinite loop to send updates to the blockchain. It will
iplement this by utilizing multi-threading
#----------------------------------------------------------------------------------------------------------------------#
#----------------------- Connects to server and requests peer list and registered peer list ---------------------------#
def initialize_peer_list(host, server_port):

    #global peers
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, server_port))

    # -- Send command to server to initialize peer table and registered peer table --#
    outgoing_message = "INIT" + str(MY_MACHINE_ID) + str(MY_PRIVATE_KEY)
    print(outgoing_message)
    s.send(outgoing_message.encode("utf-8"))

    data = s.recv(2048)
    data = data.decode()

    #-- If connection is formed and data is sent--#
    if data:
        #-- Call Function to populate peer list --#
        get_list(peers, data)
        for x in peers:
            print(str(x.machineID) + " " + str(x.privateKey) + " " + str(x.ipAddress) + " " + str(x.portNumber) + "\n")

        #-- Confirm peer list was recieved and now ready to receive registered peer list --#
        s.send("CONF".encode("utf-8"))
        data = s.recv(2048)
        data = data.decode()

        #-- Call Function to populate registered peers table
        get_list(registered_peers, data)
        for x in registered_peers:
            print(str(x.machineID) + " " + str(x.privateKey) + " " + str(x.ipAddress) + " " + str(x.portNumber) + "\n")

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

        #-- MachineID --#
        while data[index] != " ":
            machineID += data[index]
            index +=1
        index +=1

        #-- key --#
        while data[index] != " ":
            key += data[index]
            index +=1
        index += 1

        #-- ipAddress --#
        while data[index] != " ":
            ipAddress += data[index]
            index +=1
        index +=1

        #-- Port Number --#
        while (data[index] != " ") and (index < data_length):
            port += data[index]
            index +=1
        index +=1

        list.append(Peer_Info(machineID, key, ipAddress, port))
#----------------------------------------------------------------------------------------------------------------------#
#----------------------------------------------------------------------------------------------------------------------#
#----------------------------------------------------------------------------------------------------------------------#
'''
    #-- Now that peer list and registered peer list are populated the peer can initiate it's primary functions --#

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
# ---------------------- Parse recieved message into command, machineID, Key, and message ------------------------------#

'''function takes socket connection and reveives message which it then parses out to obtain the connecting peer's command, 
machineID, key, and message containing block to add to blockchain if that is the command. Returns tuple containing:
(command, machineID, Key, message)'''

def parse_incoming_message(message):

    # -- command 4 char long, machineID 10 char long, key 5 char long --#

    message_length = len(message)

    command = ""
    machineID = ""
    key = ""
    message = ""

    index = 0
    # -- Parse first four character to obtain command --#
    while index < COMMAND_LENGTH:
        command += message[index]
        index += 1
        command = command.upper()

    # -- Parse next 10 characters to get machineID --#
    while index < (COMMAND_LENGTH + MACHINE_ID_LENGTH):
        machineID += message[index]
        index += 1

    # -- parse next five characters to get peer key --#
    while index < (COMMAND_LENGTH + MACHINE_ID_LENGTH + KEY_LENGTH):
        key += message[index]
        index += 1

    # -- Parse message which will contain block to add to blockchain --#
    while index < message_length:
        message += message[index]
        index += 1

    return (command, machineID, key, message)
# ---------------------------------------------------------------------------------------------------------------------#
# --------------------------------------------- Authentication Function -----------------------------------------------#

'''Function takes the machineID and key that have been extracted from the parse_incoming_message function, and checks 
the list of peers to make sure the connecting peer is authorized to connect. If it is the function returns true, if not
returns false'''
#----------------------------------------------------------------------------------------------------------------------#
def verify_incoming_peer(connection, machineID, key):

    found_match = False

    host = connection.gethostname()
    ipAddress = host[0]
    portNumber = host[1]

    print("Machine login info is: %s %s %s %s" % (machineID, key, ipAddress, portNumber))
    # -------------------------------------------------------------------------------------------------------------#

    # -------------- Loop through list of clients and see if a match with login info is found -------------------#
    for x in peers:
        # -- Client's machine id and private key match so it is confirmed to connect --#
        if (x.machineID == machineID) and (x.privateKey == key):
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
    # ------------------------------------------------------------------------------------------------------------#
    # ------------------------------------------- Peer failed to connect to ----------------------------------------#
    if found_match is False:
        print("Peer failed to provide a valid machine name and/or key.")
        return False
    # -----------------------------------------------------------------------------------------------------------------#
    # -------------------------------------- Client successfully connected --------------------------------------------#
    else:
        already_exist = False

        # -- Add socket to list of connections --#
        for p in registered_peers:
            if p.machineID == machineID:
                p.ipAddress = ipAddress
                p.portNumber = portNumber

                already_exist = True
                break
        if already_exist is False:
            with lock:
                registered_peers.append(Peer_Info(machineID, key, ipAddress, portNumber))
                print("Added to list of registered peers.")

        return True
# ---------------------------------------------------------------------------------------------------------------------#
'''This function is used to verify that the peer we connect to and try to communiate with is in fact an authorized member
of the network
def verify_outgoing_peer(message):
    command, machineID, key, message = parse_incoming_message(message)

    verified = False
    for i in registered_peers:
        if (i.machineID == machineID) and (i.privateKey == key):
            verified = True

    return verified
'''
# ------------------------------------------------- Handle connection -------------------------------------------------#
def handle_incoming_peer(connection):

    incoming_message = connection.recv(2048)
    incoming_message = incoming_message.decode

    command, machineID, key, message = parse_incoming_message(incoming_message)

    if verify_incoming_peer(connection, machineID, key):
        print("peer verified")

        incoming_command_handler(connection, command, message)

    else:
        connection.send("ERRO".encode("utf-8"))
        connection.close()
# ---------------------------------------------------------------------------------------------------------------------#
def handle_outgoing_peer(connection, command, message=""):

    outgoing_message = command+str(MY_MACHINE_ID)+str(MY_PRIVATE_KEY)+message
    connection.send(outgoing_message.encode("utf-8"))

    handle_incoming_peer(connection)
# ------------------ Command Handler takes commands from peer and performs necessary operation ------------------------#

'''This function take the command send to peer and handles it, performing the necessary operation in accordance with the
command. The peers identity has already been established at this point so that in not a concern. Once this function
finishes it exits and the function that called it is responsible for closing the connection'''


def incoming_command_handler(connection, command, incoming_message):
    global registered_peers

    machineID = ""
    key = ""
    ipAddress = ""
    port = ""

    outgoing_message = ""
    # --------------------------Sever sends list of peers connected to peer to peer network --------------------------------#
    if command == "LIST":
        print("sending list of peers to %s " % (connection))

        outgoing_message = "PEER" + MY_MACHINE_ID + str(MY_PRIVATE_KEY)

        for x in peers:
            outgoing_message += (
                    str(x.machineID) + " " + str(x.privateKey) + " " + str(x.ipAddress) + " " + str(x.portNumber) + " ")

        print(outgoing_message)
        connection.send(outgoing_message.encode("utf-8"))

    # --------------------------------------- Peer receives list of peers info ---------------------------------------------#
    elif command == "PEER":

        message_length = len(incoming_message)
        index = 0

        while index < message_length:
            # -- MachineID --#
            while (index < message_length) and (incoming_message[index] != " "):
                machineID += incoming_message[index]
                index += 1

            index += 1

            # -- Key --#
            while (index < message_length) and (incoming_message[index] != " "):
                key += incoming_message[index]
                index += 1

            index += 1

            # -- ipAddress --#
            while (index < message_length) and (incoming_message[index] != " ")
                ipAddress += incoming_message[index]
                index += 1

            index += 1

            # -- portNumber --#
            while (index < message_length) and (incoming_message[index] != " "):
                port += incoming_message[index]
                index += 1

            index += 1

            # -- Add peer info to list of peers --#
            peers.append(Peer_Info(machineID, key, ipAddress, port))

    # ------------------------  Peer receives command to send copy of registered peer list ---------------------------------#
    elif command == "REGP":

        print("sending list of registered peers to %s " % (connection))

        outgoing_message = "REPL" + SERVER_ID + str(SERVER_KEY)

        for x in registered_peers:
            outgoing_message += (
                    str(x.machineID) + " " + str(x.privateKey) + " " + str(x.ipAddress) + " " + str(x.portNumber) + " ")

        print(outgoing_message)
        connection.send(outgoing_message.encode("utf-8"))

    # ----------------------------------------  Peer receive list of registered peers  -------------------------------------#
    elif command == "REPL":

        message_length = len(incoming_message)
        index = 0

        while index < message_length:

            # -- MachineID --#
            while (index < message_length) and (incoming_message[index] != " "):
                machineID += incoming_message[index]
                index += 1

            index += 1

            # -- Key --#
            while (index < message_length) and (incoming_message[index] != " "):
                key += incoming_message[index]
                index += 1

            index += 1

            # -- ipAddress --#
            while (index < message_length) and (incoming_message[index] != " ")
                ipAddress += incoming_message[index]
                index += 1

            index += 1

            # -- portNumber --#
            while (index < message_length) and (incoming_message[index] != " "):
                port += incoming_message[index]
                index += 1

            index += 1

            # -- Add peer to list of registered peers if not already there --#
            found = False
            for p in registered_peers:
                if (p.machineID == machineID) and (p.privateKey == key):
                    p.ipAddress = ipAddress
                    p.portNumber = port
                    found = True

            if found == False:
                registered_peers.append(Peer_Info(machineID, key, ipAddress, port))

    # -------------------------------- Peer receives command to update it's blockchain -------------------------------------#
    elif command == "ADDB":

        print("Adding block to blockchain, sent from peer: %s " % (connection))
        block_chain.append(incoming_message)

        outgoing_message = "CONF" + SERVER_ID + str(SERVER_KEY) + incoming_message

        print(outgoing_message)
        connection.send(outgoing_message.encode("utf-8"))

    # -------------------------- Peer sends out command to update the blockchain with new block ----------------------------#
    elif command == "SEND":

        outgoing_message = outgoing_message = "ADDB" + SERVER_ID + str(SERVER_KEY) + incoming_message
        connection.send(outgoing_message.encode("utf-8"))

    # ---------- Peer reveives confirmation that other peer has received new block and added it to blockchain --------------#

    elif command == "CONF":
        print("Confirmation to add block to blockchain")

        block_chain.append(incoming_message)
        print("Block added")
    # -----------------------------------------------------------------------------------------------------------------------#
    elif command == "ERRO":
        print("error performing operation")
        # outgoing_message = outgoing_message = "QUIT" + SERVER_ID + str(SERVER_KEY)+ incoming_message

        # connection.send(outgoing_message.encode("utf-8"))
    # ---------------------------------------- Peer receives Command to close socket ---------------------------------------#
    # elif command == "QUIT":
    # connection.close()
    # ----------------------------------------------------------------------------------------------------------------------#
    else:
        print("Invalid input")


#----------------------------------------------------------------------------------------------------------------------#
#----------------------------------------- Loop to Listen for connections ---------------------------------------------#
def listen_loop():
    server_socket = makeserversocket(PORT_NUMBER)
    #server_socket.settimeout(2)

    while True:

        peer, address = server_socket.accept()
        print("Connection from: %s" % (peer))

        # -- Create new thread to handle verification function --#
        t = threading.Thread(target=handle_incoming_peer(peer))
        t.daemon = True
        t.start()
#----------------------- Loop to take in votes, then request to update the blockchain ---------------------------------#
def send_loop():

    command = ""

    while True:

        print("What would you like to ask the peers to do: send a copy of the peer list(LIST), update the blockchain(ADDB)")
        command = input("command: ")
        if command == "QUIT":
            break
        message = input("message: ")

        command = command.upper()
        outgoing_message = command+str(MY_MACHINE_ID)+str(MY_PRIVATE_KEY)+message

        if command == "SEND":
            for p in registered_peers:
                ipAddress = p.ipAddress
                port = p.portNumber

                sending_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sending_socket.connect(ipAddress, port)
                handle_outgoing_peer(sending_socket, command, message)

        else:

            sending_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sending_socket.connect(ipAddress, port)
            handle_outgoing_peer(sending_socket, command, message)

#----------------------------------------------------------------------------------------------------------------------#
#------------------------------------------------ Main body of program ------------------------------------------------#

s = socket.socket()
s.connect((HOST, SERVER_PORT))

command = "LIST"
message = ""
handle_outgoing_peer(s,list,message)

command = "REGP"
handle_outgoing_peer(s,command,message)
