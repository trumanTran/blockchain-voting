import sqlite3
import os
import sys

#We have to open the server connection first.
con = sqlite3.connect("nodekey.db")
con.isolation_level = None
cur = con.cursor()
buffer = ""

"""Needed are the ip address, the machid, and the public key (per node)"""

def create_key_table():
    #This function only has one job: make the key table.
    #It has columns for the ip address, the machid, and the public key.
    cur.execute('CREATE TABLE IF NOT EXISTS key_table (mid TEXT UNIQUE NOT NULL, pub_key TEXT UNIQUE NOT NULL, ip_add TEXT UNIQUE, port TEXT UNIQUE)')
    #Table created.

def insert_to_key_table(mid, ip_add, port, pub_key):
    #Insert to the key table the values above.
    cur.execute('INSERT INTO key_table VALUES (?,?,?,?)', (mid, pub_key, ip_add, port))
    con.commit()

def mass_insert_keys(key_list):
    #Inserts a bunch of values from a list of tuples.
    for i in range (0, len(key_list)):
        insert_to_key_table(key_list[i][0],key_list[i][1],key_list[i][2],key_list[i][3])
    #All things inserted.

def CSV_Insert_Keys(file_name):
    #Takes entire file and loads as a list of tuples. Resulting list is used with mass_insert_keys.
    '''file must be in the following format:
        machine id, ip address, port, public key'''
    with open (file_name, 'r') as file:
        reader = csv.reader(file)
        k_list = list(reader)
        mass_insert_keys(k_list)
    #Insertion Finished.

def set_disconnect(old_ip):
    #Function to 'clean' the ip address field until the machine reconnects using the appropriate machid.
    cur.execute('UPDATE key_table SET ip_add=NULL, port=NULL WHERE ip_add=?', (old_ip,))
    con.commit()

def ip_change(mid, new_ip):
    #Take a machid, find a hit on the SQL table, and then change its corresponding IP value to the new value.
    cur.execute('UPDATE key_table SET ip_add=? WHERE mid=?', (new_ip, mid))
    con.commit()

def port_change(mid, new_port):
    #Takes a machid, finds it on the SQL table, and changes corresponding port value.
    cur.execute('UPDATE key_table SET port=? WHERE mid=?', (new_port, mid))
    con.commit()

def ip_update(mid, new_ip):
    #Checks if the current ip needs updating, and updates it if necessary.
    cur.execute('SELECT * FROM key_table WHERE mid=? AND ip_add=?', (mid, new_ip))
    row = cur.fetchone()
    if row is None:
        #No match. Update it.
        ip_change(mid, new_ip)

def port_update(mid, new_port):
    #Checks if the current port needs updating, and updates it if necessary.
    cur.execute('SELECT * FROM key_table WHERE mid=? AND port=?', (mid, new_port))
    row = cur.fetchone()
    if row is None:
        #No match. Update it.
        port_change(mid, new_port)

def decrypt(mid):
    #Function that takes a machid from the sending block, checks the table for the public key corresponding to that block, and returns the value.
    cur.execute('SELECT pub_key FROM key_table WHERE mid=?', (mid,))
    #Now that we have the argument selected, we have to retrieve its value using fetch.
    return cur.fetchone() #BEWARE! ALL VALUES ARE RETURNED AS TUPLES! THEY ARE IMMUTABLE!

def delete_entry(mid):
    #Function to select a node's entries by machid, for node removal.
    cur.execute('DELETE FROM key_table WHERE mid=?', (mid,))
    #Deletes the node's entry. Since the node's actual entry does not exist anymore, it functionally stops them from sending useful data or having data sent to them.

def find_node_ips():
    #This is for the broadcast function. It recalls ALL IPS CURRENTLY LISTED and returns the entire column of ips as a list of tuples. Access as if it were a list, since the column is literally one width wide.
    cur.execute('SELECT ip_add FROM key_table')
    return cur.fetchall()

