from tkinter import *


def leftClick(event): #Just a do nothing function to be replaced later
    print("You blew it")

#Map/Dictionary element contains the name of each office up for election and the voter's choice for that office
how_they_voted = {'President': 'Dracula', 'Vice President': 'The Wolfman', 'Secretary of State': 'Frankenstein\'s Monster',
         'Secretary of the Interior': 'Bigfoot', 'Head of the EPA': 'Swamp Thing', 'Secretary of Health and Human'
                                                                                   'Services': 'The Mummy'}
#prints the elements of the Map?Dictionary. For testing only
for key, value in how_they_voted.items(): #passes through dictionary and prints keys and values
    print(key, ': ', value)

#print("The number of positions being elected is: ",len(how_they_voted))

root = Tk()
root.geometry("500x300") #formats the gui to specified size
root.wm_title("Final Confirmation") #creates title for gui

#initilize two empty lists
final_results = []
final_button = []
#index used for positioning the buttons and labels
index = 0
for key, value in how_they_voted.items():
    temp_result = Label(root, text=key + ": " + ' ' + value)
    temp_result.grid(row=index, column=0, sticky=W)
    final_results.append(temp_result)

    temp_button = Button(root, text="Change Vote")
    final_button.append(temp_button)
    final_button[index].bind("<Button-1>", leftClick)
    final_button[index].grid(row=index, column=3)

    index = index + 1


root.mainloop()

