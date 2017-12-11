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
import csv

#----------------------------------------------------------------------------------------------------------------------#
#--------------------------- These identifiers will be hard coded onto each machine -----------------------------------#
SERVER_ID = "Server0001"
SERVER_KEY = "10101"

HOST = "localhost"
IP_ADDRESS = socket.gethostbyname(socket.getfqdn())
PORT_NUMBER = "999"

#COMMAND_LENGTH = 4
#MACHINE_ID_LENGTH = 10
#KEY_LENGTH = 5

#-- This message header will be used to send every message for verification purposes --#
MESSAGE_HEADER = SERVER_ID + " " + SERVER_KEY + " " + IP_ADDRESS + " " + PORT_NUMBER

#----------------------------------------------------------------------------------------------------------------------#
#------------------------------------List of all peers and their info -------------------------------------------------#
peers = []
registered_peers = [] #-- List of peer connected to the network --#
#----------------------------------------------------------------------------------------------------------------------#
#----------------------------------------- Lock to prevent race conditions --------------------------------------------#
lock = threading.Lock()
#----------------------------------------------------------------------------------------------------------------------#
#-------------------------------------- Block Chain will replace this list --------------------------------------------#
block_chain = []
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
#------------------- Import peer info from csv file and place into list of Client Info objects ------------------------#
def read_peer_info(CSV_file_to_read):
    global peers
	
    with open(CSV_file_to_read) as csvFile:
        readCSV = csv.reader(csvFile, delimiter=',')

        for row in readCSV:
            machineID = row[0]
            privateKey = row[1]
            ipAddress = row[2]
            portNumber = row[3]

            peers.append(Peer_Info(machineID,privateKey,ipAddress,portNumber ))

        for x in peers:
            print("machine ID: ", x.machineID, " private key: ", x.privateKey, " IP Address: ", x.ipAddress, x.portNumber)
# ---------------------------------------------------------------------------------------------------------------------#
# ------------------------------------------------ Create Socket ------------------------------------------------------#
def makeserversocket(portNumber, backlog=5):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #-- allows us to reuse socket immediately after it is closed --#
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    #-- binds to whatever IP Address the peer is assigne --#
    s.bind(("", int(portNumber)))
    print("binding peer server socket to port " + portNumber)
    s.listen(backlog)
    print("Listening for connections...")
    return s
# ---------------------------------------------------------------------------------------------------------------------#
'''Function takes decoded string sent from connected socket, which it then parses out to obtain the sending peer's 
machineID, key, ip address, port number, the command, and the message sent. For out purposes the only messages sent will
be either empty strings, or a block to add to the blockchain. The function returns a tuple of the form:
(machine_id, key, ip_address, port_number, command, message)'''
#----------------------------------------------------------------------------------------------------------------------#
# --------------------- Parse recieved message into command, machineID, Key, and message ------------------------------#
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
    #------------------------------------------------------------------------------------------------------------------#

    return machine_id, key, ip_address, port_number, command, message
#----------------------------------------------------------------------------------------------------------------------#
# --------------------------------------------- Authentication Function -----------------------------------------------#

'''Function takes the machineID and key that have been extracted from the parse_incoming_message function, and checks 
the list of peers to make sure the connecting peer is authorized to connect. If it is the function returns true, if not
returns false'''

def verify_incoming_peer(connection, machineID, key, ip_address, port_number):

    found_match = False

    print("Machine login info is: " + machineID + " " + key + " " + ip_address + " " + port_number)
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

            if (x.portNumber != int(port_number)):
                x.change_port_number(port_number)
                print("Updated Port Number: " + port_number)

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
        outgoing_message = MESSAGE_HEADER + " " + "ERRO" + " " + ""
        connection.send(outgoing_message.encode("utf-8"))
# ---------------------------------------------------------------------------------------------------------------------#
# ---------------------------------------------------------------------------------------------------------------------#
def handle_outgoing_peer(connection, command, message=""):

    outgoing_message = MESSAGE_HEADER + " " + command + " " + message
    connection.send(outgoing_message.encode("utf-8"))

    handle_incoming_peer(connection)
#----------------------------------------------------------------------------------------------------------------------#
#----------------------------------------------------------------------------------------------------------------------#
# ------------------ Command Handler takes commands from peer and performs necessary operation ------------------------#

