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
import sched, time
import socket
import threading
from tkinter import *
import tkinter.messagebox
import gui_header
import VotingContainer
import SQLVoterTable
import blockchain
import os

# ----------------------------------------------------------------------------------------------------------------------#
#-------------------------------------------GUI Variables--------------------------------------------------------------#
ballot = gui_header.LoadCSV('Ballot.csv')
votes = []
WriteInEntries = []
limitations = []
all_frames = []
compiledBallot = []
frameCount = 1
block = VotingContainer.Vote
stationId = 1234  # Station ID
blockToAdd = None

# ----------------------------------------------------------------------------------------------------------------------#
# ----------------------------- These identifiers will be hard coded onto each machine ---------------------------------#
MACHINE_ID = "Machine002"
MACHINE_KEY = "23456"
LEADER = False
# MAX_NUMBER_OF PEERS = 10
# HOST = "146.95.43.141"
HOST = '146.95.43.141'
SERVER_PORT = "999"
SERVER_MACHINE_ID = "Server0001"
SERVER_KEY = "10101"

IP_ADDRESS = '146.95.43.141'#socket.gethostbyname(socket.getfqdn())
PORT_NUMBER = "1000"

# -- This message header will be used to send every message for verification purposes --#
MESSAGE_HEADER = MACHINE_ID + "|" + MACHINE_KEY + "|" + IP_ADDRESS + "|" + PORT_NUMBER
# ----------------------------------------------------------------------------------------------------------------------#
# ------------------------------List of peer info and list of peer socket connections-----------------------------------#
peers = []
registered_peers = []
# ---------------------------------------- Block Chain will replace this list ------------------------------------------#
block_chain = []
# ----------------------------------------------------------------------------------------------------------------------#
# ----------------------------------------- Lock to prevent race conditions --------------------------------------------#
lock = threading.Lock()
# ----------------------------------------------------------------------------------------------------------------------#
# ------------------------------------------ Class for holding client info ---------------------------------------------#
class Peer_Info:
    # -- Constructor --#
    def __init__(self, machineID, privateKey, ipAddress, portNumber):
        self.machineID = machineID
        self.privateKey = privateKey
        self.ipAddress = ipAddress
        self.portNumber = portNumber

    def change_ip_address(self, ipAddress):
        self.ipAddress = ipAddress

    def change_port_number(self, portNumber):
        self.portNumber = portNumber

# ----------------------------------------------------------------------------------------------------------------------#
# ----------------------------------------------------------------------------------------------------------------------#
# ----------------------------------------------------------------------------------------------------------------------#
# ----------------- This function creates a server socket, binds it and returns the object -----------------------------#
def makeserversocket(portNumber, backlog=5):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # -- allows us to reuse socket immediately after it is closed --#
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # -- binds to whatever IP Address the peer is assigne --#
    s.bind(("", int(portNumber)))
    s.listen(backlog)
    s.setblocking(0)

    print("binding peer server socket to port " + PORT_NUMBER)
    print("Listening for connections...")
    return s

# ---------------------------------------------------------------------------------------------------------------------#
# --------------------------------------------- Authentication Function -----------------------------------------------#

'''Function takes the machineID and key that have been extracted from the parse_incoming_message function, and checks 
the list of peers to make sure the connecting peer is authorized to connect. If it is the function returns true, if not
returns false'''
# ---------------------------------------------------------------------------------------------------------------------#
def verify_incoming_peer(connection, machineID, key, ip_address, port_number):
    found_match = False

    print("Machine login info is: " + machineID + " " + key + "" + ip_address + "" + port_number)
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
            # -- Client's port number does not match so we update it in the Client list --#
            if (x.portNumber != port_number):
                x.change_port_number(port_number)
                print("Updated Port Number: " + str(port_number))

            # -- Match found so update variable --#
            found_match = True
            break
    # -----------------------------------------------------------------------------------------------------------------#
    # ------------------------------------------- Peer failed to connect to -------------------------------------------#
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
    machine_id, key, ip_address, port_number, command, message = incoming_message.split("|", 6)
    # machine_id, key, ip_address, port_number, command, message = parse_incoming_message(incoming_message)
    if verify_incoming_peer(connection, machine_id, key, ip_address, port_number):
        print("peer verified, command: " + command)
        incoming_command_handler(connection, ip_address, port_number, command, message)
    else:
        print("Unverified attempt to connect at: %s" % (connection))
        outgoing_message = MESSAGE_HEADER + "|" + "ERRO" + "|" + ""
        connection.send(outgoing_message.encode("utf-8"))

