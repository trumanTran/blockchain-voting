import socket
import select
import queue
import threading

import sys
import csv

#----------------------------------------------------------------------------------------------------------------------#
#---------------------------------------- import user data from csv file ----------------------------------------------#
existing_members = {}
with open("user_info.csv") as csvFile:
    readCSV = csv.reader(csvFile, delimiter=',')


    for row in readCSV:
        name = row[0]
        user_name = row[1]
        existing_members[user_name] = name

    print(existing_members)
#----------------------------------------------------------------------------------------------------------------------#
#----- Declare empty List for Input & Output, an empty queue for message queues, a login Queue, and a thread lock -----#
inputs = []
outputs = []
message_queues = {}
connected_members = {}

login_queue = {}
login_lock = threading.Lock()
#----------------------------------------------------------------------------------------------------------------------#
#------------------------------------------------- Create Socket ------------------------------------------------------#
def socket_create():
	try:
		global host
		global port
		global server

		host = 'localhost'
		port = 9999

		server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		server.setblocking(0)#non-blocking socket

		inputs.append(server)

	except socket.error as msg:
		print("Socket creation error: " + msg)
#----------------------------------------------------------------------------------------------------------------------#
#-------------------------------------------------- Bind Socket -------------------------------------------------------#
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
		
#-- Recursively calls socket_bind() function --#		
		socket_bind()
#----------------------------------------------------------------------------------------------------------------------#
#--------------------------------------------- Accept Connection ------------------------------------------------------#
# Accept from multiple clients and save to list
def accept_connection(message_queues):

	while inputs:
	#------------------------------------------------------------------------------------------------------------------#
	#------------ select() function returns three new lists, which are subsets of list passed to select() -------------#

		readable, writeable, exceptional = select.select(inputs, outputs, inputs)
	#------------------------------------------------------------------------------------------------------------------#
	#------------------------------------------------------------------------------------------------------------------#

		#-------------- Passes over readable sockets to see if they are ready to accept data --------------------------#
		for s in readable:
		
			#-- If socket is "server" socket then ready to accept another connection --#
			if s is server:
				connection, client_address = s.accept()
				print("Connection from: ", client_address)
				
			#-------------------------------------------------------------------------------------------#		
			#------------------ Create thread to handle connection requests ----------------------------#

				t = threading.Thread(target = login(connection, existing_members, connected_members, message_queues, inputs))
				t.daemon = True
				t.start()
			#-------------------------------------------------------------------------------------------#
			
			#-- If readable socket is not server socket then client socket ready to read data --#
			else:
				data = s.recv(2048)
				if data:
					print("received message: " + data.decode() + " from ", s.getpeername())
					outgoing_message = work(data)

				#-- Message put in the queue so it can be sent back to client when ready --#
					message_queues[s].put(outgoing_message)

					#-- If client socket not in list of outputs, add it so we can write back to it --#
					if s not in outputs:
						outputs.append(s)
						
				#-- A readable socket with no data is from a client that has disconnected --#
				else:
					print("Closing socket" , client_address)
					if s in outputs:
						outputs.remove(s)
					inputs.remove(s)
					s.close()

					del message_queues[s]
		#--------------------------------------------------------------------------------------------------------------#
		
		#---- s passes over writeable connections. If there is data in the queue for connection next message sent -----#
		
		#-- If there is no data in queue connection is removed from list of output connections --#
		
		for s in writeable:
			try:
				outgoing_message = message_queues[s].get_nowait()
			except queue.Empty:
				print(s.getpeername(), "queue empty")
				outputs.remove(s)
			else:
				print("Sending " + outgoing_message + " to: ", s.getpeername())
				s.send(outgoing_message.encode("utf-8"))

		#--------------- s passes over error sockets, if there is an error socket is closed ---------------------------#
		
		for s in exceptional:
			print("exception condition on ", s.getpeername(), file=sys.stderr)
			inputs.remove(s)
			if s in outputs:
				outputs.remove(s)
			s.close()

			del message_queues[s]

#----------------------------------------------------------------------------------------------------------------------#
#--------------------------------------------- Authentication Function ------------------------------------------------#
def login(connection, existing_members, connected_members, message_queues, inputs):
	
	#-------------------- Set socket to blocking until connection is accepted, to prevent error -----------------------#
	connection.setblocking(1)
	
	#------------- Prompt client for login info and receive message from client containing info -----------------------#
	connection.send("Please enter your username and password to login.".encode("utf-8"))
	login_info = connection.recv(2048)
	login_info = login_info.decode()

	number_of_tries = 0;
	connected = False
	
	#------------------------------------------- Main While() Loop ------------------------------------------------#
	while (number_of_tries < 5) and (connected is False):

		length = len(login_info)
		index = 0
		user_name = ""
		user_password = ""

		#------------------------------ Nested while loops for parsing string ---------------------------------#
		
		#-- Parse login_info string to get user_name --#
		while(login_info[index] != " ") and (index < length):
			user_name += login_info[index]
			index = index + 1

		#--  Increase index to skip blank space--#
		index = index + 1

		#-- Parse login_info string to get password --#
		while(index < length):
			user_password += login_info[index]
			index = index + 1
			
		#----------------------------- Conditionals for evaluating login info -------------------------------------#
	
		#-- If username and password matches a user found in the database --#
		if existing_members[user_name] == user_password:
			#-- Make non-blocking socket --#
			connection.setblocking(0)

			#-- Add socket to list of connections --#
			inputs.append(connection)
			
			#-- Add connection to connected_members{} dictionary --#
			connected_members[user_name] = user_password

			#-- Send welcome message to client --#
			connection.send("Hello, welcome.".encode("utf-8"))

			#-- Give the connection a queue for data we want to send --#
			message_queues[connection] = queue.Queue()

			#-- connected variable is set to true --#
			connected = True
			break

		#-- If user fails to enter valid username or password but still has chance(s) left to do so --#
		else:
			#-- increments the number of tries for every unsuccessful attempt --#
			number_of_tries += 1
			connection.send("Sorry, you entered an invalid username and/or passworld, please try again".encode("utf-8"))
			login_info = connection.recv(2048)
			login_info = login_info.decode()
		#-----------------------------------------------------------------------------------------------------------#
	#------------------------------------------ End of While() Loop ----------------------------------------------------#

	#-- Client failed to connect in five or lest attempts --#
	if connected is False:
		print("Client failed to provide a valid username and/or passworld in five tries.")
		connection.send("Sorry, you failed to provide a valid username and/or password in five attempts".encode("utf-8"))
		connection.close()

#----------------------------------------------------------------------------------------------------------------------#


#------------------ Work() Function performs any of the server profided operations ------------------------------------#
def work(command):

	command = command.decode()
	answer = ""

	if command == "send":
		answer = command
	elif command == "send all":
		answer = command
	elif command == "who":
		answer = command
		#answer = "Logged on members are: "
		#for key in existing_members.items(): #should be connectec_members
			#answer += (key + " ")
	elif command == "logout":
		answer = "Goodbye!"
	else:
		answer = "Sorry, not a valid command, please try again"

	return answer
#----------------------------------------------------------------------------------------------------------------------#

#-------------------------------------------------- Run Main()---------------------------------------------------------#
socket_create()
socket_bind()
accept_connection(message_queues)
