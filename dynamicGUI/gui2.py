from tkinter import *
import tkinter.messagebox

# read from file
with open("test.txt", "r") as data:
    input = []
    for line in data:
        input.append(line)

# create main window
root = Tk()
#root.attributes("-fullscreen", True)
root.title("Voting Booth")

# values to keep track of new frames and votes
counter = 1  # current frame
frameCount = 2  # next frame
races = []  # list of all frames
limitations = []  # list of lists: [0(for one candidate ballots) or 1(for multiple), number of candidates the voter can vote for in one race]
votes = []  # list of lists of votes submitted by the voter
WriteInCandidates = []  # list of write-ins
allCandidates = [] # list of all other candidates

def body_text(label):
    label.config(font=("", 14))

def header_text(label):
    label.config(font=("", 36))

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

def proceed():
    global frameCount
    races[frameCount].tkraise()
    frameCount += 1
    return frameCount

def nextFrame(event):
    if (limitations[frameCount - 2][0] == 0):  # check if somebody voted in a one candidate race
        if votes[frameCount - 2][0].get() == 0:  # check if the voter awnts to omit their vote
            answer = tkinter.messagebox.askquestion("YOU ARE ABOUT TO OMIT YOUR VOTE",
                                                    "Are you sure you would like to omit your vote for this race?")
            if answer == 'yes':
                proceed()
        #check if the voter wants a write-in and actually wrote somebody in
        elif votes[frameCount - 2][0].get() == WriteInCandidates[frameCount - 2][1] and WriteInCandidates[frameCount - 2][0].get() == "":
            tkinter.messagebox.showinfo("NOTICE",
                                        "You did not provide a candidate for your write-in ballot")
        else:  # if they voted for somebody
            proceed()
    else:  # check the multiple candidate ballot
        # check if the voter wants a write-in and actually wrote somebody in
        if votes[frameCount - 2][len(votes[frameCount - 2])-1].get() == 1 and WriteInCandidates[frameCount - 2][0].get() == "":
            tkinter.messagebox.showinfo("NOTICE",
                                        "You did not provide a candidate for your write-in ballot")
        else:
            tally = 0
            for i in range(0, len(votes[frameCount - 2])):
                if votes[frameCount - 2][i].get() == 1:
                    tally += 1
            if tally > limitations[frameCount - 2][1]:  # if the voter over voted
                tkinter.messagebox.showinfo("NOTICE",
                                            "You have voted for more candidates than you are allowed to")
            elif (tally < limitations[frameCount - 2][1]):  # if the voter under voted
                answer = tkinter.messagebox.askquestion("YOU ARE ABOUT TO OMIT YOUR VOTE(S)",
                                                        "Are you sure you would like to omit one or more of your votes for this race?")
                if answer == 'yes':
                    proceed()
            else:  # if the voter villed out the proper amount votes
                proceed()

# create first frame and last frame
frame1 = Frame(root)
configure(frame1)
frame1.place(relx=0.5, rely=0.5, anchor="c", relwidth=1.0, relheight=1.0)  # add new frame to the window
races.append(frame1)

lastframe = Frame(root)
configure(lastframe)
lastframe.place(relx=0.5, rely=0.5, anchor="c", relwidth=1.0, relheight=1.0)  # add new frame to the window
races.append(lastframe)

# dynamically create ballot
for i in range(0, len(input)):  # read line by line where i is the line number
    input[i] = input[i].rstrip('\n')
    read = input[i].split(':')
    if (read[0] == 'races'):
        for y in range(0, (int)(read[1])):
            frame = Frame(root)  # create a new frame
            configure(frame)
            frame.place(relx=0.5, rely=0.5, anchor="c", relwidth=1.0, relheight=1.0)  # add new frame to the window
            races.insert(1, frame)
    elif i > 1:
        # create a frame to place in the center of the window
        subFrame = Frame(races[counter])
        subFrame.grid(row=1, column=1)

        # state the race
        header = Label(subFrame, text=read[0])
        header_text(header)
        header.pack()

        # give direction regarding the race
        directions = Label(subFrame, text='(Please' + read[1] + read[2] + ')')
        body_text(directions)
        directions.pack()

        # get list of candidates
        read[3] = read[3].strip()
        candidates = read[3].split(', ')
        candidates.append('')  # create a write in candidate space

        # structure the candidates into another frame
        candidateFrame = Frame(subFrame)
        candidateFrame.pack()

        # get limit of number of candidates that can be voted for
        limits=[0,0]
        limits[1] = (int)(read[2].strip())

        #write-in option creation
        WriteIn = Entry(candidateFrame, state="disabled")
        body_text(WriteIn)
        WriteInCandidates.append([WriteIn, len(candidates)])

        if (read[1] == ' Pick only'):  # if limited to only one candidate
            var = IntVar()
            votes.append([var])
            omit = Radiobutton(candidateFrame, text="OMIT", variable=votes[i - 2][0], value=0)
            body_text(omit)
            omit.grid(sticky=W, row=0)
            WriteIn.grid(row=len(candidates), padx=30)
            for q in range(0, len(candidates)):
                rb = Radiobutton(candidateFrame, text=candidates[q], variable=votes[i - 2][0], value=q + 1,
                                 command=lambda e=WriteInCandidates[i - 2][0], v=votes[i - 2][0], x=len(candidates) - 1:
                                 enable(e, v, x))
                body_text(rb)
                rb.grid(sticky=W, row=q + 1)
            limits[0] = 0

        else:  # if more than one candidate can be selected
            candidateValues = []
            WriteIn.grid(row=len(candidates) + 1, padx=30)
            for q in range(0, len(candidates)):
                temp = IntVar()
                candidateValues.append(temp)
                if (q < len(candidates) - 1):
                    cb = Checkbutton(candidateFrame, text=candidates[q], variable=candidateValues[q])
                else:
                    cb = Checkbutton(candidateFrame, text=candidates[q], variable=candidateValues[q],
                                     command=lambda e=WriteInCandidates[i - 2][0], v=candidateValues[q], x=0:
                                     enable(e,v,x))
                body_text(cb)
                cb.grid(sticky=W, row=q + 2)
            limits[0] = 1
            votes.append(candidateValues)
        limitations.append(limits)
        allCandidates.append(candidates)
        next = Button(subFrame, text="CONTINUE")
        body_text(next)
        next.bind('<Return>', nextFrame)
        next.bind('<Button-1>', nextFrame)
        next.pack()
        counter += 1