# ---------------------------------------------------------------------------------------------------------------------#
# ---------------------------------------------------------------------------------------------------------------------#
def handle_outgoing_peer(connection, command, message=""):
    outgoing_message = MESSAGE_HEADER + "|" + command + "|" + message
    connection.send(outgoing_message.encode("utf-8"))
    handle_incoming_peer(connection)

# ---------------------------------------------------------------------------------------------------------------------#
# ---------------------------------------------------------------------------------------------------------------------#
# ------------------ Command Handler takes commands from peer and performs necessary operation ------------------------#

def incoming_command_handler(connection, ip_address, port_number, command, incoming_message):
    global registered_peers
    # -----------------------------------------------------------------#
    # -- Variables for populating the peer and registered peer lists --#
    machineID = ""
    key = ""
    ipAddress = ""
    port = ""
    # -----------------------------------------------------------------------------------------------------------------#
    # --------------------------------------- Peer receives list of peers info ----------------------------------------#
    if command == "PEER":
        info = ['','','','']
        peers_information = incoming_message.strip()
        j = 0
        for i in peers_information:
            info[j] = i
            j+=1
            if j == 3:
                j = 0
                peers.append(Peer_Info(info[0], info[1], info[2], info[3]))
                #machineID, key, ipAddress, port

    # -----------------------------------------------------------------------------------------------------------------#
    # -------------------  Peer receives command to send copy of registered peer list ---------------------------------#
    elif command == "REGP":

        print("sending list of registered peers to %s " % (connection))

        outgoing_message = MESSAGE_HEADER + "|" + "REPL" + "|" + ""

        for x in registered_peers:
            outgoing_message += (
                    str(x.machineID) + " " + str(x.privateKey) + " " + str(x.ipAddress) + " " + str(x.portNumber) + " ")

        print(outgoing_message)
        connection.send(outgoing_message.encode("utf-8"))
    # -----------------------------------------------------------------------------------------------------------------#
    # -----------------------------------  Peer receive list of registered peers  -------------------------------------#
    elif command == "REPL":
        info = ['', '', '', '']
        peers_information = incoming_message.strip()
        j = 0
        for i in peers_information:
            info[j] = i
            j += 1
            if j == 3:
                j = 0
                found = False
                for p in registered_peers:
                    if (p.machineID == machineID) and (p.privateKey == key):
                        p.ipAddress = ipAddress
                        p.portNumber = port
                        found = True
                        break
                # ------------------------------------------------------------------#
                if (found == False) and (machineID != MACHINE_ID):
                    registered_peers.append(Peer_Info(info[0], info[1], info[2], info[3]))
                    # machineID, key, ipAddress, port
    # -----------------------------------------------------------------------------------------------------------------#
    # ------------ Peer receive request from another node to join it's list of registered peers -----------------------#
    elif command == "JOIN":
        outgoing_message = MESSAGE_HEADER + "|" + "WELC" + "|" + incoming_message
        print(outgoing_message)
        connection.send(outgoing_message.encode("utf-8"))
    # -----------------------------------------------------------------------------------------------------------------#
    # ------------ Peer receives confirmation that it has joined list of registered peers for node --------------------#
    elif command == "WELC":
        print("Succesfully joined list of registered peers for node at ip address: %s port number: %s"
              % (ip_address, port_number))
    # -----------------------------------------------------------------------------------------------------------------#
    # ----------------------------- Peer receives command to update it's blockchain -----------------------------------#
    elif command == "ADDB":
        print("Adding block to blockchain, sent from peer: %s " % (connection))
        block_chain.append(incoming_message)
        outgoing_message = MESSAGE_HEADER + "|" + "CONF" + "|" + incoming_message
        print(outgoing_message)
        connection.send(outgoing_message.encode("utf-8"))
    # -----------------------------------------------------------------------------------------------------------------#
    # -------- Peer reveives confirmation that other peer has received new block and added it to blockchain -----------#
    elif command == "CONF":
        print("Confirmation to add block to blockchain")
        block_chain.append(incoming_message)
        print("Block added: " + incoming_message)
    # -----------------------------------------------------------------------------------------------------------------#
    # ------------ Peer receives error message indicating something went wrong durring communication ------------------#
    elif command == "ERRO":
        print("error performing operation")
    # -----------------------------------------------------------------------------------------------------------------#
    # ------------------------------------------ Peer quits network ---------------------------------------------------#
    elif command == "QUIT":
        outgoing_message = MESSAGE_HEADER + "|" + "DONE" + "|" + incoming_message
        connection.send(outgoing_message.encode("utf-8"))
        for i, p in enumerate(registered_peers):
            if (p.ipAddress == ipAddress) and (p.portNumber == port_number):
                print("Peer: %s signed off from network." % (p.machineID))
                del registered_peers[i]
    # -----------------------------------------------------------------------------------------------------------------#
    # ------------------ Peer receives confirmation that it has disconnected from other peer --------------------------#
    elif command == "DONE":
        print("Confirmed disconnection from peer")
    # -----------------------------------------------------------------------------------------------------------------#
    elif command == "LEAD":
        LEADER = True
        print("%s is now the SUPREME leader" % (MACHINE_ID))
        time.sleep(3.0)
        LEADER = False
    # ----------------------------- Peer receives unrecognized command to close socket --------------------------------#
    else:
        outgoing_message = MESSAGE_HEADER + "|" + "ERRO" + "|" + incoming_message
        print(outgoing_message)
        connection.send(outgoing_message.encode("utf-8"))
    # -----------------------------------------------------------------------------------------------------------------#

