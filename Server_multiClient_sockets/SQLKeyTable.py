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
    cur.execute('CREATE TABLE IF NOT EXISTS key_table (signature TEXT UNIQUE NOT NULL, ip_add TEXT UNIQUE, port TEXT UNIQUE, pub_key TEXT UNIQUE NOT NULL)')
    #Table created.

def insert_to_key_table(sig, ip_add, port, pub_key):
    #Insert to the key table the values above.
    cur.execute('INSERT INTO key_table VALUES (?,?,?,?)', (sig, ip_add, port, pub_key))
    con.commit()

def mass_insert_keys(key_list):
    #Inserts a bunch of values from a list of tuples.
    for i in range (0, len(key_list)):
        insert_to_key_table(key_list[i][0],key_list[i][1],key_list[i][2],key_list[i][3])
    #All things inserted.

def CSV_Insert_Keys(file_name):
    #Takes entire file and loads as a list of tuples. Resulting list is used with mass_insert_keys.
    '''file must be in the following format:
        signature, ip address, port, public key'''
    with open (file_name, 'r') as file:
        reader = csv.reader(file)
        k_list = list(reader)
        mass_insert_keys(k_list)
    #Insertion Finished.

def set_disconnect(old_ip):
    #Function to 'clean' the ip address field until the machine reconnects using the appropriate signature.
    cur.execute('UPDATE key_table SET ip_add=NULL, port=NULL WHERE ip_add=?', (old_ip,))
    con.commit()

def ip_change(sig, new_ip, port):
    #Take a signature, find a hit on the SQL table, and then change its corresponding IP value to the new value.
    cur.execute('UPDATE key_table SET ip_add=?, port=? WHERE sig=?', (new_ip, port, sig))
    con.commit()

def decrypt(sig):
