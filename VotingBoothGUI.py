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
    frame.grid(row = 0, column = 0, sticky = 'news')



#get info from entries
def checkInfo(event):
    print("name: %s | address: %s" % ( nI.get(), aI.get() ) )
    if (nI.get() == "name" and aI.get() == "address")or(nI.get()=='aa' and aI.get() == 'bb'):
        #reset text boxes to blank and goto next frame
        print ("valid")
        nI.delete(0, END)
        aI.delete(0, END)
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

#name and address labels
name = Label(f1, text = "Name")
address = Label(f1, text = "Address")
welcome = Label(f1, text = "Welcome")

#entry boxes
nI = Entry(f1)
aI = Entry(f1)

#button definition
submit = Button(f1, text = "Submit")
submit.bind("<Button-1>", checkInfo)
quit = Button(f1, text = "QUIT", command = quitCheck)


#placement onto the window
welcome.grid(columnspan = 100, sticky = 'news')
name.grid(row = 1, column = 1, sticky=E)
address.grid(row = 2, column = 1, sticky=E)

nI.grid(row = 1, column = 2)
aI.grid(row = 2, column = 2)

submit.grid(row = 3, column = 2)
quit.grid(row=3, column = 0)





#functions for frame 2 and 3

#check only candidate
def presidentCheck():
    print (vote.get())
    raise_frame(f3)

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
vote = IntVar()

label = Label(f2, text = "PRESIDENT" + '\n' + "(Please vote for one)")
label.grid(sticky = 'news')

#declaration of check boxes
cb1 = Radiobutton(f2, text="Hilary Clinton", variable = vote, value = 1)
cb1.grid(sticky = 'news')

cb2 = Radiobutton(f2, text="Bernie Sanders", variable = vote, value = 2)
cb2.grid(sticky = 'news')

cb3 = Radiobutton(f2, text="Donald Trump", variable = vote, value = 3)
cb3.grid(sticky = 'news')


submitR1 = Button(f2, text = "Submit", command = presidentCheck)
submitR1.grid (sticky = 'news')







#frame 3
label = Label(f3, text = "FAVORITE FOOD" + '\n' + "(Please vote for as many as you'd like)")
label.grid(sticky = 'news')

#set different variables for different race
Chicken = IntVar()
Pork = IntVar()
Beef = IntVar()

#checkbox definitions
cb1 = Checkbutton(f3, text="Chicken", variable = Chicken)
cb1.grid(sticky = W)

cb2 = Checkbutton(f3, text="Pork", variable = Pork)
cb2.grid(sticky = W)

cb3 = Checkbutton(f3, text="Beef", variable = Beef)
cb3.grid(sticky = W)

checks2 = [Chicken, Pork, Beef]

#button definitions
submitR2 = Button(f3, text = "Submit", command = generalTally)

submitR2.grid (sticky = 'news')





#frame 4

label = Label(f4, text = "Thanks for voting")
label.pack()

#function to reset all parameters and start the voting booth from the beginning
def reset():
    vote.set(0)
    Chicken.set(0)
    Beef.set(0)
    Pork.set(0)
    raise_frame(f1)

end = Button(f4, text = "END", command = reset)
end.pack()









raise_frame(f1)

root.mainloop()
