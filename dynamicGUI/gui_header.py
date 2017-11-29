import tkinter.messagebox
import csv

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

def fillConfirmation(number, list, frame):
    if len(list) == 0:
        for i in range(number):
            tkinter.Label(frame, text='', font=("",12)).grid(row=i)
    else:
        counter = 0
        for i in range(len(list)):
            tkinter.Label(frame, text=list[i][0], font=("",12), bg = 'yellow').grid(row = counter, column = 0)
            counter+=1
            for j in range (1, len(list[i])):
                tkinter.Label(frame, text="                         "+list[i][j]+"                         ", font=("",12)).grid(row = counter, column = 0)
                counter+=1