frame1.tkraise()

# get info from entries on login
def checkInfo(event):
    print("name: %s | address: %s" % (nameInfo.get(), addressInfo.get()))
    if (nameInfo.get() == "name" and addressInfo.get() == "address") or (
            nameInfo.get() == 'aa' and addressInfo.get() == 'bb'):  # whole line for testing
        # reset text boxes to blank and goto next frame
        print("valid")
        races[1].tkraise()
    else:
        tkinter.messagebox.showinfo("INVALID", "Your name or address are invalid")
        print("not valid")

# confirm quitting the app
def quitCheck():
    answer = tkinter.messagebox.askquestion("YOU ARE ABOUT TO QUIT", "Are you sure you'd like to quit?")
    if answer == 'yes':
        root.quit()

def reset(event):
    global frameCount
    frameCount = 2
    frame1.tkraise()

    for k in range(0, len(votes)):
        print("Race", k + 1, ": ", end="")
        for j in range(0, len(votes[k])):
            if (limitations[k][0] == 0):
                if (votes[k][j].get() == WriteInCandidates[k][1]):  # if a one candidate ballot write in
                    print(WriteInCandidates[k][0].get(), end="")
                else:
                    if votes[k][j].get() > 0:
                        print(allCandidates[k][j], " ", end="")
                    else:
                        print ('Omitted')
            elif (j == WriteInCandidates[k][1] - 1):  # if while checking a multiple candidate ballot and if checking the last option of a write in
                if (limitations[k][0] == 1):
                    if (votes[k][j].get() == 1):
                        print(WriteInCandidates[k][0].get(), end="")
            else:  # if checking  multiple candidate ballot and not yet checked the last option of a write in
                if votes[k][j].get() == 1:
                    print(allCandidates[k][j], " ", end="")
            votes[k][j].set(0)  # reset all buttons to false/unchecked
        print("")  # line separator for the ballots while printing
    # reset text entry fields
    for k in range(0, len(WriteInCandidates)):
        WriteInCandidates[k][0].delete(0, END)  # delete write-ins
        enable(WriteInCandidates[k][0], votes[k][0], WriteInCandidates[k][1])  #reset all text entries to disabled
    nameInfo.delete(0, END)  # delete name entry
    addressInfo.delete(0, END)  # delete address entry

    return frameCount


# frame 1
frame1_subFrame = Frame(frame1)
frame1_subFrame.grid(column=1, row=1)
# name and address labels
name = Label(frame1_subFrame, text="NAME")
address = Label(frame1_subFrame, text="ADDRESS")
welcome = Label(frame1, text="WELCOME")
body_text(name)
body_text(address)
header_text(welcome)
# entry boxes
nameInfo = Entry(frame1_subFrame)
addressInfo = Entry(frame1_subFrame)
body_text(nameInfo)
body_text(addressInfo)
# button definition
submit = Button(frame1, text="SUBMIT")
submit.bind('<Return>', checkInfo)
submit.bind('<Button-1>', checkInfo)
submit.config(width=30, bg='gray80')
quit = Button(frame1, text="QUIT", command=quitCheck)
body_text(submit)
body_text(quit)
# placement of widgets onto the first frame
welcome.grid(column=1, row=1, sticky=N)
name.grid(row=0, column=0, sticky=E)
address.grid(row=1, column=0, sticky=E)
nameInfo.grid(row=0, column=1, sticky=EW)
addressInfo.grid(row=1, column=1, sticky=EW)
submit.grid(row=1, column=1, sticky=S)
quit.grid(row=2, column=1, sticky=W)

# last frame
lastframe_SubFrame = Frame(lastframe)
lastframe_SubFrame.grid(column=1, row=1)
thanks = Label(lastframe_SubFrame, text="THANK YOU FOR VOTING")
header_text(thanks)
end = Button(lastframe_SubFrame, text="FINISH")
body_text(end)
end.bind('<Return>', reset)
end.bind('<Button-1>', reset)
thanks.pack()
end.pack()

root.mainloop()
