from tkinter import *
import tkinter.messagebox
import gui_header
import VotingContainer
import SQLVoterTable
import blockchain
import os
# ---------------------------------------------------------------------------------------------------------------------
# ------------------------------------------- Initialize Local Variables ----------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------
ballot = gui_header.LoadCSV('Ballot.csv')
votes = []
WriteInEntries = []
limitations = []
all_frames = []
compiledBallot = []
frameCount = 1
block = VotingContainer.Vote
stationId = 1234 #Station ID
blockToAdd = None
# ---------------------------------------------------------------------------------------------------------------------
# ------------------------------------------- Initialize Local Tables Once --------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------
SQLVoterTable.create_voter_reg()
SQLVoterTable.CSV_Load_Voters('NamesAddresses.csv')
# ---------------------------------------------------------------------------------------------------------------------
# ---------------------------------------------- Initialize Blockchain ------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------
#during actual initialization, genesis_block will be set equal to the genesis block given by central server
#central server will be the one to call create_genesis_block() and send that to all nodes
genesisBlock = blockchain.create_genesis_block()
#machine will create its own local blockchain utilizing the genesis block given
blockchain.create_new_chain(genesisBlock)
# ---------------------------------------------------------------------------------------------------------------------
# ---------------------------------------------- Root Window declaration ----------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------
root = Tk()
#root.attributes("-fullscreen", True)
root.title("Voting Booth")
root.config(width = 600, height = 600)
# ---------------------------------------------------------------------------------------------------------------------
# -------------------------------- create first frame, confirmation page, last frame ----------------------------------
# ---------------------------------------------------------------------------------------------------------------------
LoginFrame = Frame(root)
confirmation_page = Frame(root)
lastFrame = Frame(root)
# ---------------------------------------------------------------------------------------------------------------------
# -------------------------------------------- Local function definaitions --------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------
def proceed():
    global frameCount
    if frameCount < len(all_frames) - 1:
        all_frames[frameCount].tkraise()
        frameCount = frameCount + 1
    else:
        lastFrame.tkraise()
        frameCount = frameCount + 1
    return TRUE

def lessCheck(counter):
    if counter < limitations[frameCount - 2][0]:
        answer = tkinter.messagebox.askquestion("YOU ARE ABOUT TO OMIT YOUR VOTE(S)",
                                                "Are you sure you would like to omit "+(str)(limitations[frameCount-2][0]-counter)+" vote(s) for this race?")
        if answer == 'yes':
            WriteInEntries[len(WriteInEntries) - frameCount + 1].config(state='disabled')
            return proceed()
	else:
	    return FALSE
    else:
        WriteInEntries[len(WriteInEntries) - frameCount + 1].config(state='disabled')
        return proceed()

def populate():
    global frameCount
    for i in range(0, len(votes)):
        if limitations[i][0] > 1:
            counter = 0
            for j in range(len(votes[i])):
                if votes[i][len(votes[i]) - 1].get() == 1 and counter == 0:
                    compiledBallot[i].append(WriteInEntries[len(WriteInEntries) - 1 - i].get())
                    counter += 1
                elif votes[i][j].get() == 1 and j < len(votes[i])-1 :
                    compiledBallot[i].append(ballot[i][j + 2])
                    counter += 1
            while counter < limitations[i][0]:
                counter += 1
                compiledBallot[i].append('Omitted')
        else:
            if votes[i][0].get() > 0:
                if votes[i][0].get() == limitations[i][1]:
                    compiledBallot[i].append(WriteInEntries[len(WriteInEntries) - 1 - i].get())
                else:
                    compiledBallot[i].append(ballot[i][votes[i][0].get() + 1])
            else:
                compiledBallot[i].append('Omitted')
    #print(compiledBallot)  # send instance of John's container to the back end
    block.set_votes(block, compiledBallot)
    block.set_id(block, nameInfo.get() + addressInfo.get())

