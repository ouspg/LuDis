###################################
#   Module for the help/manual.   #
#   Author: Jarmo Luomala (2013)  #
###################################

from Tkinter import *
from tkSimpleDialog import askstring

class HelpWin(Frame):

	def __init__(self, parent=None, text='', text_file=None):
		Frame.__init__(self, parent)
		self.grab_set()			# grab all mouse/keyboard events in this window i.e. disable the main window
		self.master.bind('<Escape>', self.on_cancel)
		self.main_window = self.master.master
		self.WIN_WIDTH = 450
		self.WIN_HEIGHT = 550
		self.WIN_OFFSET = '+450+50'
		self.master.geometry(str(self.WIN_WIDTH)+'x'+str(self.WIN_HEIGHT)+self.WIN_OFFSET)
		self.master.resizable(FALSE, FALSE)
		self.pack(expand=YES, fill=BOTH)
		self.master.title('Help')
		self.make_widgets()
		self.set_text(text, text_file)

	def make_widgets(self):	
		"""Make widgets for the popup window."""
		btn_frame = Frame(self)
		btn_frame.pack(anchor=N, expand=YES, fill=X, padx=5, pady=5)
		Button(btn_frame, text='Find', width=4, command=self.on_find).pack(side=LEFT, padx=5)
		Button(btn_frame, text='Close', width=4, command=self.on_cancel).pack(side=LEFT, padx=5)
		text_frame = Frame(self)
		text_frame.pack(anchor=N, expand=YES, fill=BOTH, padx=5, pady=5)
		text_area = Text(text_frame, height=50, relief=SUNKEN, font=('Courier', 10, 'normal'))
		sbar = Scrollbar(text_frame)
		sbar.config(command=text_area.yview)
		text_area.config(yscrollcommand=sbar.set)
		sbar.pack(side=RIGHT, fill=Y)
		text_area.pack(side=LEFT, expand=YES, fill=BOTH)
		self.text = text_area
		self.text.config(state=DISABLED)

	def set_text(self, text='', text_file=None):
		"""Sets the content of the text area."""
		self.text.config(state=NORMAL)			# enable text area
		if text_file:
			text = open(text_file, 'r').read()
		self.text.delete('1.0', END)			# delete current text
		self.text.insert('1.0', text)			# add at line 1, col 0
		self.text.mark_set(INSERT, '1.0')		# set insert cursor
		self.text.config(state=DISABLED)		# disable text area

	def on_find(self):
		target = askstring('Find', 'Search for:', parent=self)
		if target:
			where = self.text.search(target, INSERT, END, nocase=True)  # search from insert cursor
			if where:                                      # returns an index
				pastit = where + ('+%dc' % len(target))    # index past target
				self.text.tag_remove(SEL, '1.0', END)      # remove selection
				self.text.tag_add(SEL, where, pastit)      # select found target
				self.text.mark_set(INSERT, pastit)         # set insert mark
				self.text.see(INSERT)                      # scroll display

	def on_cancel(self, event=None):
		self.master.destroy()


if __name__ == '__main__':
	root = Tk()
	HelpWin(parent=root, text_file='help.txt').mainloop()