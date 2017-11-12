import socket
import select
import queue
import sys

#----------------------------------------------------------------------------------------------------------------------#
#---------------------------------------- Declare List for Input & Output ---------------------------------------------#
inputs = []
outputs = []
message_queues = {}
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
		socket_bind()
#----------------------------------------------------------------------------------------------------------------------#
#--------------------------------------------- Accept Connection ------------------------------------------------------#
# accept from multiple clients and save to list
def accept_connection(message_queues):

	while inputs:
	#------- select() function returns three new lists, which are supsets of list passed to select() ---------#
		readable, writeable, exceptional = select.select(inputs, outputs, inputs)

	#---------------- passes over readable sockets to see if they are ready to accept data -------------------#
		for s in readable:
		#---------------- If socket is "server" socket then ready to accept another connection-----------#
			if s is server:
				connection, client_address = s.accept()
				print("Connection from: ", client_address)
				connection.setblocking(0)
				inputs.append(connection)
				connection.send("Hello, welcome. Please enter a command".encode("utf-8"))

				message_queues[connection] = queue.Queue() #give the connection a queue for data we want to send
		#----- Data is read with recv() then message in the queue so it can be sent back to client -----#
			else:
				data = s.recv(2048)
				if data:
					print("received message: " + data.decode() + " from ", s.getpeername())
					outgoing_message = "Message received"

					message_queues[s].put(outgoing_message)

					if s not in outputs:
						outputs.append(s)
			#---------  A readable socket with no data is from a client that has disconnected----------#
				else:
					print("Closing socket" , client_address)
					if s in outputs:
						outputs.remove(s)
					inputs.remove(s)
					s.close()

					del message_queues[s]

	#- s passes over writeable connections. If there is data in the queue for connection next message sent -#
	#------ If there is no data in queue connection is removed from list of output connections -------------#
		for s in writeable:
			try:
				outgoing_message = message_queues[s].get_nowait()
			except queue.Empty:
				print(s.getpeername(), "queue empty")
				outputs.remove(s)
			else:
				print("Sending " + outgoing_message + " to: ", s.getpeername())
				s.send(outgoing_message.encode("utf-8"))

	#-------------- s passes over error sockets, if there is an error socket is closed --------------------#
		for s in exceptional:
			print("exception condition on ", s.getpeername(), file=sys.stderr)
			inputs.remove(s)
			if s in outputs:
				outputs.remove(s)
			s.close()

			del message_queues[s]
#----------------------------------------------------------------------------------------------------------------------#
#---------------------------------------- Communication Function-------------------------------------------------------#
#yet to me finished---------------
'''
def communication(conn):
	conn.send(str.encode("Hello, and welcome. Please enter a command\n"))
	while True:
		incoming_message = conn.recv(2048)
		incoming_message = incoming_message.decode("utf-8")
		print(incoming_message)

		if incoming_message == 'quit':
			outgoing_message = 'Goodbye'
			conn.send(str.encode(outgoing_message))
			break
		elif incoming_message == 'list':
			outgoing_message = list_connections()
		else:
			outgoing_message = "Command not recognized"

		conn.send(str.encode(outgoing_message))		
'''
#----------------------------------------------------------------------------------------------------------------------#
#-------------------------------------------------- Run Main()---------------------------------------------------------#
socket_create()
socket_bind()
accept_connection(message_queues)
