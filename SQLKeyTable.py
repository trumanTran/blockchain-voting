import sqlite3
import os
import sys

#We have to open the server connection first.
con = sqlite3.connect("nodekey.db")
con.isolation_level = None
cur = con.cursor()
buffer = ""

"""Needed are the ip address, the signature, and the public key (per node)"""

def create_key_table():
	#This function only has one job: make the key table.
	#It has columns for the ip address, the signature, and the public key.
	cur.execute('CREATE TABLE key_table (signature TEXT, ip_add TEXT, pub_key TEXT)')
	#Table created.
	
def insert_to_key_table(sig, ip_add, pub_key):
	#Insert to the key table the values above.
	cur.execute('INSERT INTO key_table VALUES (?,?,?)', (sig, ip_add, pub_key))
	con.commit()

def ip_change(sig, new_ip):
	#Take a signature, find a hit on the SQL table, and then change its corresponding IP value to the new value.
	cur.executemany('UPDATE key_table SET ip_add=? WHERE sig=?', (new_ip, sig))
	con.commit()
	
def decrypt(sig):
	#Function that takes a signature from the sending block, checks the table for the public key corresponding to that block, and returns the value.
	cur.execute('SELECT pub_key FROM key_table WHERE sig=?', sig)
	#Now that we have the argument selected, we have to retrieve its value using fetch.
	return cur.fetchone() #BEWARE! ALL VALUES ARE RETURNED AS TUPLES! THEY ARE IMMUTABLE!

def delete_entry(sig):
	#Function to select a node's entries by signature, for node removal.
	cur.execute('DELETE FROM key_table WHERE sig=?', (sig,))
	#Deletes the node's entry. Since the node's actual entry does not exist anymore, it functionally stops them from sending useful data or having data sent to them.
	con.commit()

def find_node_ips():
	#This is for the broadcast function. It recalls ALL IPS CURRENTLY LISTED and returns the entire column of ips as a list of tuples. Access as if it were a list, since the column is literally one width wide.
	cur.execute('SELECT ip_add FROM key_table')
	return cur.fetchall()

"""Table Creation"""
create_key_table()