# ---------------------------------------------------------------------------------------------------------------------#
# -------------------------------------------- Outgoing command handler -----------------------------------------------#
def outgoing_command_handler(command, message):
    global registered_peers
    if command == "ADDB":
        for p in registered_peers:
            sending_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # -- allows us to reuse socket immediately after it is closed --#
            sending_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            try:
                sending_socket.connect((p.ipAddress, int(p.portNumber)))
                handle_outgoing_peer(sending_socket, command, message)
                sending_socket.close()

            except socket.error as e:
                print(str(e))
                del registered_peers[p]

        # ----------------------------------------------------------------------------------#
        # ---------------------------------- Quit Program ----------------------------------#
    elif command == "QUIT":
        for p in registered_peers:
            try:
                sending_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sending_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

                sending_socket.connect((p.ipAddress, int(p.portNumber)))
                handle_outgoing_peer(sending_socket, command, message)
                sending_socket.close()

            except socket.error as e:
                print(str(e))
        # ----------------------------------------------------------------------------------#
    elif command == "LIST PEERS":
        list(peers)

    elif command == "LIST REGPEERS":
        list(registered_peers)
        # -------------------------- Invalid Command Given ---------------------------------#
    else:
        print("invalid command dummy!")
    # ----------------------------------------------------------------------------------#

# ---------------------------------------------------------------------------------------------------------------------#
# ------------------------------------------------ List peer info -----------------------------------------------------#
def list(peer_list):
    if peer_list:
        for i in peer_list:
            print(i.machineID + " " + i.privateKey + " " + i.ipAddress + " " + i.portNumber)
    else:
        print("List is empty")

