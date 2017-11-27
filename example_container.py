import os
import sys

'''this is a container for the voting data. Hashing is not relevant to us at the moment.
the container should have an internal container containing their votes.
it should also have an equal and separate container that holds the politicians or whatever being voted for have their names listed.
Can hold multiple entries for different positions.
use position as a secondary measure to make sure everything is ready.

'''


class Vote:
    __voterID = None  # take zip-code for sorts involving this class object
    __VoteBlock = None  # Undefined list, first list is the 'race' being run, second is position, and third are chosen candidates.

    def __init__(self):
        self.__voterID = None
        self.__VoteBlock = None

    def insert_votes(self, block):
        # We use this function to modify the private values.
        # Need something to check that it is of type list of list of list, with multiple nested lists.
        self.__VoteBlock = block

    def insert_id(self, id):
        self.__voterID = id

    def get_votes(self):
        return self.__VoteBlock

    def get_id(self):
        return self.__voterID

    def alt_retrieve(self, race, position):
        return self.__VoteBlock[race+1][position+1]
        #Retrieves the actual thing, which is +1 because of the appended extra data.

    def alt_get_race(self, pos):
        return self.__VoteBlock[pos][0]
	
    def alt_search_votes(self, name):
        #Combs data for hit just like above, ignores 'initial' position tag which is reserved for the race being participated in/the position.
        for i in range (0, len(self.__VoteBlock)):
            for j in range (1, len(self.__VoteBlock[i])):
                if(self.__VoteBlock[i][j] == name):
                    return True #Got a hit on the list of lists.
        #No hits found.
        return False
	
    def alt_print_votes(self):
        #Prints out everything in order, according to following formula - [Race/Position - People (seperated by commas)].
        #Each race and position is seperated by a new line. DESIGNED FOR THINGS OTHER THAN TUPLES.
        for i in range (0, len(self.__VoteBlock)):
            print(self.__VoteBlock[i][0] + " - ")
            for j in range (0, len(self.__VoteBlock[i])):
                if (j < len(self.__VoteBlock[i])):
                    print (self.__VoteBlock[i][j] + ", ")
                elif (j == len(self.__VoteBlock[i])):
                    print (self.__VoteBlock[i][j] + "." + "/n")
                #Should give rows that look like [Race, Position] - [Names] in rows per race/position pairing.
	
    def alt_print_tuple_votes(self):
        #Prints out everything in order, according to following formula - [Race/Position - People (seperated by commas)].
        #Each race and position is seperated by a new line.
        identitag = None
        for i in range (0, len(self.__VoteBlock)):
            if(identitag != self.VoteBlock[i][0][0]):
                #The third 0 is actually for the in-built tuple INSIDE the container, so a third 0 is needed to specify which part of the tuple we want.
                identitag = self.VoteBlock[i][0][0]
                print (identitag + "/n")
            print (self.VoteBlock[i][0][1] + " - ") #Prints the 'position' of the race. Since each position changes, there's no need for the identitag like above.
            for j in range (1, len(self.__VoteBlock[i])):
                #Since values for the race and position are stored as tuples, we do this the following way:
                #Print the first tuple object (the race) and keep going until the tuple object changes in some way. We need a value to host this.
                #This would be so much easier with a list of lists of lists, but whatever.
                if (j < len(self.__VoteBlock[i])):
                    print (self.VoteBlock[i][j] + ", ")
                elif (j == len(self.self.VoteBlock[i])):
                    print (self.VoteBlock[i][j] + "." + "/n")
					
# Some test functions here
#SomeBallot = Vote()
# Created a new ballot. Now, pass some random stuff to it.
# First we must create a simulated list of list of lists.
PoliRace = ["Law", "Local", "Unseen University"]
Positions = [["Judge", "Jury", "Executioner"], ["Mayor", "Deputy"], ["Bursar", "Archchancellor", "Librarian", "Dean"]]
VoterPicks = [[["Dredd", "Anderson", "Duncan Wu", "Tex", "Henderson"], ["Rigger", "Gobbet", "Walter"], ["Frank Castle", "Morgitz" , "Kharn", "Azrael"]],
                [["Light Yagami", "Totoro", "Alucard"], ["Touta Matsuda", "Simon", "Maria"]],
                [["A.A. Dinwiddie", "Johnathan"], ["Ridcully", "Krasus", "Shanoa", "Hestia"], ["Horace Worblehat", "Jaina", "Albert"], ["Two-Chairs", "Charlotte"]]] #Internal 'voter choices' list that pretends to be what the voter picked.

