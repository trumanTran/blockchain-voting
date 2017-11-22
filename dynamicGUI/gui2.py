from tkinter import *
import tkinter.messagebox
import gui_header

#ballot = (["President", 1, "Johnny", 'Frank'], ['Mayor', 2, 'Me', 'Myself', 'I'])#johns_stuff.get_ballot()
ballot = gui_header.LoadCSV('Ballot.csv')
votes = []
WriteIns = []
limitations = []
all_frames = []
frameCount = 1

root = Tk()
#root.attributes("-fullscreen", True)
root.title("Voting Booth")
root.config(width = 600, height = 600)

# create first frame, confirmation page, last frame
LoginFrame = Frame(root)
confirmation_page = Frame(root)
lastFrame = Frame(root)

def proceed():
    global frameCount
    if frameCount < len(all_frames) - 1:
        all_frames[frameCount].tkraise()
        frameCount = frameCount + 1
    else:
        lastFrame.tkraise()
        frameCount = frameCount + 1

def check():
    global frameCount
    if limitations[frameCount - 2] == 1:
        if votes[frameCount - 2][0].get() == 0:
            answer = tkinter.messagebox.askquestion("YOU ARE ABOUT TO OMIT YOUR VOTE",
                                                    "Are you sure you would like to omit your vote for this race?")
            if answer == 'yes':
                proceed()
        else:
            proceed()
    else:
        counter = 0
        for i in range(0, len(votes[frameCount - 2])):
            if votes[frameCount - 2][i].get() == 1:
                counter += 1
        if counter > limitations[frameCount - 2]:
            tkinter.messagebox.showinfo("NOTICE", "You have voted for more candidates than you are allowed to")
        elif counter < limitations[frameCount - 2]:
            answer = tkinter.messagebox.askquestion("YOU ARE ABOUT TO OMIT YOUR VOTE(S)",
                                                    "Are you sure you would like to omit your vote(s) for this race?")
            if answer == 'yes':
                proceed()
        else:
            proceed()

def reset():
    global frameCount
    LoginFrame.tkraise()
    frameCount = 1
    # populate john's container
    for i in votes:
        for j in range(len(i)):
            i[j].set(0)
    print('broadcast') # send instance of John's container to the back end

# -------------------- login Frame --------------------
LoginFrame_subFrame = Frame(LoginFrame)
LoginFrame_subFrame.grid(column=1, row=1)
# name and address labels
name = Label(LoginFrame_subFrame, text="NAME")
address = Label(LoginFrame_subFrame, text="ADDRESS")
welcome = Label(LoginFrame, text="WELCOME")
# entry boxes
nameInfo = Entry(LoginFrame_subFrame)
addressInfo = Entry(LoginFrame_subFrame)
# button definition
submit = Button(LoginFrame, text="SUBMIT", command = proceed)
submit.config(width=30, bg='gray80')
quit = Button(LoginFrame, text="QUIT", command= lambda x = root: gui_header.quitCheck(x))
# placement of widgets onto the first frame
welcome.grid(column=1, row=1, sticky=N)
name.grid(row=0, column=0, sticky=E)
address.grid(row=1, column=0, sticky=E)
nameInfo.grid(row=0, column=1, sticky=EW)
addressInfo.grid(row=1, column=1, sticky=EW)
submit.grid(row=1, column=1, sticky=S)
quit.grid(row=2, column=1, sticky=W)
# -------------------- last frame --------------------
lastFrame_SubFrame = Frame(lastFrame)
lastFrame_SubFrame.grid(column=1, row=1)
thanks = Label(lastFrame_SubFrame, text="THANK YOU FOR VOTING")
end = Button(lastFrame_SubFrame, text="FINISH", command = reset)
# -------------------- confirmation page --------------------
confirmation_subframe = Frame(confirmation_page)
confirmation_subframe.grid(column = 1, row = 1)
confirm = Button(confirmation_subframe, text = 'confirm', command = proceed)
prompt = Label(confirmation_subframe, text = 'PLEASE CONFIRM')
# -------------------- placement of wigits --------------------
for i in [thanks, end, prompt, confirm]:
    i.pack()
# -------------------- placement of frames --------------------
for i in [LoginFrame, confirmation_page, lastFrame]:
    gui_header.configure(i)
    i.place(relx=0.5, rely=0.5, anchor="c", relwidth=1.0, relheight=1.0)  # add new frame to the window
    all_frames.append(i)
# -------------------- dynamically create ballot based off ballot tuple --------------------
for i in range(0,len(ballot)):
    ballot_entry = Frame(root) # frame for all information regarding one race
    gui_header.configure(ballot_entry)
    ballot_entry.place(relx=0.5, rely=0.5, anchor="c", relwidth=1.0, relheight=1.0)
    all_frames.insert(1, ballot_entry)
    subFrame = Frame(ballot_entry) # subframe for the general information to go
    candidateFrame = Frame(subFrame) # subfframe of subframe for the specific candidate entries
    subFrame.grid(row = 1, column = 1)
    raceText = Label(subFrame, text = ballot[i][0])
    nextButton = Button(subFrame, text = 'NEXT', command = check)
    directionsText = Label(subFrame, text="Please vote for " + (str)(ballot[i][1]))
    for iterator in (raceText, directionsText, candidateFrame, nextButton):
        iterator.pack()
    if ballot[i][1] == '1': # if a single candidate race
        notBlank = 0
        limitations.append(1)
        var = IntVar()
        votes.append([var])
        omit = Radiobutton(candidateFrame, text = 'Omit', variable = votes[i][0], value = 0)
        omit.grid(sticky = 'W', row = 0)
        wrb = Radiobutton(candidateFrame, variable=votes[i][0])
        wrb.grid(sticky='W', row=len(ballot[i]))
        writeIn = Entry(candidateFrame, state='disabled')
        writeIn.grid(sticky='W', row=len(ballot[i]), padx=30)
        WriteIns.append(writeIn)
        for j in range (2, len(ballot[i])):
            if ballot[i][j] != '':
                notBlank+=1
                rb = Radiobutton(candidateFrame, text = ballot[i][j], variable = votes[i][0], value = notBlank,
                                 command=lambda e=WriteIns[i], v=votes[i][0], x = len(ballot[i]) - 2:
                                 gui_header.enable(e, v, x))
                rb.grid(sticky = 'W', row = j-1)
        wrb.configure(value=notBlank + 1, command=lambda e=WriteIns[i], v=votes[i][0], x = notBlank:
                                         gui_header.enable(e, v, x))

    else: # if multiple candidates may be selected
        limitations.append((int)(ballot[i][1]))
        candidateArray = []
        for j in range (2, len(ballot[i])):
            if(ballot[i][j] != ''):
                var = IntVar()
                candidateArray.append(var)
                cb = Checkbutton(candidateFrame, text = ballot[i][j], variable = candidateArray[j-2])
                cb.grid(sticky = 'W', row = j - 2)
        # --- Write-in ---
        var = IntVar()
        candidateArray.append(var)
        writeIn = Entry(candidateFrame, state='disabled')
        WriteIns.append(writeIn)
        writeIn.grid(sticky='W', row=len(ballot[i]) - 1, padx=30)
        cb = Checkbutton(candidateFrame, variable = candidateArray[len(candidateArray)-1],
                         command=lambda e=WriteIns[i], v=candidateArray[len(candidateArray)-1], x=0:
                         gui_header.enable(e, v, x))
        cb.grid(sticky = 'W', row = len(ballot[i]) - 1)
        votes.append(candidateArray)
limitations.reverse()
votes.reverse()
LoginFrame.tkraise()
root.mainloop()
