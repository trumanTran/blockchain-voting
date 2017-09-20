from tkinter import *

def raise_frame(frame):
    frame.tkraise()

root = Tk()
root.attributes("-fullscreen", True)

f1 = Frame(root)
f2 = Frame(root)
f3 = Frame(root)
f4 = Frame(root)

f1.columnconfigure(0,weight = 1)

for frame in (f1, f2, f3, f4):
    frame.grid(row = 0, column = 0, sticky = 'news')



#get info from entries
def checkInfo(event):
    print("name: %s | address: %s" % ( nI.get(), aI.get() ) )
    if nI.get() == "name" and aI.get() == "address":
        print ("valid")
        raise_frame(f2)
    else:
        print("not valid")


#name and address labels
name = Label(f1, text = "Name")
address = Label(f1, text = "Address")

#entry boxes
nI = Entry(f1)
aI = Entry(f1)

#button definition
submit = Button(f1, text = "Submit")
submit.bind("<Button-1>", checkInfo)



#placement onto the window
name.grid(row = 0, sticky=E)
address.grid(row = 1, sticky=E)


nI.grid(row = 0, column = 1)
aI.grid(row = 1, column = 1)

submit.grid(row = 3, column = 1)






#functions for frame 2 and 3

#count how many candidates were selected and limit to 1
def presidentTally(event):
    total = 0
    x = 0
    while(x < 3):
        if checks[x].get() == 1:
            total += 1
        x+=1
    print(total)

    if(total == 1):
        raise_frame(f3)
    else:
        print("Invalid vote")

#no limit on amount of candidates to vote for
def generalTally(event):
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
Hillary_Clinton = IntVar()
Bernie_Sandars = IntVar()
Donald_Trump = IntVar()

label = Label(f2, text = "PRESIDENT" + '\n' + "(Please vote for one)")
label.grid(sticky = 'news')

#declaration of check boxes
cb1 = Checkbutton(f2, text="Hilary Clinton", variable = Hillary_Clinton)
cb1.grid(sticky = 'news')

cb2 = Checkbutton(f2, text="Bernie Sanders", variable = Bernie_Sandars)
cb2.grid(sticky = 'news')

cb3 = Checkbutton(f2, text="Donald Trump", variable = Donald_Trump)
cb3.grid(sticky = 'news')

checks = [Hillary_Clinton, Bernie_Sandars, Donald_Trump]

submitR1 = Button(f2, text = "Submit")
submitR1.bind("<Button-1>", presidentTally)

submitR1.grid (sticky = 'news')







#frame 3
label = Label(f3, text = "FAVORITE FOOD" + '\n' + "(Please vote for as many as you'd like)")
label.grid(sticky = 'news')

#set different variables for different race
Chicken = IntVar()
Pork = IntVar()
Beef = IntVar()

cb1 = Checkbutton(f3, text="Chicken", variable = Chicken)
cb1.grid(sticky = W)

cb2 = Checkbutton(f3, text="Pork", variable = Pork)
cb2.grid(sticky = W)

cb3 = Checkbutton(f3, text="Beef", variable = Beef)
cb3.grid(sticky = W)

checks2 = [Chicken, Pork, Beef]

submitR2 = Button(f3, text = "Submit")
submitR2.bind("<Button-1>", generalTally)

submitR2.grid (sticky = 'news')






#frame 4
label = Label(f4, text = "Thanks for voting")
label.pack()



raise_frame(f1)

root.mainloop()