def check(confirmation):
    global frameCount
    progress = FALSE
    if limitations[frameCount - 2][0] == 1:
        if votes[frameCount - 2][0].get() == 0:
            answer = tkinter.messagebox.askquestion("YOU ARE ABOUT TO OMIT YOUR VOTE",
                                                    "Are you sure you would like to omit your vote for this race?")
            if answer == 'yes':
                WriteInEntries[len(WriteInEntries) - frameCount + 1].config(state='disabled')
                progress = proceed()
        else:
            if votes[frameCount - 2][0].get() == limitations[frameCount - 2][1]:
                if (WriteInEntries[len(WriteInEntries) - frameCount + 1].get()).strip() == '':
                    tkinter.messagebox.showinfo("NOTICE", "The Write-In ballot has been left blank")
                else:
                    WriteInEntries[len(WriteInEntries) - frameCount + 1].config(state='disabled')
                    progress = proceed()
            else:
                WriteInEntries[len(WriteInEntries) - frameCount + 1].config(state='disabled')
                progress = proceed()
    else:
        counter = 0
        for i in range(0, len(votes[frameCount - 2])):
            if votes[frameCount - 2][i].get() == 1:
                counter += 1
        if counter > limitations[frameCount - 2][0]:
            tkinter.messagebox.showinfo("NOTICE", "You have voted for more candidates than you are allowed to")

        elif (votes[frameCount - 2][limitations[frameCount - 2][1] - 1].get() == 1):
            if (WriteInEntries[len(WriteInEntries) - frameCount + 1].get()).strip() == '':
                tkinter.messagebox.showinfo("NOTICE", "The Write-In ballot has been left blank")
            else:
                progress = lessCheck(counter)
        else:
            progress = lessCheck(counter)
    if confirmation == 1 and progress == TRUE:
        populate()
        gui_header.fillConfirmation(0, compiledBallot, canvasFrame)

def appendBlock():
    global blockToAdd
    index = len(blockchain.chain)
    currentBallot = block.get_votes(block)
    #set blockToAdd to the proposed block containing the current voter's ballot
    blockToAdd = blockchain.next_block(stationId, currentBallot)
    #This is where we should first broadcast block or otherwise check to see if we accept block from another node
	#For the time being, check whether previous hash of broadcast node is equal to latest block's current hash 
    #Once ready, node will append block to local blockchain
    if (blockToAdd.previous_hash == blockchain.chain[index-1].hash):
        blockchain.append_block(blockToAdd)
    print("Machine ID: ", blockchain.chain[index].machine_id)
    print("Time: ", blockchain.chain[index].timestamp)
    print("Ballot: ", blockchain.chain[index].data)
    print("Current Hash: ", blockchain.chain[index].hash)
    print("Previous Hash: ", blockchain.chain[index].previous_hash, "\n")
    proceed()

def printOut():
    open("file.txt", 'w').close
    file = open("file.txt", 'w+')
    for i in range(0,len(compiledBallot)):
        string = (str)(compiledBallot[i]) + '\n'
        file.write(string)
    file.close()
    startfile("file.txt", "print")
	
def reset():
    global frameCount
    #printOut()
    LoginFrame.tkraise()
    frameCount = 1
    for i in range(0, len(votes)):
        for j in range(len(votes[i])):
            votes[i][j].set(0)
    for entry in WriteInEntries:
        var = IntVar(0)
        gui_header.enable(entry, var, -1)
        entry.delete(0, END)
        gui_header.enable(entry, var, 1)
    nameInfo.delete(0, END)
    addressInfo.delete(0, END)
    for i in compiledBallot:
        for j in range(1, len(i)):
            del i[1]

def configureCanvas(event):
    canvas.configure(scrollregion=canvas.bbox("all"), width=500, height=500)

