'''
The header for each byte stream sent and received is of the following format:
XXXXXXXXXX YYYYY Z* A* BBBB C*

- X represents the 10 character id of the sender
- Y represents the 5 character key of the sender
- Z represents any number of characters representing the ip address of the sender
- A represents any number of characters representing the port number of the sender
- B represents the uppercase 4 character command
- C represents the any number of characters making up the message sent

MACHINE_ID-MACHINE_KEY-IP_ADDRESS-PORT_NUMBER-COMMAND-MESSAGE
'''
import socket
import threading
#----------------------------------------------------------------------------------------------------------------------#
#----------------------------- These identifiers will be hard coded onto each machine ---------------------------------#
MACHINE_ID = "Machine001"
MACHINE_KEY = 12345

#MAX_NUMBER_OF PEERS = 10

HOST = "localhost"
SERVER_PORT = 999
SERVER_MACHINE_ID = "Server0001"
SERVER_KEY = 10101

IP_ADDRESS = socket.gethostbyname(socket.getfqdn())
PORT_NUMBER = 1000

#COMMAND_LENGTH = 4
#MACHINE_ID_LENGTH = 10
#KEY_LENGTH = 5

#-- This message header will be used to send every message for verification purposes --#
MESSAGE_HEADER = MACHINE_ID + " " + str(MACHINE_KEY) + " " + IP_ADDRESS + " " + str(PORT_NUMBER)
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
# ---------------------- Parse recieved message into command, machineID, Key, and message ------------------------------#

'''function takes socket connection and reveives message which it then parses out to obtain the connecting peer's command, 
machineID, key, and message containing block to add to blockchain if that is the command. Returns tuple containing:
(command, machineID, Key, message)'''

'''Function takes decoded string sent from connected socket, which it then parses out to obtain the sending peer's 
machineID, key, ip address, port number, the command, and the message sent. For out purposes the only messages sent will
be either empty strings, or a block to add to the blockchain. The function returns a tuple of the form:
(machine_id, key, ip_address, port_number, command, message)'''

def parse_incoming_message(message_string):

    machine_id = ""
    key = ""
    ip_address = ""
    port_number = ""
    command = ""
    message = ""

    message_length = len(message_string)
    i = 0
    #-- function to parse through string --#
    while i < message_length:

        #--------- machine_id -------------#
        while message_string[i] != " ":
            machine_id += message_string[i]
            i += 1
        #----------------------------------#

        i += 1
        #------------- key ----------------#
        while message_string[i] != " ":
            key += message_string[i]
            i += 1
        #----------------------------------#

        i += 1
        #---------- ip address ------------#
        while message_string[i] != " ":
            ip_address += message_string[i]
            i += 1
        #----------------------------------#

        i += 1
        #--------- port number ------------#
        while message_string[i] != " ":
            port_number += message_string[i]
            i += 1
        #----------------------------------#

        i += 1
        #------------ command -------------#
        while message_string[i] != " ":
            command += message_string[i]
            i += 1
        #----------------------------------#

        i +=1
        #------------- message ------------#
        while i < message_length:
            message += message_string[i]
            i += 1
        #----------------------------------#
    #-------------------------------------------------------------------------------------------------------------#

    return machine_id, key, ip_address, port_number, command, message
# ---------------------------------------------------------------------------------------------------------------------#
# --------------------------------------------- Authentication Function -----------------------------------------------#

'''Function takes the machineID and key that have been extracted from the parse_incoming_message function, and checks 
the list of peers to make sure the connecting peer is authorized to connect. If it is the function returns true, if not
returns false'''
#----------------------------------------------------------------------------------------------------------------------#
def verify_incoming_peer(connection, machineID, key, ip_address, port_number):

    found_match = False

    print("Machine login info is: %s %s %s %s" % (machineID, key, ip_address, port_number))
    # -------------------------------------------------------------------------------------------------------------#

    # -------------- Loop through list of clients and see if a match with login info is found -------------------#
    for x in peers:
        # -- Client's machine id and private key match so it is confirmed to connect --#
        if (x.machineID == machineID) and (x.privateKey == key):
            print("match found!")

            # -- Client's IP address does not match so we update it in the Client list --#
            if (x.ipAddress != ip_address):
                x.change_ip_address(ip_address)
                print("Updated IP Address: " + ip_address)

            if (x.portNumber != port_number):
                x.change_port_number(port_number)
                print("Updated Port Number: " + str(port_number))

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
                p.ipAddress = ip_address
                p.portNumber = port_number

                already_exist = True
                break
        if already_exist is False:
            with lock:
                registered_peers.append(Peer_Info(machineID, key, ip_address, port_number))
                print("Added to list of registered peers.")

        return True