def incoming_command_handler(connection, ip_address, port_number, command, incoming_message):
    global registered_peers
    '''
    #---------------------------------------------------------#
    #-- used to populate peer list and registered peer list --#
    machineID = ""
    key = ""
    ipAddress = ""
    port = ""
    #---------------------------------------------------------#
    '''
    outgoing_message = ""
    #---------------Server receives command to send list of peers elligible to connect to network ---------------------#
    if command == "INIT":

        print("sending list of peers to %s " %(connection))

        outgoing_message = MESSAGE_HEADER + " " + "PEER" + " " + ""

        for x in peers:
            #outgoing_message += (str(x.machineID) + " " + str(x.privateKey) + " " + str(x.ipAddress) + " " + str(x.portNumber) + " ")
            outgoing_message += (x.machineID + " " + x.privateKey + " " + x.ipAddress + " " + x.portNumber + " ")

        print(outgoing_message)
        connection.send(outgoing_message.encode("utf-8"))

    #------------------------  Server receives command to send copy of registered peer list -----------------------------#
    elif command == "REGP":

        print("sending list of registered peers to %s " %(connection))

        outgoing_message = MESSAGE_HEADER + " " + "REPL" + " " + ""

        for x in registered_peers:
            #outgoing_message += (str(x.machineID) + " " + str(x.privateKey) + " " + str(x.ipAddress) + " " + str(x.portNumber) + " ")
            outgoing_message += (x.machineID + " " + x.privateKey + " " + x.ipAddress + " " + x.portNumber + " ")

        print(outgoing_message)
        connection.send(outgoing_message.encode("utf-8"))

    #------------------------------------------------------------------------------------------------------------------#
    #--------------- Peer receive request from another node to join it's list of registered peers ---------------------#
    elif command == "JOIN":
        outgoing_message = MESSAGE_HEADER + " " + "WELC" + " " + incoming_message
        print(outgoing_message)
        connection.send(outgoing_message.encode("utf-8"))
    #------------------------------------------------------------------------------------------------------------------#
	#----------------------------- Server receives command to update it's blockchain ----------------------------------#
    elif command == "ADDB":

        print("Adding block to blockchain, sent from peer: %s " % (connection))
        block_chain.append(incoming_message)

        outgoing_message = MESSAGE_HEADER + " " + "CONF" + " " + incoming_message

        print(outgoing_message)
        connection.send(outgoing_message.encode("utf-8"))
    #------------------------------------------------------------------------------------------------------------------#
	#-------- Server receives error message notifying it that something went wrong durring communication ----------------#
    elif command == "ERRO":
        print("error performing operation")
    #------------------------------------------------------------------------------------------------------------------#
    # ----------------------- Server receives notification that peer has quit the network -----------------------------#
    elif command == "QUIT":
        outgoing_message = MESSAGE_HEADER + " " + "DONE" + " " + incoming_message
        connection.send(outgoing_message.encode("utf-8"))
        print("Peer signed off from network")

        for p in registered_peers:
            if (p.ipAddress == ip_address) and (p.portNumber == port_number):
                del registered_peers[p]
    #------------------------------------------------------------------------------------------------------------------#
	#------------------------------------------ Recieves invalid input ------------------------------------------------#
    else:
        outgoing_message = MESSAGE_HEADER + " " + "ERRO" + " " + incoming_message

        print(outgoing_message)
        connection.send(outgoing_message.encode("utf-8"))
        print("Invalid input")
    #------------------------------------------------------------------------------------------------------------------#
#----------------------------------------------------------------------------------------------------------------------#

#----------------------------------------------------------------------------------------------------------------------#
#----------------------------------------------  Main body of program  ------------------------------------------------#

#-- Call function to read from csv table and populate peer and registered_peer lists --#
read_peer_info("peer_info_port.csv")




#peer, address = server_socket.accept()

#print("Connection from: %s" % (peer))

#-- Create server socket to listen for connections --#
server_socket = makeserversocket(PORT_NUMBER)
#server_socket.settimeout(2)
while True:
	
    peer, address = server_socket.accept()
    print("Connection from: %s" %(peer))

    handle_incoming_peer(peer)
    '''
    #-- Create new thread to handle verification function --#
    t = threading.Thread(target=handle_incoming_peer(peer))
    t.daemon = True
    t.start()
    '''
#----------------------------------------------------------------------------------------------------------------------#

#server.close()
	