def changeVote():
    global frameCount
    frameCount = 1
    for i in compiledBallot:
        for j in range(1,len(i)):
            del i[1]
    for entry in WriteInEntries:
        var = IntVar(0)
        gui_header.enable(entry, var, -1)

    proceed()

def validate():
        if SQLVoterTable.check_voter(nameInfo.get(), addressInfo.get()):
            proceed()
# ---------------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------- login Frame ----------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------
LoginFrame_subFrame = Frame(LoginFrame)
LoginFrame_subFrame.grid(column=1, row=1)
# ----- name and address labels -----
name = Label(LoginFrame_subFrame, text="NAME", font=("",12))
address = Label(LoginFrame_subFrame, text="ADDRESS", font=("",12))
welcome = Label(LoginFrame, text="WELCOME", font=("",18))
# ----- entry boxes -----
nameInfo = Entry(LoginFrame_subFrame, font=("",12))
addressInfo = Entry(LoginFrame_subFrame, font=("",12))
# ----- button definition -----
submit = Button(LoginFrame, text="SUBMIT", command = validate, font=("",14))
submit.config(width=30, bg='gray80')
quit = Button(LoginFrame, text="QUIT", command= lambda x = root: gui_header.quitCheck(x))
# ----- placement of widgets onto the first frame -----
welcome.grid(column=1, row=1, sticky=N)
name.grid(row=0, column=0, sticky=E)
address.grid(row=1, column=0, sticky=E)
nameInfo.grid(row=0, column=1, sticky=EW)
addressInfo.grid(row=1, column=1, sticky=EW)
submit.grid(row=1, column=1, sticky=S)
quit.grid(row=2, column=1, sticky=W)
# ---------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------- Last frame ----------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------
lastFrame_SubFrame = Frame(lastFrame)
lastFrame_SubFrame.grid(column=1, row=1)
thanks = Label(lastFrame_SubFrame, text="THANK YOU FOR VOTING", font=("",14))
end = Button(lastFrame_SubFrame, text="FINISH", command = reset, font=("",14))
# ---------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------- Confirmation page -------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------
confirmation_subframe = Frame(confirmation_page)
confirmation_subframe.grid(column=1, row=1)
confirm = Button(confirmation_subframe, text='CONFIRM', command=appendBlock)
redo = Button(confirmation_subframe, text='CHANGE', command=changeVote)
prompt = Label(confirmation_subframe, text='PLEASE CONFIRM', font=("",14))
# ----- Scrollbar in case the entries in a ballot extend off screen -----
myscrollbar=Scrollbar(confirmation_subframe,orient="vertical")
canvas=Canvas(confirmation_subframe)
canvas.configure(yscrollcommand=myscrollbar.set)
canvasFrame=Frame(canvas)
myscrollbar.config(command=canvas.yview)
myscrollbar.pack(side="right",fill="y")
canvas.create_window((250,0),window=canvasFrame,anchor='n')
canvas.bind("<Configure>",configureCanvas)
# ---------------------------------------------------------------------------------------------------------------------
# ------------------------------------------- Placement of wigits and frames ------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------
for i in [thanks, end, prompt, canvas]:
    i.pack()
confirm.pack(side='right')
redo.pack(side='left')
for i in [LoginFrame, confirmation_page, lastFrame]:
    gui_header.configure(i)
    i.place(relx=0.5, rely=0.5, anchor="c", relwidth=1.0, relheight=1.0)  # add new frame to the window
    all_frames.append(i)