# ---------------------------------------------------------------------------------------------------------------------#
# ------------ Initilize Peer by connecting to server and requesting peer_info and registered_peer_info ---------------#
def start_peer():
    peers.clear()
    registered_peers.clear()

    # ------------- add server info to list of peers to allow communication ------------#
    peers.append(Peer_Info(SERVER_MACHINE_ID, str(SERVER_KEY), "", ""))
    # ----------------------------------------------------------------------------------#
    # ------------------- Connect with server and get peer info ------------------------#
    command = "INIT"
    message = ""
    sending_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        sending_socket.connect((HOST, int(SERVER_PORT)))
        handle_outgoing_peer(sending_socket, command, message)

    except socket.error as msg:
        print("Failed to connect to server. " + str(msg))
        host_manual = input("IP Address-> ")
        port_number_manual = input("Port Number-> ")

        try:
            sending_socket.connect((host_manual, int(port_number_manual)))
            handle_outgoing_peer(sending_socket, command, message)

        except socket.error as msg:
            print("Failed to connnect to server. " + str(msg))

        finally:
            sending_socket.close()
    # ----------------------------------------------------------------------------------#

    # ------------- Connect with server and get registered peer info -------------------#
    command = "REGP"
    sending_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        sending_socket.connect((HOST, int(SERVER_PORT)))
        handle_outgoing_peer(sending_socket, command, message)

    except socket.error as msg:
        print("Failed to connect to server. " + str(msg))
        host_manual = input("IP Address-> ")
        port_number_manual = input("Port Number-> ")

        try:
            sending_socket.connect((host_manual, int(port_number_manual)))
            handle_outgoing_peer(sending_socket, command, message)

        except socket.error as msg:
            print("Failed to connnect to server. " + str(msg))
    finally:
        sending_socket.close()
    # ------------------------------------------------------------------------------------#

    # ---- Broadcast to other nodes to let them know new peer has joined network ---------#
    command = "JOIN"

    for peer in registered_peers:
        try:
            sending_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except:
            print("failed to create server socket")

        try:
            sending_socket.connect((peer.ipAddress, int(peer.portNumber)))
        except:
            print("failed to connect to %s %s %s" % (peer.machineID, peer.ipAddress, peer.portNumber))
        try:
            handle_outgoing_peer(sending_socket, command, message)
            sending_socket.close()
        except:
            print("failed to handle outgoing peer")

# ---------------------------------------------------------------------------------------------------------------------#
# ----------------------------------------- Loop to Listen for connections --------------------------------------------#
def listen_loop(server_socket):
    while True:
        try:
            peer, address = server_socket.accept()
            print("Connection from: %s" % (peer))
            # handle_incoming_peer(peer)
            # -- Create new thread to handle verification function --#
            t = threading.Thread(target=handle_incoming_peer, args=(peer,))
            t.daemon = True
            t.start()
        except:
            pass

    server_socket.close()

# ---------------------------------------------------------------------------------------------------------------------#
# ----------------------- Loop to take in votes, then request to update the blockchain --------------------------------#
def MAIN():
    start_peer()
    server_socket = makeserversocket(int(PORT_NUMBER))
    t = threading.Thread(target=listen_loop, args=(server_socket,))
    t.daemon = True
    t.start()