# We don't need the actual specific people they voted for, since we're providing the names manually.
# The above is to keep track of all the damned positions, race types, etc.

def insert_to_block():
    '''How this works is that choice is a string, but race and position are ints
       we use the specified ints to 'find' the location that its supposed to be in.'''
    PolRace = []  # The political race category specified
    #So we need to 'cycle' through the many positions located above in Positions. We do this one block at a time, so we don't have to keep declaring crap.
    for i in range (0, len(Positions)): #We need to go through the length of the positions list itself, not internal lists.
        PolPos = []  # The position to be determined
        for j in range (0, len(Positions[i])):  #Go through the current specified internal list.
            PolChoices = []  # The actual votes inputted
            for k in range (0, len(Positions[i][j])):
                #How this all works is we shove in our choices in the votes.
                # check it with the above 'positions' listing to retrieve values (master key).
                VoterChoices = VoterPicks
                PolChoices.append(VoterChoices[i][j][k])  #Appends the correct 'choices' for our voter. Adds all chosen ones. Limiter handled by some method. Assume the choices are 'wanted'.
            PolPos.append((list(PolChoices), PolChoices[0]))  #Make a new copy of the list calling the list constructor explicitly.
            PolChoices.clear()  #Clean it up explicitly so the next round could be done.
        PolRace.append((list(PolPos), PolPos[0]))  #Now make a new copy of the list of lists and shove it in.
        PolPos.clear()  #Clean up the list of lists after making a copy. Explicit call.
    return PolRace  #Return the stored values as a list of list of lists.

'''Alternate method: store position 0 as the 'type' identifier (so [0] returns the race and position.
This takes less overall space as we are not repeating the same thing over each line
Format is [Race, Position][Persons].
This means that it will be a list of lists of tuples, which will not be changeable after insertion.
'''
AltBallot = Vote() #Create a new class object.
AltPoliData = []
# We have to push in stuff manually using append.
def alt_insert_block():
    '''The way this is going to happen is we have to insert the beginning identifier tag in position zero of each of their respective lists.
    This can be done via tuples or generic list attributes.'''
    AltRace = [] #Empty container for now.
    for i in range (0, len(PoliRace)):
        AltPos = []
        #Now we must insert the thing into the container just made.
        for j in range (0, len(Positions[i])):
            AltPos.append((PoliRace[i] + ", " + Positions[i][j]))
            #Now fill in the relevant sections one chunk at a time.
            for k in range (0, len(VoterPicks[i][j][k])):
                AltPos.append(VoterPicks[i][j][k])
            AltRace.append((list(AltPos), AltPos[0]))
            #Now continue appending.
    #Everything appended. Now return the value of the appended block.
    return AltRace

#SomeBallot.insert_votes(alt_insert_block())
'''Copy crap as an entire list of list of lists and store it in the object. Now we can pass it.
To actually get the values back for the race type and the positions in each race, you have to consult a completely separate list or list of lists.'''


'''
    def get_data_pos(self, race, position): #Function that 'gets' the voter stuff at the specified race and position set.
        #Again, not real helpful by itself, but this is just a proof of concept. It returns a 'section' of the specified race and position (a list).
        return self.__VoteBlock[race][position]

    def search_votes_for_hit(self, name): #Function to 'comb' data by searching through a list of list of lists at O(n^3) complexity. Horribly inefficient.
        for i in range(0, len(self.__VoteBlock)):
            for j in range (0, len(self.__VoteBlock[i])):
                for k in range (0, len(self.__VoteBlock[i][j])):
                    if(self.__VoteBlock[i][j][k] == name):
                        return True #Found a hit, return the value.
        #End of the line, no hits found.
        return False

    def print_votes(self): #Special function that will print out everything in order. It will go through the list of lists of lists by lists.
        #This means it prints out entire swathes of people who were elected for a specific position.
        for i in range (0, len(self.__VoteBlock)):
            for j in range (0, len(self.__VoteBlock[i])):
                #Now print out the entire list stored in each position.
                print(self.__VoteBlock[i][j])
    #Functions beyond this point are for the 'secondary' method, where the info is the header for their relevant sections.
'''
