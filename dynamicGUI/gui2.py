from tkinter import *
import tkinter.messagebox
import os

#function to raise a frame
def raise_frame(frame):
    frame.tkraise()

#font definitions
def set_as_body_text(label):
    label.config(font = ("",14))

def set_as_top_text(label):
    label.config(font = ("", 36))

def configure(frame):
    for x in range(0, 3):
        frame.columnconfigure(x, weight=1)
    for y in range(0, 3):
        frame.rowconfigure(y, weight=1)
#read from file
with open("test.txt", "r") as data:
    input = []
    for line in data:
        input.append(line)

#create main window
root = Tk()
root.attributes("-fullscreen", True)
root.title("Voting Booth")

#values to keep track of new frames and votes
races = [] #list of all frames
counter = 1 #current frame
frameCount = 2 #next frame
ballotTypes = [] #if one candidate is expected or multiple
limitations = [] #list how many candidates are
votes = [] #list of lists of votes submitted by the voter

def nextFrame(event):
    global frameCount
    #check if somebody voted in a one candidate race
    if(ballotTypes[frameCount - 2] == 0):
        # check if the voter awnts to omit their vote
        if votes[frameCount - 2][0].get()==0:
            print ("bad Vote")
            answer = tkinter.messagebox.askquestion("YOU ARE ABOUT TO OMIT YOUR VOTE",
                                                    "Are you sure you would like to omit your vote for this race?")
            if answer == 'yes':
                raise_frame(races[frameCount])
                frameCount += 1
        else:
            raise_frame(races[frameCount])
            frameCount += 1
    else:
        #check the multiple candidate ballot
        tally = 0
        for i in range (0, len(votes[frameCount - 2])):
            if votes[frameCount - 2][i].get() == 1:
                tally += 1
        if tally > limitations[frameCount - 2]: #if the voter over voted
            tkinter.messagebox.showinfo("NOTICE",
                                        "You have voted for more candidates than you are supposed to")
            print ("invalid vote")
        elif(tally < limitations[frameCount - 2]): #if the voter under voted
            print ("less votes")
            answer = tkinter.messagebox.askquestion("YOU ARE ABOUT TO OMIT SOME VOTES",
                                                    "Are you sure you would like to omit some of your votes?")
            if answer == 'yes':
                raise_frame(races[frameCount])
                frameCount += 1
        else: #if the voter villed out the proper amount votes
            raise_frame(races[frameCount])
            frameCount += 1

    return frameCount

#create first frame and last frame
frame1 = Frame(root)
configure(frame1)
frame1.place(relx=0.5, rely=0.5, anchor="c", relwidth=1.0, relheight=1.0)  # add new frame to the window
races.append(frame1)

lastframe = Frame(root)
configure(lastframe)
lastframe.place(relx=0.5, rely=0.5, anchor="c", relwidth=1.0, relheight=1.0)  # add new frame to the window
races.append(lastframe)

#dynamically create ballot
for i in range(0, len(input)): #read line by line where i is the line number
    input[i] = input[i].rstrip('\n')
    read = input[i].split(':')
    if(read[0] == 'races'):
        for y in range(0, (int)(read[1])):
            frame = Frame(root) #create a new frame
            configure(frame)
            frame.place(relx=0.5, rely=0.5, anchor="c", relwidth=1.0, relheight=1.0)  # add new frame to the window
            races.insert (1, frame)
    elif i > 1:
        #create a frame to place in the center of the window
        subFrame = Frame(races[counter])
        subFrame.grid(row = 1, column = 1)

        #state the race
        header = Label(subFrame, text = read[0])
        set_as_top_text(header)
        header.pack()

        #give direction regarding the race
        directions = Label(subFrame, text = read[1] + read[2])
        set_as_body_text(directions)
        directions.pack()

        #get list of candidates
        read[3] = read[3].strip()
        candidates = read[3].split(', ')

        #structure the candidates into another frame
        candidateFrame = Frame(subFrame)
        candidateFrame.pack()

        #get limit of number of candidates that can be voted for
        limitations.append((int)(read[2].strip()))

        if(read[1] == ' Pick only'):
            var = IntVar()
            oneCandidateList = [var]
            votes.append(oneCandidateList)
            for q in range (0, len(candidates)):
                rb = Radiobutton(candidateFrame, text = candidates[q], variable = votes[i-2][0], value = q+1)
                set_as_body_text(rb)
                rb.grid(sticky = W)
            ballotTypes.append(0)
        else:
            candidateValues = []
            for q in range (0, len(candidates)):
                temp = IntVar()
                candidateValues.append(temp)
                cb = Checkbutton(candidateFrame, text = candidates[q], variable = candidateValues[q])
                set_as_body_text(cb)
                cb.grid(sticky = W)
            ballotTypes.append(1)
            votes.append(candidateValues)

        next = Button(subFrame, text = "CONTINUE")
        set_as_body_text(next)
        next.bind('<Return>', nextFrame)
        next.bind('<Button-1>', nextFrame)
        next.pack()
        counter += 1