# ---------------------------------------------------------------------------------------------------------------------
# ---------------------------------- Dynamically create ballot based off ballot tuple ---------------------------------
# ---------------------------------------------------------------------------------------------------------------------
for i in range(0,len(ballot)):
    ballot_entry = Frame(root) # frame for all information regarding one race
    gui_header.configure(ballot_entry)
    ballot_entry.place(relx=0.5, rely=0.5, anchor="c", relwidth=1.0, relheight=1.0)
    all_frames.insert(1, ballot_entry)
    subFrame = Frame(ballot_entry) # subframe for the general information to go
    candidateFrame = Frame(subFrame) # subfframe of subframe for the specific candidate entries
    subFrame.grid(row = 1, column = 1)
    raceText = Label(subFrame, text = ballot[i][0], font=("",14))
    compiledBallot.append([ballot[i][0]])
    nextButton = Button(subFrame, text = 'NEXT', command = lambda x = 0: check(x))
    if i == 0:
        nextButton.config(command = lambda x = 1: check(x))
    directionsText = Label(subFrame, text="Please vote for " + (str)(ballot[i][1]), font=("",10))
    for iterator in (raceText, directionsText, candidateFrame, nextButton):
        iterator.pack()
    limit = [0, 0] # Allowed vote, number of candidates
    writeIn = Entry(candidateFrame, state='disabled', font=("", 12))
    WriteInEntries.append(writeIn)
    if ballot[i][1] == '1': # if a single candidate race
        limit[0] = 1
        var = IntVar()
        votes.append([var])
        omit = Radiobutton(candidateFrame, text = 'Omit', variable = votes[i][0], value = 0, font=("",12))
        omit.grid(sticky = 'W', row = 0)
        wrb = Radiobutton(candidateFrame, variable=votes[i][0], font=("",12))
        wrb.grid(sticky='W', row=len(ballot[i]))
        writeIn.grid(sticky='W', row=len(ballot[i]), padx=28)
        for j in range (2, len(ballot[i])):
            if ballot[i][j] != '':
                limit[1]+=1
                rb = Radiobutton(candidateFrame, text = ballot[i][j], variable = votes[i][0], value = limit[1], font=("",12),
                                 command=lambda e=WriteInEntries[i], v=votes[i][0], x = len(ballot[i]) - 2:
                                 gui_header.enable(e, v, x))
                rb.grid(sticky = 'W', row = j-1)
        wrb.configure(value=limit[1] + 1, command=lambda e=WriteInEntries[i], v=votes[i][0], x = limit[1]:
                                         gui_header.enable(e, v, x))
        limit[1]+=1
    else: # if multiple candidates can be selected
        limit[0] = ((int)(ballot[i][1]))
        candidateArray = []
        for j in range (2, len(ballot[i])):
            if(ballot[i][j] != ''):
                var = IntVar()
                candidateArray.append(var)
                cb = Checkbutton(candidateFrame, text = ballot[i][j], variable = candidateArray[j-2], font=("",12))
                cb.grid(sticky = 'W', row = j - 2)
                limit[1]+=1
        # --- Write-in ---
        var = IntVar()
        candidateArray.append(var)
        writeIn.grid(sticky='W', row=len(ballot[i]) - 1, padx=28)
        cb = Checkbutton(candidateFrame, variable = candidateArray[len(candidateArray)-1], font=("",12),
                         command=lambda e=WriteInEntries[i], v=candidateArray[len(candidateArray)-1], x=0:
                         gui_header.enable(e, v, x))
        limit[1]+=1
        cb.grid(sticky = 'W', row = len(ballot[i]) - 1)
        votes.append(candidateArray)
    limitations.append(limit)
# ---------------------------------------------------------------------------------------------------------------------
# ------------------------------------ Populate confirmation list with blank space ------------------------------------
# ---------------------------------------------------------------------------------------------------------------------
listRowNumber = len(ballot)
for i in range(len(limitations)):
    listRowNumber = listRowNumber + limitations[i][0]
gui_header.fillConfirmation(listRowNumber, [], canvasFrame)
# ---------------------------------------------------------------------------------------------------------------------
# -------------------------------------- Flip around lists to match output of GUI -------------------------------------
# ---------------------------------------------------------------------------------------------------------------------
limitations.reverse()
votes.reverse()
ballot.reverse()
compiledBallot.reverse()
LoginFrame.tkraise()
root.mainloop()
