mport socket
import threading
import csv

HOST = "localhost"
PORT_NUMBER = 999

#-- List of peer info --#
peers = []
#-- List of peer socket connections --#
registered_peers = []
#-- Lock to prevent race conditions --#
lock = threading.Lock()

#-- Block Chain will replace this list --#
block_chain = []

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
# ----------------------------------------------------------------------------------------------------------------------#
# ------------------------------------------------- Create Socket ------------------------------------------------------#
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
# ----------------------------------------------------------------------------------------------------------------------#
# --------------------------------------------- Authentication Function ------------------------------------------------#
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
      # ------------------------------------------------------------------------------------------------------------#
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
	
    #---------------------- Sever sends list of peers connected to peer to peer network -------------------------------#
    if command == "INIT":
        print("sending list of peers to %s " %(connection))

        outgoing_message = ""
        for x in peers:
            outgoing_message += (str(x.machineID) + " " + str(x.privateKey) + " " + str(x.ipAddress) + " " + str(x.portNumber) + " ")

        print(outgoing_message)
        connection.send(outgoing_message.encode("utf-8"))

        confirmation = connection.recv(2048)
        confirmation = confirmation.decode()

		#-- peer receive peer list successfully, now ready to receive registered user list --#
        if confirmation == "CONF":
            outgoing_message = ""
            for x in registered_peers:
                outgoing_message += (str(x.machineID) + " " + str(x.privateKey) + " " + str(x.ipAddress) + " " + str(x.portNumber) + " ")

            print(outgoing_message)
            connection.send(outgoing_message.encode("utf-8"))

            return True
        else:
            print("Failed to send peer list to peer requesting it.")
            return False
	#-------------------------------------------------------------------------------------------------------------------#
	#-- Server receive command to return list of registered peers --#
    elif command == "PEER":
        print("sending list of connect peers to %s " %(connection))

        outgoing_message = ""
        for x in registered_peers:
            outgoing_message += (str(x.machineID) + " " + str(x.privateKey) + " " + str(x.ipAddress) + " " + str(x.portNumber) + " ")

        print(outgoing_message)
        connection.send(outgoing_message.encode("utf-8"))
        return True

    #-- Server receives command to add to blockchain --#
    elif command == "ADDB":
        block_chain.append(incoming_message)
        print("block chain updated")
        connection.send("CONF".encode("utf-8"))
        return True
		
    #-- Undefined command --#
    else:
        print("Invalid Command!")
        connection.send("QUIT".encode("utf-8"))
        return False
#----------------------------------------------------------------------------------------------------------------------#
#------------------------------------------------- Handle connection --------------------------------------------------#
def handle_peer(connection):

    if verify_peer(connection):
        print("client verified")
        data = connection.recv(2048)
        data = data.decode()
        data_length = len(data)
		
        command = ""
        message = ""
        index = 0
		
        while index < 4:
            command += data[index]
            index += 1
			
        command = command.upper()
			
        while index < data_length:
            message += data[index]
            index += 1
			
        command_handler(connection, command, message)

# ---------------------------------------------------------------------------------------------------------------------#
#-----------------------------------------------------------------------------------------------------------------#

#-- call function to read from csv table --#
read_peer_info("peer_info_port.csv")
server_socket = makeserversocket(PORT_NUMBER)
#server_socket.settimeout(2)
#---------------- Main body of function, using infinite loop to continue listening for connections ---------------#
while True:
	
    peer, address = server_socket.accept()
    print("Connection from: %s" %(peer))
    handle_peer(peer)
    '''
    #------------------------------------------------------------------------------#
    #------------ Create new thread to handle verification function ---------------#
    t = threading.Thread(target=verify_client(connection, peers))
    t.daemon = True
    t.start()
    #------------------------------------------------------------------------------#
    #------------------------------------------------------------------------------#
	'''

#server.close()