# -------------------------------- Loop keeps running as long as peer is active ---------------------------------------#
    # -----------------------------------------------------------------------------------------------------------------#
    # -------------------------------------------------GUI-------------------------------------------------------------#

    # ------------------------------------------------------------------------------------------------------------------
    # ----------------------------------------- Initialize Local Tables Once -------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    # SQLVoterTable.create_voter_reg()
    # SQLVoterTable.CSV_Load_Voters('/Users/admin/Desktop/blockchain-voting-master/dynamicGUI/NamesAddresses.csv')
    # ------------------------------------------------------------------------------------------------------------------
    # ------------------------------------------- Initialize Blockchain ------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    # during actual initialization, genesis_block will be set equal to the genesis block given by central server
    # central server will be the one to call create_genesis_block() and send that to all nodes
    genesisBlock = blockchain.create_genesis_block()
    # machine will create its own local blockchain utilizing the genesis block given
    blockchain.create_new_chain(genesisBlock)
    # ------------------------------------------------------------------------------------------------------------------
    # ------------------------------------------- Root Window declaration ----------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    root = Tk()
    # root.attributes("-fullscreen", True)
    root.title("Voting Booth")
    root.config(width=600, height=600)
    # ------------------------------------------------------------------------------------------------------------------
    # ----------------------------- create first frame, confirmation page, last frame ----------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    LoginFrame = Frame(root)
    confirmation_page = Frame(root)
    lastFrame = Frame(root)

    # ------------------------------------------------------------------------------------------------------------------
    # ----------------------------------------- Local function definaitions --------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    def proceed():
        global frameCount
        if frameCount < len(all_frames) - 1:
            all_frames[frameCount].tkraise()
            frameCount = frameCount + 1
        else:
            lastFrame.tkraise()
            frameCount = frameCount + 1
        return TRUE

    def lessCheck(counter):
        if counter < limitations[frameCount - 2][0]:
            answer = tkinter.messagebox.askquestion("YOU ARE ABOUT TO OMIT YOUR VOTE(S)",
                                                    "Are you sure you would like to omit " + (str)(limitations[frameCount - 2][0] - counter) + " vote(s) for this race?")
            if answer == 'yes':
                WriteInEntries[len(WriteInEntries) - frameCount + 1].config(state='disabled')
                return proceed()
        else:
            WriteInEntries[len(WriteInEntries) - frameCount + 1].config(state='disabled')
            return proceed()

    def populate():
        global frameCount
        for i in range(0, len(votes)):
            if limitations[i][0] > 1:
                counter = 0
                for j in range(len(votes[i])):
                    if votes[i][len(votes[i]) - 1].get() == 1 and counter == 0:
                        compiledBallot[i].append(WriteInEntries[len(WriteInEntries) - 1 - i].get().upper())
                        counter += 1
                    elif votes[i][j].get() == 1 and j < len(votes[i]) - 1:
                        compiledBallot[i].append(ballot[i][j + 2])
                        counter += 1
                while counter < limitations[i][0]:
                    counter += 1
                    compiledBallot[i].append('omitted')
            else:
                if votes[i][0].get() > 0:
                    if votes[i][0].get() == limitations[i][1]:
                        compiledBallot[i].append(WriteInEntries[len(WriteInEntries) - 1 - i].get().upper())
                    else:
                        compiledBallot[i].append(ballot[i][votes[i][0].get() + 1])
                else:
                    compiledBallot[i].append('omitted')
        block.set_votes(block, compiledBallot)
        block.set_id(block, nameInfo.get() + addressInfo.get())

    def check(confirmation):
        global frameCount
        progress = FALSE
        if limitations[frameCount - 2][0] == 1:
            if votes[frameCount - 2][0].get() == 0:
                answer = tkinter.messagebox.askquestion("YOU ARE ABOUT TO OMIT YOUR VOTE",
                                                        "Are you sure you would like to omit your vote for this race?")
                if answer == 'yes':
                    WriteInEntries[len(WriteInEntries) - frameCount + 1].config(state='disabled')
                    progress = proceed()
            else:
                if votes[frameCount - 2][0].get() == limitations[frameCount - 2][1]:
                    if (WriteInEntries[len(WriteInEntries) - frameCount + 1].get()).strip() == '':
                        tkinter.messagebox.showinfo("NOTICE", "The Write-In ballot has been left blank")
                    else:
                        WriteInEntries[len(WriteInEntries) - frameCount + 1].config(state='disabled')
                        progress = proceed()
                else:
                    WriteInEntries[len(WriteInEntries) - frameCount + 1].config(state='disabled')
                    progress = proceed()
        else:
            counter = 0
            for i in range(0, len(votes[frameCount - 2])):
                if votes[frameCount - 2][i].get() == 1:
                    counter += 1
            if counter > limitations[frameCount - 2][0]:
                tkinter.messagebox.showinfo("NOTICE", "You have voted for more candidates than you are allowed to")

            elif (votes[frameCount - 2][limitations[frameCount - 2][1] - 1].get() == 1):
                if (WriteInEntries[len(WriteInEntries) - frameCount + 1].get()).strip() == '':
                    tkinter.messagebox.showinfo("NOTICE", "The Write-In ballot has been left blank")
                else:
                    progress = lessCheck(counter)
            else:
                progress = lessCheck(counter)
        if confirmation == 1 and progress == TRUE:
            populate()
            gui_header.fillConfirmation(0, compiledBallot, canvasFrame)

    def appendBlock():
        global blockToAdd
        index = len(blockchain.chain)
        currentBallot = block.get_votes(block)
        # set blockToAdd to the proposed block containing the current voter's ballot
        blockToAdd = blockchain.next_block(stationId, currentBallot)
        # This is where we should first broadcast block or otherwise check to see if we accept block from another node
        #  For the time being, check whether previous hash of broadcast node is equal to latest block's current hash
        # Once ready, node will append block to local blockchain
        if (blockToAdd.previous_hash == blockchain.chain[index - 1].hash):
            blockchain.append_block(blockToAdd)
        print("Machine ID: ", blockchain.chain[index].machine_id)
        print("Time: ", blockchain.chain[index].timestamp)
        print("Ballot: ", blockchain.chain[index].data)
        print("Current Hash: ", blockchain.chain[index].hash)
        print("Previous Hash: ", blockchain.chain[index].previous_hash, "\n")

        message = (str)(blockchain.chain[index].machine_id) + '%' + (str)(blockchain.chain[index].timestamp) + '%' + \
                  (str)(blockchain.chain[index].data) + '%' + (str)(blockchain.chain[index].hash) + '%' + \
                  (str)(blockchain.chain[index].previous_hash)
        outgoing_command_handler('ADDB', 'BLOCK INFORMATION')
        proceed()

    def printOut():
        open("file.txt", 'w').close
        file = open("file.txt", 'w+')
        string = nameInfo.get() + addressInfo.get()
        string = string.replace(' ', '')
        file.write(string + '\n')
        for i in range(0, len(compiledBallot)):
            string = (str)(compiledBallot[i][0]) + ':' + '\n'
            file.write(string)
            for j in range(1, len(compiledBallot[i])):
                string = compiledBallot[i][j].strip() + '\n'
                file.write(string)
        file.close()
        os.startfile("file.txt", "print")

    def reset():
        global frameCount
        printOut()
        LoginFrame.tkraise()
        frameCount = 1
        for i in range(0, len(votes)):
            for j in range(len(votes[i])):
                votes[i][j].set(0)
        for entry in WriteInEntries:
            var = IntVar(0)
            gui_header.enable(entry, var, -1)
            entry.delete(0, END)
            gui_header.enable(entry, var, 1)
        nameInfo.delete(0, END)
        addressInfo.delete(0, END)
        for i in compiledBallot:
            for j in range(1, len(i)):
                del i[1]

    def configureCanvas(event):
        canvas.configure(scrollregion=canvas.bbox("all"), width=500, height=500)

    def changeVote():
        global frameCount
        frameCount = 1
        for i in compiledBallot:
            for j in range(1, len(i)):
                del i[1]
        for entry in WriteInEntries:
            if entry.get() != '':
                gui_header.enable(entry, IntVar(0), -1)
                if entry.get() != '':
                    gui_header.enable(entry, IntVar(0), -1)
        proceed()

    def validate():
        if SQLVoterTable.check_voter(nameInfo.get(), addressInfo.get()):
            proceed()

    # ------------------------------------------------------------------------------------------------------------------
    # ------------------------------------------------- login Frame ----------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    LoginFrame_subFrame = Frame(LoginFrame)
    LoginFrame_subFrame.grid(column=1, row=1)
    # ----- name and address labels ----- #
    name = Label(LoginFrame_subFrame, text="NAME", font=("", 12))
    address = Label(LoginFrame_subFrame, text="ADDRESS", font=("", 12))
    welcome = Label(LoginFrame, text="WELCOME", font=("", 18))
    # ----- entry boxes ----- #
    nameInfo = Entry(LoginFrame_subFrame, font=("", 12))
    addressInfo = Entry(LoginFrame_subFrame, font=("", 12))
    # ----- button definition ----- #
    submit = Button(LoginFrame, text="SUBMIT", command=validate, font=("", 14))
    submit.config(width=30, bg='gray80')
    # ----- placement of widgets onto the first frame ----- #
    welcome.grid(column=1, row=1, sticky=N)
    name.grid(row=0, column=0, sticky=E)
    address.grid(row=1, column=0, sticky=E)
    nameInfo.grid(row=0, column=1, sticky=EW)
    addressInfo.grid(row=1, column=1, sticky=EW)
    submit.grid(row=1, column=1, sticky=S)
    # ------------------------------------------------------------------------------------------------------------------
    # -------------------------------------------------- Last frame ----------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    lastFrame_SubFrame = Frame(lastFrame)
    lastFrame_SubFrame.grid(column=1, row=1)
    thanks = Label(lastFrame_SubFrame, text="THANK YOU FOR VOTING", font=("", 14))
    end = Button(lastFrame_SubFrame, text="FINISH", command=reset, font=("", 14))
    # ------------------------------------------------------------------------------------------------------------------
    # ---------------------------------------------- Confirmation page -------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    confirmation_subframe = Frame(confirmation_page)
    confirmation_subframe.grid(column=1, row=1)
    confirm = Button(confirmation_subframe, text='CONFIRM', command=appendBlock)
    redo = Button(confirmation_subframe, text='CHANGE', command=changeVote)
    prompt = Label(confirmation_subframe, text='PLEASE CONFIRM', font=("", 14))
    # ------- Scrollbar in case the entries in a ballot extend off screen ------- #
    myscrollbar = Scrollbar(confirmation_subframe, orient="vertical")
    canvas = Canvas(confirmation_subframe)
    canvas.configure(yscrollcommand=myscrollbar.set)
    canvasFrame = Frame(canvas)
    myscrollbar.config(command=canvas.yview)
    myscrollbar.pack(side="right", fill="y")
    canvas.create_window((250, 0), window=canvasFrame, anchor='n')
    canvas.bind("<Configure>", configureCanvas)
    # ------------------------------------------------------------------------------------------------------------------
    # ---------------------------------------- Placement of wigits and frames ------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    for i in [thanks, end, prompt, canvas]:
        i.pack()
    confirm.pack(side='right')
    redo.pack(side='left')
    for i in [LoginFrame, confirmation_page, lastFrame]:
        gui_header.configure(i)
        i.place(relx=0.5, rely=0.5, anchor="c", relwidth=1.0, relheight=1.0)  # add new frame to the window
        all_frames.append(i)
    # ------------------------------------------------------------------------------------------------------------------
    # ------------------------------- Dynamically create ballot based off ballot tuple ---------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    for i in range(0, len(ballot)):
        ballot_entry = Frame(root)  # frame for all information regarding one race
        gui_header.configure(ballot_entry)
        ballot_entry.place(relx=0.5, rely=0.5, anchor="c", relwidth=1.0, relheight=1.0)
        all_frames.insert(1, ballot_entry)
        subFrame = Frame(ballot_entry)  # subframe for the general information to go
        candidateFrame = Frame(subFrame)  # subfframe of subframe for the specific candidate entries
        subFrame.grid(row=1, column=1)
        raceText = Label(subFrame, text=ballot[i][0], font=("", 14))
        compiledBallot.append([ballot[i][0]])
        nextButton = Button(subFrame, text='NEXT', command=lambda x=0: check(x))
        if i == 0:
            nextButton.config(command=lambda x=1: check(x))
        directionsText = Label(subFrame, text="Please vote for " + (str)(ballot[i][1]), font=("", 10))
        for iterator in (raceText, directionsText, candidateFrame, nextButton):
            iterator.pack()
        limit = [0, 0]  # Allowed vote, number of candidates
        writeIn = Entry(candidateFrame, state='disabled', font=("", 12))
        WriteInEntries.append(writeIn)
        if ballot[i][1] == '1':  # if a single candidate race
            limit[0] = 1
            var = IntVar()
            votes.append([var])
            omit = Radiobutton(candidateFrame, text='OMIT', variable=votes[i][0], value=0, font=("", 12))
            omit.grid(sticky='W', row=0)
            wrb = Radiobutton(candidateFrame, variable=votes[i][0], font=("", 12))
            wrb.grid(sticky='W', row=len(ballot[i]))
            writeIn.grid(sticky='W', row=len(ballot[i]), padx=28)
            for j in range(2, len(ballot[i])):
                if ballot[i][j] != '':
                    limit[1] += 1
                    rb = Radiobutton(candidateFrame, text=ballot[i][j].upper(), variable=votes[i][0], value=limit[1],
                                     font=("", 12),
                                     command=lambda e=WriteInEntries[i], v=votes[i][0], x=len(ballot[i]) - 2:
                                        gui_header.enable(e, v, x))
                    rb.grid(sticky='W', row=j - 1)
            wrb.configure(value=limit[1] + 1, command=lambda e=WriteInEntries[i], v=votes[i][0], x=limit[1]:
            gui_header.enable(e, v, x))
            limit[1] += 1
        else:  # if multiple candidates can be selected
            limit[0] = ((int)(ballot[i][1]))
            candidateArray = []
            for j in range(2, len(ballot[i])):
                if (ballot[i][j] != ''):
                    var = IntVar()
                    candidateArray.append(var)
                    cb = Checkbutton(candidateFrame, text=ballot[i][j].upper(), variable=candidateArray[j - 2],
                                     font=("", 12))
                    cb.grid(sticky='W', row=j - 2)
                    limit[1] += 1
            # --- Write-in ---
            var = IntVar()
            candidateArray.append(var)
            writeIn.grid(sticky='W', row=len(ballot[i]) - 1, padx=28)
            cb = Checkbutton(candidateFrame, variable=candidateArray[len(candidateArray) - 1], font=("", 12),
                                command=lambda e=WriteInEntries[i], v=candidateArray[len(candidateArray) - 1], x=0:
                             gui_header.enable(e, v, x))
            limit[1] += 1
            cb.grid(sticky='W', row=len(ballot[i]) - 1)
            votes.append(candidateArray)
        limitations.append(limit)
    # ------------------------------------------------------------------------------------------------------------------
    # --------------------------------- Populate confirmation list with blank space ------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    listRowNumber = len(ballot)
    for i in range(len(limitations)):
        listRowNumber = listRowNumber + limitations[i][0]
    gui_header.fillConfirmation(listRowNumber, [], canvasFrame)
    # ------------------------------------------------------------------------------------------------------------------
    # ----------------------------------- Flip around lists to match output of GUI -------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    for i in [limitations, votes, ballot, compiledBallot]:
        i.reverse()
    LoginFrame.tkraise()
    root.mainloop()
    # ---------- Send Quit Message ---------- #
    outgoing_command_handler('QUIT', '')
    # -----------------------------------------------------------------------------------------------------------------#
# ---------------------------------------------------------------------------------------------------------------------#
# ----------------------------------------------------- MAIN CALL -----------------------------------------------------#

MAIN()
