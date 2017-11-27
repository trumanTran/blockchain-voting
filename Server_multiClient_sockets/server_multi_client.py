import socket
import select
import queue
import threading

import sys
import csv

#------------------------------------------ Class for holding client info ---------------------------------------------#
class Client_Info:
    #-- Constructor --#
    def __init__(self, machineID, privateKey, ipAddress ):
        self.machineID = machineID
        self.privateKey = privateKey
        self.ipAddress = ipAddress

    def change_ip_address(self, ipAddress):
        self.ipAddress = ipAddress

#----------------------------------------------------------------------------------------------------------------------#
#------------------- Import peer info from csv file and place into list of Client Info objects ------------------------#
clients = []

with open("peer_info.csv") as csvFile:
    readCSV = csv.reader(csvFile, delimiter=',')

    for row in readCSV:
        machineID = row[0]
        privateKey = row[1]
        ipAddress = row[2]

        clients.append(Client_Info(machineID,privateKey,ipAddress ))

    for x in clients:
        print("machine ID: ", x.machineID, " private key: ", x.privateKey, " IP Address: ", x.ipAddress)
#----------------------------------------------------------------------------------------------------------------------#
# ----- Declare empty List for Input & Output, an empty queue for message queues, a login Queue, and a thread lock -----#
inputs = []
outputs = []
message_queues = {}

login_queue = {}
login_lock = threading.Lock()

# ----------------------------------------------------------------------------------------------------------------------#
# ------------------------------------------------- Create Socket ------------------------------------------------------#
def socket_create():
    try:
        global host
        global port
        global server

        host = 'localhost'
        port = 9999

        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setblocking(0)  # non-blocking socket

        inputs.append(server)

    except socket.error as msg:
        print("Socket creation error: " + msg)


# ----------------------------------------------------------------------------------------------------------------------#
# -------------------------------------------------- Bind Socket -------------------------------------------------------#
def socket_bind():
    try:
        global host
        global port
        global server

        print("Binding socket to port: " + str(port))
        server.bind((host, port))

        server.listen(5)  # allows server to accept connections

    except socket.error as msg:
        print("Socket binding error: " + str(msg) + "\n" + "Retrying...")

        # -- Recursively calls socket_bind() function --#
        socket_bind()

# ---------------------------------------------------------------------------------------------------------------------#
# --------------------------------------------- Accept Connections ----------------------------------------------------#
# Accept from multiple clients and save to list
def accept_connections(message_queues):
    while inputs:
    #-------------------------------------------------------------------------------------------------------------#
        # -- select() function returns three new lists, which are subsets of list passed to select() --#
        readable, writeable, exceptional = select.select(inputs, outputs, inputs)
        #----------------------------------------------------------------------------------------------#

        # -------------- Passes over readable sockets to see if they are ready to accept data -------------------#
        for s in readable:

            # ---------------- If socket is "server" socket then ready to accept another connection-----------#
            if s is server:
                connection, client_address = s.accept()
                print("Connection from: ", client_address)

                #------------------------------------------------------------------------------#
                #------------ Create new thread to handle verification function ---------------#
                t = threading.Thread(target=verify_client(connection, clients))
                t.daemon = True
                t.start()
                #------------------------------------------------------------------------------#
                #------------------------------------------------------------------------------#

            # -------- If readable socket is not server socket then client socket ready to read data --------#
            else:
                data = s.recv(2048)
                if data:
                    print("received message: " + data.decode() + " from ", s.getpeername())
                    outgoing_message = work(data)

                    # ------------ Message put in the queue so it can be sent back to client when ready -------------#
                    message_queues[s].put(outgoing_message)

                    # --------- If client socket not in list of outputs, add it so we can write back to it ----------#
                    if s not in outputs:
                        outputs.append(s)

                        # -----------  A readable socket with no data is from a client that has disconnected ------------#
                else:
                    print("Closing socket", s.client_address)
                    if s in outputs:
                        outputs.remove(s)
                    inputs.remove(s)
                    s.close()

                    del message_queues[s]

                    # - s passes over writeable connections. If there is data in the queue for connection next message sent -#
                    # ------ If there is no data in queue connection is removed from list of output connections -------------#
        for s in writeable:
            try:
                outgoing_message = message_queues[s].get_nowait()
            except queue.Empty:
                print(s.getpeername(), "queue empty")
                outputs.remove(s)
            else:
                print("Sending " + outgoing_message + " to: ", s.getpeername())
                s.send(outgoing_message.encode("utf-8"))

                # -------------- s passes over error sockets, if there is an error socket is closed --------------------#
        for s in exceptional:
            print("exception condition on ", s.getpeername(), file=sys.stderr)
            inputs.remove(s)
            if s in outputs:
                outputs.remove(s)
            s.close()

            del message_queues[s]

