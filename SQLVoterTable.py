import sqlite3
import os
import sys
import csv

#The goal is to create three entries on the table: The name of the person (hashed), the address of the person (also hashed), and a bool value that checks if they're registered or not.
#For the hash, a cryptographic hash would be optimal.

#We have to open the server connection first.
con = sqlite3.connect("something.db")
con.isolation_level = None
cur = con.cursor()
buffer = ""
	
def create_voter_reg():
	#Creates the voter table.
	cur.execute('CREATE TABLE voter_reg (name TEXT, address TEXT, hasvoted BOOLEAN NOT NULL)')
	con.commit()
	
def insert_voter(voter_name, voter_add):
	#Insert a new voter, with the last bool value being set to 'false'.
	cur.execute('INSERT INTO voter_reg VALUES (?,?,?)', (voter_name, voter_add, 0))
	#Each voter must be inserted manually, but there will be a bulk insertion method avaliable later when this is refined.
        con.commit()
	
def mass_insert_voters(voter_list):
	#Inserts n amount of names and addresses.
    for i in range(0, len(voter_list)):
		insert_voter(voter_list[i][0], voter_list[i][1])
	#Stuff inserted.
	
def CSV_Load_Voters(file_name):
	#Function that takes the name of a file and loads it as a list of tuples. This list is then used to insert via the mass insert voters function.
	'''file must be in the following format for voter insertion:
	whole name, address
	Takes the result as a tuple, which is then processed by mass_insert_voters.'''
	with open(file_name, 'r') as file:
		reader = csv.reader(file)
		v_list = list(reader) #Entire list loaded into voter_list as a list of tuples.
		#Now that we are done opening the file, do things.
		mass_insert_voters(v_list) #Voters inserted.
	
def check_voter(target_name, target_address):
	'''Simplified version of hit_entry that has predefined arguments.
	It will form a query that checks for a bool from two conditionals. If true, it will then do a check for validity (the 'voted' bool value).
	If the bool value is false, the voter did not vote yet, and it is set to true, and a 'true' (1) bool is returned.
	Else, the bool value is false (0). False is a rejection of voter, keep this in mind. Everything is case sensitive.'''
	cur.execute('SELECT hasvoted FROM voter_reg WHERE name=:tname AND address=:tadd', {"tname": target_name, "tadd": target_address})
	bool_val = cur.fetchone()
	#Retrieves vote value. 'true' and 'false' become 1 and 0 respectively.
	if(bool_val == (0,)): #Assuming they haven't voted yet...
		#Pass an argument that sets the bool column to true, and also confirm the voter can vote.
		'''Insert vote message passing thing here.'''
		cur.execute('UPDATE voter_reg SET hasvoted = 1 WHERE name=? AND address=?', (target_name, target_address)) #Execute bool change.
		con.commit()
		return True;
	elif(bool_val == (1,)):
		#They voted already.
		'''Insert already voted message.'''
		return False;
	else():
		#No hits on list, suspicious...
		'''Insert not registered voter message.'''
		return False;
