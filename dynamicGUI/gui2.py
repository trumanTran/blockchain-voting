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

#read from file
with open("test.txt", "r") as data:
    input = []
    for line in data:
        input.append(line)

#create main window
root = Tk()
root.attributes("-fullscreen", True)
root.title("Voting Booth")

#keep track of new frames
races = []
counter = 1
a = 2

def nextFrame1():
    global a
    raise_frame(races[a])
    a += 1
    return a

def configure(frame):
    for x in range(0, 3):
        frame.columnconfigure(x, weight=1)
    for y in range(0, 3):
        frame.rowconfigure(y, weight=1)


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
for i in range(0, len(input)):
    input[i] = input[i].rstrip('\n')
    read = input[i].split(':')
    if(read[0] == 'races'):
        for y in range(0, (int)(read[1])):
            frame = Frame(root) #create a new frame
            configure(frame)
            frame.place(relx=0.5, rely=0.5, anchor="c", relwidth=1.0, relheight=1.0)  # add new frame to the window
            races.insert (1, frame)
    elif i > 1:
        subFrame = Frame(races[counter])
        subFrame.grid(row = 1, column = 1)
        header = Label(subFrame, text = read[0])
        set_as_top_text(header)
        header.pack()

        directions = Label(subFrame, text = read[1] + read[2])
        set_as_body_text(directions)
        directions.pack()

        read[3] = read[3].strip()
        candidates = read[3].split(', ')

        candidateFrame = Frame(subFrame)
        candidateFrame.pack()

        if(read[1] == ' Pick only' and read[2][1] == '1'):
            var = IntVar()
            for q in range (0, len(candidates)):
                rb = Radiobutton(candidateFrame, text = candidates[q], variable = var, value = q+1)
                set_as_body_text(rb)
                rb.grid(sticky = W)
        else:
            for q in range (0, len(candidates)):
                temp = IntVar()
                cb = Checkbutton(candidateFrame, text = candidates[q], variable = temp)
                set_as_body_text(cb)
                cb.grid(sticky = W)

        next = Button(subFrame, text = "CONTINUE", command = nextFrame1)
        set_as_body_text(next)
        next.pack()
        counter += 1

raise_frame(frame1)

#get info from entries
def checkInfo():
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

    def reset():
        raise_frame(frame1)

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
submit = Button(frame1, text = "SUBMIT", command = checkInfo)
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
end = Button(lastframe_SubFrame, text = "FINISH", command = reset)
set_as_body_text(end)
thanks.pack()
end.pack()

root.mainloop()