# ---------------------------------------------------------------------------------------------------------------------#
# ------------------------------------------------- Handle connection -------------------------------------------------#
def handle_incoming_peer(connection):

    incoming_message = connection.recv(2048)
    incoming_message = incoming_message.decode()

    machine_id, key, ip_address, port_number, command, message = parse_incoming_message(incoming_message)

    if verify_incoming_peer(connection, machine_id, key, ip_address, port_number):
        print("peer verified, command: " + command)

        incoming_command_handler(connection, ip_address, port_number, command, message)

    else:
        print("Unverified attempt to connect at: %s" %(connection))
        outgoing_message = MESSAGE_HEADER + " " + "ERRO" + " " + ""
        connection.send(outgoing_message.encode("utf-8"))
        #connection.close()
# ---------------------------------------------------------------------------------------------------------------------#
#----------------------------------------------------------------------------------------------------------------------#
def handle_outgoing_peer(connection, command, message=""):

    outgoing_message = MESSAGE_HEADER + " " + command + " " + message
    connection.send(outgoing_message.encode("utf-8"))

    handle_incoming_peer(connection)
#----------------------------------------------------------------------------------------------------------------------#
#----------------------------------------------------------------------------------------------------------------------#
# ------------------ Command Handler takes commands from peer and performs necessary operation ------------------------#

def incoming_command_handler(connection, ip_address, port_number, command, incoming_message):

    global registered_peers

    #------------------------------------------------------------#
	#-- used for populating the peer and registered peer lists --#
    machineID = ""
    key = ""
    ipAddress = ""
    port = ""
    #------------------------------------------------------------#
	
    outgoing_message = ""
    #------------------------------------------------------------------------------------------------------------------#
    # --------------------------------------- Peer receives list of peers info ----------------------------------------#
    if command == "PEER":

        message_length = len(incoming_message)
        
        index = 0
        while index < message_length:
		
            # -----------  MachineID ---------------#
            while incoming_message[index] != " ":
                machineID += incoming_message[index]
                index += 1
            #---------------------------------------#
            
            index += 1
            # --------------- Key ------------------#
            while incoming_message[index] != " ":
                key += incoming_message[index]
                index += 1
            #---------------------------------------#
			
            index += 1
            #------------- ipAddress ---------------#
            while incoming_message[index] != " ":
                ipAddress += incoming_message[index]
                index += 1
            #---------------------------------------#
			
            index += 1
            #------------ portNumber ---------------#
            while incoming_message[index] != " ":
                port += incoming_message[index]
                index += 1
            #---------------------------------------#
            index +=1
            # -- Add peer info to list of peers --#
            peers.append(Peer_Info(machineID, key, ipAddress, port))

            # -- clear each variable so it can be reused --#
            machineID = ""
            key = ""
            ipAddress = ""
            port = ""

    #------------------------------------------------------------------------------------------------------------------#
    # -------------------  Peer receives command to send copy of registered peer list ---------------------------------#
    elif command == "REGP":

        print("sending list of registered peers to %s " % (connection))

        outgoing_message = MESSAGE_HEADER + " " + "REPL" + " " + ""

        for x in registered_peers:
            outgoing_message += (str(x.machineID) + " " + str(x.privateKey) + " " + str(x.ipAddress) + " " + str(x.portNumber) + " ")

        print(outgoing_message)
        connection.send(outgoing_message.encode("utf-8"))
    #-----------------------------------------------------------------------------------------------------------------------#
    # ----------------------------------------  Peer receive list of registered peers  -------------------------------------#
    elif command == "REPL":

        message_length = len(incoming_message)
        index = 0

        while index < message_length:

            # ------------------------- MachineID -----------------------------#
            while (index < message_length) and (incoming_message[index] != " "):
                machineID += incoming_message[index]
                index += 1
            #------------------------------------------------------------------#

            index += 1
            #------------------------------ Key ------------------------------#
            while (index < message_length) and (incoming_message[index] != " "):
                key += incoming_message[index]
                index += 1
            #------------------------------------------------------------------#
            
            index += 1
            # -------------------------- ipAddress ----------------------------#
            while (index < message_length) and (incoming_message[index] != " "):
                ipAddress += incoming_message[index]
                index += 1
            #------------------------------------------------------------------#
            
            index += 1
            #-------------------------- portNumber ----------------------------#
            while (index < message_length) and (incoming_message[index] != " "):
                port += incoming_message[index]
                index += 1
            #------------------------------------------------------------------#
            
            index += 1
            #---- Add peer to list of registered peers if not already there ---#
            found = False
            for p in registered_peers:
                if (p.machineID == machineID) and (p.privateKey == key):
                    p.ipAddress = ipAddress
                    p.portNumber = port
                    found = True
                    break
            #------------------------------------------------------------------#
            if found == False:
                registered_peers.append(Peer_Info(machineID, key, ipAddress, port))

            # -- clear variables to reuse --#
            machineID = ""
            key = ""
            ipAddress = ""
            port = ""

    #---------------------------------------------------------------------------------------------------------------#
    #----------------------------- Peer receives command to update it's blockchain ---------------------------------#
    elif command == "ADDB":

        print("Adding block to blockchain, sent from peer: %s " % (connection))
        block_chain.append(incoming_message)

        outgoing_message = MESSAGE_HEADER + " " + "CONF" + " " + incoming_message

        print(outgoing_message)
        connection.send(outgoing_message.encode("utf-8"))
    #---------------------------------------------------------------------------------------------------------------#
    #---------------------- Peer sends out command to update the blockchain with new block -------------------------#
    elif command == "SEND":

        outgoing_message = MESSAGE_HEADER + "ADDB" + " "  + incoming_message
        connection.send(outgoing_message.encode("utf-8"))
    #---------------------------------------------------------------------------------------------------------------#
    #-------- Peer reveives confirmation that other peer has received new block and added it to blockchain ---------#

    elif command == "CONF":
        print("Confirmation to add block to blockchain")

        block_chain.append(incoming_message)
        print("Block added")
    # --------------------------------------------------------------------------------------------------------------#
	#------------ Peer receives error message indicating something went wrong durring communication ----------------#
    elif command == "ERRO":
        print("error performing operation")
    #---------------------------------------------------------------------------------------------------------------#
    #------------------------------------ Peer receives Command to close socket ------------------------------------#
    # elif command == "QUIT":
	#---------------------------------------------------------------------------------------------------------------#
    #-------------------------   ----------- Peer receives invalid input -------------------------------------------#
    else:
        print("Invalid input")

    #connection.close()
	#---------------------------------------------------------------------------------------------------------------#
