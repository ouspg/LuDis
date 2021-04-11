#######################################
#   Module for closing the program.   #
#   Author: Jarmo Luomala (2013)      #
#######################################

from Tkinter import *
from tkMessageBox import askquestion

class Quitter(Frame):
	def __init__(self, parent=None):
		Frame.__init__(self, parent)
		self.pack()
		widget = Button(self, text='Quit', width=4, bg='gray80', command=self.quit)
		widget.pack(expand=YES, fill=BOTH, side=LEFT)

	def quit(self):
		ans = askquestion('Confirm quit', "Are you sure you want to quit?")
		if ans == 'yes':
			Frame.quit(self)

if __name__ == '__main__':
	Quitter().mainloop()
