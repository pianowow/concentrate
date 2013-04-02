#-------------------------------------------------------------------------------
# Name:        search
# Purpose:
#
# Author:      CHRISTOPHER_IRWIN
#
# Created:     31/03/2013

from tkinter import *
from tkinter import ttk
from player import player0

alpha = ('A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z')

root = Tk()
root.title("Concentrate")
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)
root.aspect(3,1,3,1)

s = ttk.Style()
s.configure('red.TEntry',background='red')
s.configure('maroon.TEntry',background='maroon')
s.configure('aqua.TEntry',background='aqua')
s.configure('blue.TEntry',background='blue')
s.configure('white.TEntry',background='white')


mainframe = ttk.Frame(root, padding=(3,3,12,12))
mainframe.grid(column=0, row=0, sticky=(N, S, E, W))
mainframe.columnconfigure(0, weight=1)
mainframe.columnconfigure(1, weight=1)
mainframe.columnconfigure(2, weight=1)
mainframe.rowconfigure(0, weight=0)
mainframe.rowconfigure(1, weight=1)

ttk.Label(mainframe, text="Board").grid(column=0,row=0)
ttk.Label(mainframe, text="Played Words").grid(column=1,row=0)
btnsearch = ttk.Button(mainframe, text="Search")
btnsearch.grid(column=2,row=0)
btnsearch['default'] = 'active'

boardframe = ttk.Frame(mainframe,width=500, height=500)
boardframe.grid(column=0,row=1,sticky=(N, W, E, S) )

letters = [[StringVar() for x in range(5)] for y in range(5)]
e = [[0 for x in range(5)] for y in range(5)]

##def nex(widget,newval):
##    if len(newval) > 1:
##        return False
##    if len(newval) == 0:
##        return True
##    if newval.upper() not in alpha:
##        return False
##    me = boardframe.nametowidget(widget)
##    merow = 0
##    mecol = 0
##    for row in range(5):
##        for col in range(5):
##            if e[row][col] == me:
##                merow = row
##                mecol = col
##    letters[merow][mecol].set(newval.upper())
##    nextwidget = (merow*5 + mecol + 1 ) % 25
##    nextwrow = nextwidget // 5
##    nextwcol = nextwidget % 5
##    e[nextwrow][nextwcol].focus()
##    e[nextwrow][nextwcol].selection_range(0, END)
##    return True

def nex(event):
    me = event.widget
    newval = me.get()
    if len(newval) > 1:
        me.delete(1,END)
        newval = me.get()
    if len(newval) == 0:
        return
    if newval.upper() not in alpha:
        me.delete(0,END)
        return
    print(event.char)
    if event.char.upper() in alpha:
        #me = boardframe.nametowidget(widget)
        merow = 0
        mecol = 0
        for row in range(5):
            for col in range(5):
                if e[row][col] == me:
                    merow = row
                    mecol = col
        letters[merow][mecol].set(newval.upper())
        nextwidget = (merow*5 + mecol + 1 ) % 25
        nextwrow = nextwidget // 5
        nextwcol = nextwidget % 5
        e[nextwrow][nextwcol].focus()
        e[nextwrow][nextwcol].selection_range(0, END)

def highlight(event):
    me = event.widget
    me.selection_range(0, END)


def undo(widget,oldval):
    me = boardframe.nametowidget(widget)
    merow = 0
    mecol = 0
    for row in range(5):
        for col in range(5):
            if e[row][col] == me:
                merow = row
                mecol = col
    letters[merow][mecol].set(oldval)

def chgcolor(event):
    me = event.widget
    curcolor = me['background']
    if curcolor == 'white':
        me['background'] = 'light blue'
    elif curcolor == 'light blue':
        me['background'] = 'pink'
    elif curcolor == 'pink':
        me['background'] = 'white'

vcmd = (root.register(nex),'%W','%P')
inv = (root.register(undo), '%W','%s')

for row in range(5):
    for col in range(5):
        #e[row][col] = ttk.Entry(boardframe,width=2,textvariable=letters[row][col], validate='key', validatecommand=vcmd,invalidcommand=inv,background='white')
        e[row][col] = Entry(boardframe,width=2,textvariable=letters[row][col],background='white')
        e[row][col].bind('<KeyRelease>',nex)
        e[row][col].grid(column=col, row=row, sticky=(N, S, E, W))
        e[row][col].bind("<Button-3>", chgcolor) #so if you want to change the color
        e[row][col].bind("<Button-1>", highlight) #so if you left-click on a square with a letter already in it, that letter is highlighted
    boardframe.rowconfigure(row, weight=1)
    boardframe.columnconfigure(row, weight=1) #can get away with this because it's square

history = ttk.Treeview(mainframe)
history.grid(row=1,column=1,sticky=(N,S,E,W))

suggest = ttk.Treeview(mainframe)
suggest.grid(row=1,column=2,sticky=(N,S,E,W))

root.mainloop()