raise_frame(frame1)

#get info from entries
def checkInfo(event):
    print("name: %s | address: %s" % ( nameInfo.get(), addressInfo.get() ) )
    if (nameInfo.get() == "name" and addressInfo.get() == "address")or(nameInfo.get()=='aa' and addressInfo.get() == 'bb'): #whole line for testing
        #reset text boxes to blank and goto next frame
        print ("valid")
        raise_frame(races[1])
    else:
        tkinter.messagebox.showinfo("INVALID", "Your name or address are invalid")
        print("not valid")

#confirm quitting the app
def quitCheck():
    answer = tkinter.messagebox.askquestion("YOU ARE ABOUT TO QUIT", "Are you sure you'd like to quit?")
    if answer == 'yes':
        root.quit()

def reset(event):
    global frameCount
    frameCount=2
    raise_frame(frame1)

    for k in range (0, len(votes)):
        for j in range (0, len(votes[k])):
            print(votes[k][j].get()) #print ballots on terminal
            votes[k][j].set(0) #reset all buttons to false/unchecked
        print ("_____________") #separator for the ballots while printing

    #reset text entry fields
    nameInfo.delete(0, END)
    addressInfo.delete(0, END)

    return frameCount

#frame 1
frame1_subFrame = Frame(frame1)
frame1_subFrame.grid(column = 1, row = 1)

#name and address labels
name = Label(frame1_subFrame, text = "NAME")
address = Label(frame1_subFrame, text = "ADDRESS")
welcome = Label(frame1, text = "WELCOME")
set_as_body_text(name)
set_as_body_text(address)
set_as_top_text(welcome)

#entry boxes
nameInfo = Entry(frame1_subFrame)
addressInfo = Entry(frame1_subFrame)
set_as_body_text(nameInfo)
set_as_body_text(addressInfo)

#button definition
submit = Button(frame1, text = "SUBMIT")
submit.bind('<Return>', checkInfo)
submit.bind('<Button-1>', checkInfo)
submit.config(width = 30, bg = 'gray80')
quit = Button(frame1, text = "QUIT", command = quitCheck)
set_as_body_text(submit)
set_as_body_text(quit)

#placement of widgets onto the first frame
welcome.grid(column = 1, row = 1, sticky = N)
name.grid(row = 0, column = 0, sticky=E)
address.grid(row = 1, column = 0, sticky=E)
nameInfo.grid(row = 0, column = 1, sticky = EW)
addressInfo.grid(row = 1, column = 1, sticky = EW)
submit.grid(row = 1, column = 1, sticky = S)
quit.grid(row=2, column = 1, sticky = W)

#last frame
lastframe_SubFrame = Frame(lastframe)
lastframe_SubFrame.grid(column = 1, row = 1)
thanks = Label(lastframe_SubFrame, text = "THANK YOU FOR VOTING")
set_as_top_text(thanks)
end = Button(lastframe_SubFrame, text = "FINISH")
set_as_body_text(end)
end.bind('<Return>', reset)
end.bind('<Button-1>', reset)
thanks.pack()
end.pack()

root.mainloop()
