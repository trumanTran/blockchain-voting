import csv
import os

#Name of CSV file must be in singular quotes (char type)
def LoadCSV(CSVFileName):
	with open(CSVFileName, 'r') as f:
		reader = csv.reader(f)
		somelist = list(reader) #This actually loads the whole csv file.
		return somelist #Return entire list of lists object.

"""CSV files should have the following format for insertion.
Each CSV file represents one 'race'.
CSV files must be in the following order per row: position, number of votes allowed, candidates (x many)."""
