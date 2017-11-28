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

    def retrieve(self, race, position):
        return self.__VoteBlock[race+1][position+1]
        #Retrieves the actual thing, which is +1 because of the appended extra data.

    def get_race(self, pos):
        return self.__VoteBlock[pos][0]
	
    def search_votes(self, name):
        #Combs data for hit just like above, ignores 'initial' position tag which is reserved for the race being participated in/the position.
        for i in range (0, len(self.__VoteBlock)):
            for j in range (1, len(self.__VoteBlock[i])):
                if(self.__VoteBlock[i][j] == name):
                    return True #Got a hit on the list of lists.
        #No hits found.
        return False
	
    def print_votes(self):
        #Prints out everything in order, according to following formula - [Race/Position - People (seperated by commas)].
        #Each race and position is seperated by a new line. DESIGNED FOR THINGS OTHER THAN TUPLES.
        for i in range (0, len(self.__VoteBlock)):
            print(self.__VoteBlock[i][0] + " - ")
            for j in range (1, len(self.__VoteBlock[i])):
                if (j < len(self.__VoteBlock[i])):
                    print (self.__VoteBlock[i][j])
                elif (j == len(self.__VoteBlock[i])):
                    print (self.__VoteBlock[i][j] + "." + "/n")
                #Should give rows that look like [Race, Position] - [Names] in rows per race/position pairing.
