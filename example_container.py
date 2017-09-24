import os
import sys

'''this is a container for the voting data. Hashing is not relevant to us at the moment.
the container should have an internal container containing their votes.
it should also have an equal and separate container that holds the politicians or whatever being voted for have their names listed.
Can hold multiple entries for different positions.
use position as a secondary measure to make sure everything is ready.

'''


class Vote:
    __ZipCode = None  # take zip-code for sorts involving this class object
    __VoteBlock = None  # Undefined list, first list is the 'race' being run, second is position, and third are chosen candidates.
    def __init__(self):
        self.__ZipCode = None
        self.__VoteBlock = None

    def insert_votes(self, block):
        # We use this function to modify the private values.
        # Need something to check that it is of type list of list of list, with multiple nested lists.
        self.__VoteBlock = block

    def insert_zip(self, zip):
        self.__ZipCode = zip

    def get_votes(self):
        return self.__VoteBlock

    def get_zip(self):
        return self.__ZipCode

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

    def alt_retrieve(self, race, position):
        return self.__VoteBlock[race+1][position+1]
        #Retrieves the actual thing, which is +1 because of the appended extra data.
    
    def alt_get_race(self, pos):
        return self.__VoteBlock[pos][0]

# Some test functions here
SomeBallot = Vote()
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

SomeBallot.insert_votes(insert_to_block())
'''Copy crap as an entire list of list of lists and store it in the object. Now we can pass it.
To actually get the values back for the race type and the positions in each race, you have to consult a completely separate list or list of lists.'''


'''Alternate method: store position 0 as the 'type' identifier (so [0] returns the race, [X][0] returns the position for that race, etc.
This takes less overall space as we are not repeating the same thing over each line
A more contemporary approach requires [race, position, name] type format for each entry.
We could use 'tuples' to mix-match our data, since it is immutable and after voting you don't want the votes changing.
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
        AltPos.append(PoliRace[i])
        for j in range (0, len(Positions[i])):
            AltChoices = []
            AltChoices.append(Positions[i][j])
            #Now fill in the relevant sections one chunk at a time.
            for k in range (0, len(VoterPicks[i][j][k])):
                AltChoices.append(VoterPicks[i][j][k])
            AltPos.append((list(AltChoices), AltChoices[0]))
            #Now continue appending.
        AltRace.append((list(AltPos), AltPos[0]))
    #Everything appended. Now return the value of the appended block.
    return AltRace
