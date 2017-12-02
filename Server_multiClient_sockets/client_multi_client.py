import socket
import sys
#import threading #library used to create seperate thread to run broadcast thread
#import sched #library used to schedule broadcast function
#import time #library used to schedule broadcast function

#------------------------------------ Declare host an port number to connect to ---------------------------------------#
host = 'localhost'
port = 9999
server = ('localhost', 9999)
#----------------------------------------------------------------------------------------------------------------------#

#----------------------------- These identifiers will be hard coded onto each machine ---------------------------------#
machine_name = "Machine1"
public_key = "12345"
#----------------------------------------------------------------------------------------------------------------------#

#---------------------------------- Create client socket and connect to server ----------------------------------------#
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((host, port))
#----------------------------------------------------------------------------------------------------------------------#

#----------------------------------------------------------------------------------------------------------------------#
#------------------------------------ Deals with login confirmation with server ---------------------------------------#
logged_in = False
ALLOWED_NUMBER_OF_TRIES = 3
number_of_attempts = 0

#--------------- Loop attempts to automatically login client giving up after three failed attempts --------------------#
while (not logged_in) and (number_of_attempts < ALLOWED_NUMBER_OF_TRIES):
	outgoing_message = machine_name + " " + public_key
	client.sendto(outgoing_message.encode("utf-8"), server)

	incoming_message = client.recv(4096)
	#-- If the server can confirm the client's identity it allows it to join network --#
	if incoming_message.decode() == "CONFIRMED":
		print("Loggin confirmed!")
		logged_in = True
	#-----------------------------------------------------------------------------------#
	else:
		number_of_attempts += 1
#----------------------------------------------------------------------------------------------------------------------#

number_of_attempts = 0
outgoing_message = ""

#------------------ If the automatic login fails give the user three attempts to login manually -----------------------#
while(logged_in is False) and (number_of_attempts < ALLOWED_NUMBER_OF_TRIES):
	print("Login was unsuccesful, please enter the machine name and public key, seperated by one space.")

	outgoing_message = input("-> ")
	client.sendto(outgoing_message.encode('utf-8'), server)

	incoming_message = client.recv(4096)
	# -- If the server can confirm the client's identity it allows it to join network --#
	if incoming_message.decode() == "CONFIRMED":
		print("login confirmed!")
		logged_in = True
	#-----------------------------------------------------------------------------------#
	else:
		number_of_attempts += 1
#----------------------------------------------------------------------------------------------------------------------#

#------------------------------------- If loggin fails to connect program exits ---------------------------------------#
if logged_in is False:
	print("Sorry, you failed to connect to the network.")
	sys.exit()
#----------------------------------------------------------------------------------------------------------------------#
#----------------------------------------------------------------------------------------------------------------------#

#-------------- Client has succeeded in logging into server now ready to send command to server ----------------------#

while outgoing_message != 'quit':

	outgoing_message = ""
	incoming_message = ""

	outgoing_message = input("->")
	client.sendto(outgoing_message.encode('utf-8'), server)

	if not outgoing_message:
		print("Closing Socket", client.getsockname(), file=sys.stderr)
		client.close()

	incoming_message = client.recv(4096)
	if incoming_message != "":
		print(incoming_message)


