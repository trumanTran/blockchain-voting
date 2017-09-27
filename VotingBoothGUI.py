from tkinter import *
import tkinter.messagebox

def raise_frame(frame):
    frame.tkraise()

#create a window
root = Tk()
root.attributes("-fullscreen", True)
root.title("Voting Booth")

f1 = Frame(root)
f2 = Frame(root)
f3 = Frame(root)
f4 = Frame(root)

for frame in (f1, f2, f3, f4):
    frame.place(relx = 0.5, rely = 0.5, anchor = "c", relwidth = 1.0, relheight = 1.0)



#get info from entries
def checkInfo(event):
    print("name: %s | address: %s" % ( nI.get(), aI.get() ) )
    if (nI.get() == "name" and aI.get() == "address")or(nI.get()=='aa' and aI.get() == 'bb'): #whole line for testing
        #reset text boxes to blank and goto next frame
        print ("valid")
        raise_frame(f2)
    else:
        tkinter.messagebox.showinfo("INVALID", "Your name or address are invalid")
        print("not valid")

#confirm quitting the app
def quitCheck():
    answer = tkinter.messagebox.askquestion("YOU ARE ABOUT TO QUIT",
                                            "Are you sure you'd like to quit?")
    if answer == 'yes':
        root.quit()


#frame 1
f1.columnconfigure(0, weight = 1)
f1.columnconfigure(1, weight = 2)
f1.columnconfigure(2, weight = 1)

f1.rowconfigure(0, weight = 1)
f1.rowconfigure(1, weight = 1)
f1.rowconfigure(2, weight = 1)


f1a = Frame(f1)
f1a.grid(column = 1, row = 1)

#name and address labels
name = Label(f1a, text = "Name")
address = Label(f1a, text = "Address")
welcome = Label(f1, text = "Welcome")

#entry boxes
nI = Entry(f1a)
aI = Entry(f1a)

#button definition
submit = Button(f1, text = "Submit")
submit.bind("<Button-1>", checkInfo)
quit = Button(f1, text = "QUIT", command = quitCheck)


#placement onto the window
welcome.grid(column = 1, row = 0, sticky = 'news')#'news' centers in the middle of a cell
name.grid(row = 0, column = 0, sticky=E)
address.grid(row = 1, column = 0, sticky=E)

nI.grid(row = 0, column = 1, sticky = EW)
aI.grid(row = 1, column = 1, sticky = EW)

submit.grid(row = 2, column = 1, sticky = E)
quit.grid(row=2, column = 1, sticky = W)



#functions for frame 2 and 3

#check only candidate
def presidentCheck():
    if president.get() != 0:
        print (president.get())
        raise_frame(f3)
    else:
        tkinter.messagebox.showinfo("INVALID", "Please submit a vote")

#no limit on amount of candidates to vote for
def generalTally():
    total = 0
    x = 0
    while (x < 3):
        if checks2[x].get() == 1:
            total += 1
        x += 1
    print(total)
    raise_frame(f4)



#frame 2
#declaration of a variable to check if a checkbox is ticked or not
f2.rowconfigure(0,weight = 1)
f2.rowconfigure(1,weight = 1)
f2.rowconfigure(2,weight = 1)
f2.columnconfigure(0, weight = 1)
f2.columnconfigure(1, weight = 1)
f2.columnconfigure(2, weight = 1)

f2a = Frame(f2)

f2a.grid(row = 1, column = 1)

president = IntVar()

label = Label(f2a, text = "PRESIDENT" + '\n' + "(Please vote for one)")
label.pack()

#declaration of check boxes
cb1 = Radiobutton(f2a, text="Hilary Clinton", variable = president, value = 1)
cb1.pack()

cb2 = Radiobutton(f2a, text="Bernie Sanders", variable = president, value = 2)
cb2.pack()

cb3 = Radiobutton(f2a, text="Donald Trump", variable = president, value = 3)
cb3.pack()


submitR1 = Button(f2a, text = "Submit", command = presidentCheck)
submitR1.pack()




#frame 3
f3.columnconfigure(0, weight = 1)
f3.columnconfigure(1, weight = 1)
f3.columnconfigure(2, weight = 1)
f3.columnconfigure(3, weight = 1)
f3.columnconfigure(4, weight = 1)

f3.rowconfigure(0, weight = 1)
f3.rowconfigure(1, weight = 1)
f3.rowconfigure(2, weight = 1)

f3_sub_frame_a = Frame(f3)

f3_sub_frame_a.grid(row = 1, column = 2)

label = Label(f3_sub_frame_a, text = "FAVORITE FOOD" + '\n' + "(Please vote for as many as you'd like)")
label.grid(sticky = 'news', column = 2)

#set different variables for different race
Chicken = IntVar()
Pork = IntVar()
Beef = IntVar()

#checkbox definitions
cb1 = Checkbutton(f3_sub_frame_a, text="Chicken", variable = Chicken)
cb1.grid(sticky = W, column = 2)

cb2 = Checkbutton(f3_sub_frame_a, text="Pork", variable = Pork)
cb2.grid(sticky = W, column = 2)

cb3 = Checkbutton(f3_sub_frame_a, text="Beef", variable = Beef)
cb3.grid(sticky = W, column = 2)

checks2 = [Chicken, Pork, Beef]

#button definitions
submitR2 = Button(f3_sub_frame_a, text = "Submit", command = generalTally)

submitR2.grid ( column = 2)





#frame 4
f4.columnconfigure(0, weight = 1)
f4.rowconfigure(0, weight = 1)

label = Label(f4, text = "Thanks for voting")
label.grid(sticky = 'news')

#function to reset all parameters and start the voting booth from the beginning
def reset():
    vote.set(0)
    Chicken.set(0)
    Beef.set(0)
    Pork.set(0)
    raise_frame(f1)
    nI.delete(0, END)
    aI.delete(0, END)

end = Button(f4, text = "END", command = reset)
end.grid(pady = 50) #50 pixels from top and from bottom of button as a spacer






raise_frame(f1)

root.mainloop() #loop infinitely and keep gui running
