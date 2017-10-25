import sqlite3
import os
import sys


#The goal is to create three entries on the table: The name of the person (hashed), the address of the person (also hashed), and a bool value that checks if they're registered or not.
#For the hash, a cryptographic hash would be optimal.

#We have to open the server connection first.
con = sqlite3.connect("something.db")
con.isolation_level = None
cur = con.cursor()
buffer = ""

def create_table(table_name, arg_count, arg_values):
    '''Takes a table name, a number of arguments count, and argument values.
    Argument values are used for the individual table columns.'''
    #TODO: SANITIZE INPUTS.
    #Create the table.
    arg_string = " ("
    for i in range (0, arg_count):
        #We have to process it as a string first.
        if i < (arg_count - 1):
            #If it is not the last argument in the string, insert a comma.
            arg_string += (arg_values[i] + ", ")
        elif i == (arg_count - 1):
            #If it is the last argument in the string, insert a closing parentheses and semicolon.
            arg_string += (arg_values[i] + ") ")
    cur.execute("CREATE TABLE " + table_name + arg_string)
    con.commit() #Commit changes
    #Now that we made the table and added the columns, we have to have functions to do other things like insert values.

def insert_entries(table_name, table_col_count, col_values):
    #We insert values in an entire block for a chosen table. Insert it as name of table,  a numerical length of list, and the list itself.
    #Insert values as a list. A format example is included.
	'''Example Insertion - Boolean values 
		Voters = [('Dlanod Pmurt', '527 th5 euneva', 'No'),
             ('Yrallih Notnilc', 'placesome', 'Yes'),
             ('Geedubya', 'Lonestar', 'No')]'''
    script_char = 'INSERT INTO ' + table_name + ' VALUES ('
    # We have to use ? and other methods to sanitize inputs. There is an else clause to reject the input.
    for i in range (table_col_count):
        if i < (table_col_count - 1):
            script_char += '?,'
        elif i == (table_col_count - 1):
            script_char += '?)'
        else:
            #Print error message.
            print "Bad Input. Rejecting..."
            #Reject input.
            return
    cur.executemany(script_char, col_values)
con.commit()

def insert_entry(table_name, table_col_count, col_values):
	#Function to insert a singular row into the table. ONLY INSERTS ONE ROW.
	#Initial sanitation of input. Designed to minimize chance of SQL injection.
	entry = (col_values,)
	#Insert the things into the table
	cur.execute('SELECT * FROM ' + table_name + ' WHERE symbol=?', entry)
	#now we have to finalize crap. Print out something to make sure it worked.
	print cur.fetchone()
	con.commit() #Commit changes
	
def hit_entry(table_name, num_args, target_col, hit_col):
	'''Check for a hit on the table for the specified columns. If it confirms a hit, confirm all specified columns for hit on that row.
	If there is any discrepency, let the sqlite wrapper handle it. We must check for every argument. num_args covers how many arguments are made.
	target_col specifies the targeted column for the argument (is a list). hit_col specifies the thing we want to check against the table's specified column.'''
	arg_spam = None
	for i in range (0, num_args):
		#Keep adding arguments. We're processing everything as a singular block.
		
	cur.executemany('SELECT * FROM ' + table_name + ' WHERE ' )
	'''not finished.'''
	
def create_voter_reg():
	#Runs the table creation with preset values already determined.
	table_args = ['name', 'address', 'hasvoted BOOLEAN NOT NULL'] #Arguments.
	create_table('voter_reg', 3, table_args) #Create the table.
	
def insert_voter(voter_name, voter_add):
	#Insert a new voter, with the last bool value being set to 'false'.
	insert_entry('voter_reg', voter_name, voter_add, 'false')
	#Each voter must be inserted manually, but there will be a bulk insertion method avaliable later when this is refined.
	
def check_voter(table_name, target_name, target_address):
	'''Simplified version of hit_entry that has predefined arguments.
	It will form a query that checks for a bool from two conditionals. If true, it will then do a check for validity (the 'voted' bool value).
	If the bool value is false, the voter did not vote yet, and it is set to true, and a 'true' (1) bool is returned.
	Else, the bool value is false (0). False is a rejection of voter, keep this in mind. Everything is case sensitive.'''
	arg_list = 'IF EXISTS ( SELECT 1 FROM ' + table_name + ' WHERE name=' + target_name + ' AND address=' + target_address + ' ) THEN CAST(1 AS BIT) ELSE CAST(0 AS BIT) END'
	#Cast as bit is used here to represent 'true' and 'false'.
	bool_val = cur.executemany(arg_list)
	if(bool_val == '1'): #Assuming a successful find...
		#Pass an argument that sets the bool column to true, and also confirm the voter can vote.
		'''Insert vote message passing thing here.'''
		cur.execute(something) #Execute bool change.
	elif(bool_val == '0'):
		#We got a wrong hit.
		'''Insert already voted message.'''
	else():
		#No hits on list, suspicious...
		'''Insert not registered voter message.'''