def find_mid(mid):
    #Finds a mach id and returns if its there or not.
    cur.execute('SELECT mid FROM key_table WHERE mid=?', (mid,))
    row = cur.fetchone()
    if row is not None:
    #we found a match.
        return True
    else:
        return False

def match_connection(mid, key):
    #Finds if there is a matching machid and key.
    cur.execute('SELECT * FROM key_table WHERE mid=? AND pub_key=?', (mid, key))
    row = cur.fetchone()
    if row is not None:
    #found match.
        return True
    else:
        return False

"""Table Creation"""
create_key_table()
#Now we create some fake values for testing.
#some_key_list = [('red', 1.212.3.34, 'someencrypt.pem'),('black', 8.42.144.32, 'starplatinum.pem'),('blue', 73.2.2.44:2918, 'theworld.pem'),('yellow', 84.24.1.43, 'thehangedman.pem'),('white', 323.43.1.54, 'hatemachine.pem')]
#mass_insert_into_table(key_list)
#print find_node_ips;
    #Takes a machid, finds it on the SQL table, and changes corresponding port value.
    cur.execute('UPDATE key_table SET port=? WHERE mid=?', (new_port, mid))
    con.commit()

def ip_update(mid, new_ip):
    #Checks if the current ip needs updating, and updates it if necessary.
    cur.execute('SELECT * FROM key_table WHERE mid=? AND ip_add=?', (mid, new_ip))
    row = cur.fetchone()
    if row is None:
        #No match. Update it.
        ip_change(mid, new_ip)

def port_update(mid, new_port):
    #Checks if the current port needs updating, and updates it if necessary.
    cur.execute('SELECT * FROM key_table WHERE mid=? AND port=?', (mid, new_port))
    row = cur.fetchone()
    if row is None:
        #No match. Update it.
        port_change(mid, new_port)

def decrypt(mid):
    #Function that takes a machid from the sending block, checks the table for the public key corresponding to that block, and returns the value.
    cur.execute('SELECT pub_key FROM key_table WHERE mid=?', (mid,))
    #Now that we have the argument selected, we have to retrieve its value using fetch.
    return cur.fetchone() #BEWARE! ALL VALUES ARE RETURNED AS TUPLES! THEY ARE IMMUTABLE!

def delete_entry(mid):
    #Function to select a node's entries by machid, for node removal.
    cur.execute('DELETE FROM key_table WHERE mid=?', (mid,))
    #Deletes the node's entry. Since the node's actual entry does not exist anymore, it functionally stops them from sending useful data or having data sent to them.

def find_node_ips():
    #This is for the broadcast function. It recalls ALL IPS CURRENTLY LISTED and returns the entire column of ips as a list of tuples. Access as if it were a list, since the column is literally one width wide.
    cur.execute('SELECT ip_add FROM key_table')
    return cur.fetchall()

def find_mid(mid):
    #Finds a mach id and returns if its there or not.
    cur.execute('SELECT mid FROM key_table WHERE mid=?', (mid,))
    row = cur.fetchone()
    if row is not None:
    #we found a match.
        return True
    else:
        return False

def match_connection(mid, key):
    #Finds if there is a matching machid and key.
    cur.execute('SELECT * FROM key_table WHERE mid=? AND pub_key=?', (mid, key))
    row = cur.fetchone()
    if row is not None:
    #found match.
        return True
    else:
        return False

"""Table Creation"""
create_key_table()
#Now we create some fake values for testing.
#some_key_list = [('red', 1.212.3.34, 'someencrypt.pem'),('black', 8.42.144.32, 'starplatinum.pem'),('blue', 73.2.2.44:2918, 'theworld.pem'),('yellow', 84.24.1.43, 'thehangedman.pem'),('white', 323.43.1.54, 'hatemachine.pem')]
#mass_insert_into_table(key_list)
#print find_node_ips;