#-------------------------------------------------------------------------------------------------------------------#
#-------------------------------------- Loop to Listen for connections ---------------------------------------------#
def listen_loop():
    server_socket = makeserversocket(PORT_NUMBER)
    #server_socket.settimeout(2)

    while True:

        peer, address = server_socket.accept()
        print("Connection from: %s" % (peer))

        handle_incoming_peer(peer)
        '''
        # -- Create new thread to handle verification function --#
        t = threading.Thread(target=handle_incoming_peer(peer))
        t.daemon = True
        t.start()
		'''
#----------------------------------------------------------------------------------------------------------------------#
#----------------------- Loop to take in votes, then request to update the blockchain ---------------------------------#
def send_loop():

    command = ""
    peers.append(Peer_Info(SERVER_MACHINE_ID, str(SERVER_KEY), "", ""))
    for i in peers:
        print(i.machineID + str(i.privateKey) + i.ipAddress + str(i.portNumber))

    while True:
        print("Would you like to receive a copy of the peer info: (INIT), receive a copy of the registered peers in the "
              "network:(REGP), or send a block to be added to the blockchain: (SEND), or quit this program(QUIT)?")

        command = input("command: ")
        command = command.upper()
        if command == "QUIT":
            break
        message = input("message: ")

        sending_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        #s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #s.connect((host, port))

        if command == "SEND":

            for p in registered_peers:
                sending_socket.connect((p.ipAddress, p.port))
                handle_outgoing_peer(sending_socket, command, message)

        elif command == "INIT":

            sending_socket.connect((HOST,SERVER_PORT))
            handle_outgoing_peer(sending_socket, command, message)

        elif command == "REGP":
            sending_socket.connect((HOST,SERVER_PORT))
            handle_outgoing_peer(sending_socket, command, message)

        else:
            print("invalid command dummy!")

#----------------------------------------------------------------------------------------------------------------------#
#----------------------------------------------------------------------------------------------------------------------#

#----------------------------------------------------------------------------------------------------------------------#
#------------------------------------------------ Main body of program ------------------------------------------------#

#-- Have to first add the server's security info so that it can communicate with this peer --#
peers.append(Peer_Info(SERVER_MACHINE_ID, str(SERVER_KEY), "", ""))

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, SERVER_PORT))

command = "INIT"
message = ""
handle_outgoing_peer(s,command,message)

for i in peers:
    print("Peers: " + i.machineID + " " +  i.privateKey + " " + i.ipAddress + " " + i.portNumber)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, SERVER_PORT))

command = "REGP"
handle_outgoing_peer(s,command,message)

for i in registered_peers:
    print("Registered peers: " + " " + i.machineID + " " +  i.privateKey + " " + i.ipAddress + " " + i.portNumber)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, SERVER_PORT))

message = "BLOCKCHAIN BABY!!!"
command = "ADDB"
handle_outgoing_peer(s, command, message)

for b in block_chain:
    print(b)
