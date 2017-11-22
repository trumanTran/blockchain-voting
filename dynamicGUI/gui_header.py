
import tkinter.messagebox
import csv

'''
#read from file
with open("test.txt", "r") as data:
    input = []
    for line in data:
        input.append(line)
'''
def body_text(label):
    label.config(font=("", 14))

def header_text(label):
    label.config(font=("", 26))

def configure(frame):
    for x in range(0, 3):
        frame.columnconfigure(x, weight=1)
    for y in range(0, 3):
        frame.rowconfigure(y, weight=1)

def enable(Entry, var, limit):
    if (var.get() > limit):
        Entry.config(state="normal")
    else:
        Entry.config(state='disabled')

def proceed(races, frameCount):
    races[frameCount].tkraise()
    frameCount += 1
    return frameCount

def navigate(races, fCount):
    global frameCount
    frameCount = fCount
    races[fCount].tkraise()

# confirm quitting the app
def quitCheck(x):
    answer = tkinter.messagebox.askquestion("YOU ARE ABOUT TO QUIT", "Are you sure you'd like to quit?")
    if answer == 'yes':
        x.quit()

def LoadCSV(CSVFileName):
    with open(CSVFileName, 'r') as f:
        reader = csv.reader(f)
        somelist = list(reader) #This actually loads the whole csv file.
        return somelist #Return entire list of lists object.