# ----------------------------------------------------------------------------------------------------------------------#
# --------------------------------------------- Authentication Function ------------------------------------------------#
def verify_client(connection, clients):

    #-- Declare inputs  and message_queues as global variable so we can modify it --#
    global inputs
    global message_queues

    MAXIMUM_NUMBER_OF_ATTEMPTS = 5
    number_of_tries = 0;
    connected = False

    connection.setblocking(1)

    connection.send("Please enter your machine ID number, private key, and IP Address.".encode("utf-8"))
    login_info = connection.recv(2048)
    login_info = login_info.decode("utf-8")

    #------------------------------------------- Main While() Loop ------------------------------------------------#
    while (number_of_tries < MAXIMUM_NUMBER_OF_ATTEMPTS) and (connected is False):

        length = len(login_info)
        index = 0

        machineID = ""
        privateKey = ""
        ipAddress = ""

        print("%s %s" %(length, index))
    #------------------------------------- 3 While loops for parsing string --------------------------------------#

        #-- Parse login_info string to get machine name --#
        while(login_info[index] != " ") and (index < length):
            machineID += login_info[index]
            index = index + 1

        #--  Increase index to skip blank space --#
        index = index + 1

        #-- Parse login_info string to get private key --#
        while(login_info[index] != " ") and (index < length):
            privateKey += login_info[index]
            index = index + 1

         #-- Increase index to skip blank space --#
        index = index + 1

        #-- Parse login_info string to get IP Address --#
        while(index < length):
            ipAddress += login_info[index]
            index = index + 1

        print("Your login info is: %s %s %s" % (machineID, privateKey, ipAddress))
    #-------------------------------------------------------------------------------------------------------------#
    #-------------------------------------------------------------------------------------------------------------#

    #-- Bool variable for determining if a client exists in table --#
        found_match = False

    #-------------- Loop through list of clients and see if a match with login info is founc -------------------#
        for x in clients:

            #-- Client's machine id and private key match so it is confirmed to connect --#
            if (x.machineID == machineID) and (x.privateKey == privateKey):
                #-- Match found so update variable --#
                found_match = True
                print("match found!")

                #-- Client's IP address does not match so we update it in the Client list --#
                if(x.ipAddress != ipAddress):
                    x.change_ip_address(ipAddress)
                    print("Updated IP Address")

                #-- Make non-blocking socket --#
                connection.setblocking(0)

                #-- Add socket to list of connections --#
                inputs.append(connection)
                print("Added to inputs")

                #-- Send welcome message to client --#
                connection.send("Hello, welcome to the peer to peer network".encode("utf-8"))

                #-- Give the connection a queue for data we want to send --#
                message_queues[connection] = queue.Queue()

                #-- connected variable is set to true --#
                connected = True
                break
        #-----------------------------------------------------------------------------------------------------#
        #--#
        if found_match == True:
            break
        #----- If user fails to enter valid username or password but still has chance(s) left to do so -------#
        else:
            #-- increments the number of tries for every unsuccessful attempt --#
            number_of_tries += 1
            connection.send("Sorry, you entered an invalid username and/or passworld, please try again".encode("utf-8"))
            login_info = connection.recv(2048)
            login_info = login_info.decode()
    #------------------------------------------ End of While() Loop -----------------------------------------------#

	#--------------------------------------------------------------------------------------------------------------#
	#--------------------------------- Client failed to connect in five or lest attempts --------------------------#
    if connected is False:
        print("Client failed to provide a valid username and/or passworld in five tries.")
        connection.send("Sorry, you failed to provide a valid username and/or password in five attempts".encode("utf-8"))
        connection.close()

# ---------------------------------------------------------------------------------------------------------------------#
# ------------------ Work() Function performs any of the server profided operations -----------------------------------#
def work(command):
    command = command.decode()
    answer = ""

    if command == "blockchain":
        answer = "BLOCKCHAIN BABY!!!"
    elif command == "echo":
        answer = command
    elif command == "list":
        answer = str(inputs)
    else:
        answer = "Sorry, not a valid command, please try again"

    return answer


# ----------------------------------------------------------------------------------------------------------------------#
# -------------------------------------------------- Run Main()---------------------------------------------------------#
socket_create()
socket_bind()
accept_connections(message_queues)
