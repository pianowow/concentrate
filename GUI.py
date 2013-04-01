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


root = Tk()
root.title("Concentrate")
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)


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

boardframe = ttk.Frame(mainframe)
boardframe.grid(column=0,row=1,sticky=(N, S, E, W))

letters = [[StringVar() for x in range(5)] for y in range(5)]
e = [[0 for x in range(5)] for y in range(5)]

def nex(widget,newval,oldval):
    
    if len(newval) > 1:
        return False
    if len(newval) == 0:
        return True
    if newval.upper() not in ('A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z'):
        return False
    
    
    me = boardframe.nametowidget(widget)
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

    return True


vcmd = (root.register(nex),'%W','%P','%s')

for row in range(5):
    for col in range(5):
        e[row][col] = ttk.Entry(boardframe,width=2,textvariable=letters[row][col], validate='key', validatecommand=vcmd)
        e[row][col].grid(column=col, row=row, sticky=(N, S, E, W))


##e00 = ttk.Entry(boardframe, width=2, textvariable=letters[0][0])
##e01 = ttk.Entry(boardframe, width=2, textvariable=letters[0][1])
##e02 = ttk.Entry(boardframe, width=2, textvariable=letters[0][2])
##e03 = ttk.Entry(boardframe, width=2, textvariable=letters[0][3])
##e04 = ttk.Entry(boardframe, width=2, textvariable=letters[0][4])
##
##e10 = ttk.Entry(boardframe, width=2, textvariable=letters[1][0])
##e11 = ttk.Entry(boardframe, width=2, textvariable=letters[1][1])
##e12 = ttk.Entry(boardframe, width=2, textvariable=letters[1][2])
##e13 = ttk.Entry(boardframe, width=2, textvariable=letters[1][3])
##e14 = ttk.Entry(boardframe, width=2, textvariable=letters[1][4])
##
##e20 = ttk.Entry(boardframe, width=2, textvariable=letters[2][0])
##e21 = ttk.Entry(boardframe, width=2, textvariable=letters[2][1])
##e22 = ttk.Entry(boardframe, width=2, textvariable=letters[2][2])
##e23 = ttk.Entry(boardframe, width=2, textvariable=letters[2][3])
##e24 = ttk.Entry(boardframe, width=2, textvariable=letters[2][4])
##
##e30 = ttk.Entry(boardframe, width=2, textvariable=letters[3][0])
##e31 = ttk.Entry(boardframe, width=2, textvariable=letters[3][1])
##e32 = ttk.Entry(boardframe, width=2, textvariable=letters[3][2])
##e33 = ttk.Entry(boardframe, width=2, textvariable=letters[3][3])
##e34 = ttk.Entry(boardframe, width=2, textvariable=letters[3][4])
##
##e40 = ttk.Entry(boardframe, width=2, textvariable=letters[4][0])
##e41 = ttk.Entry(boardframe, width=2, textvariable=letters[4][1])
##e42 = ttk.Entry(boardframe, width=2, textvariable=letters[4][2])
##e43 = ttk.Entry(boardframe, width=2, textvariable=letters[4][3])
##e44 = ttk.Entry(boardframe, width=2, textvariable=letters[4][4])

##e00.grid(column=0, row=0, sticky=(N, S, E, W))
##e01.grid(column=1, row=0, sticky=(N, S, E, W))
##e02.grid(column=2, row=0, sticky=(N, S, E, W))
##e03.grid(column=3, row=0, sticky=(N, S, E, W))
##e04.grid(column=4, row=0, sticky=(N, S, E, W))
##
##e10.grid(column=0, row=1, sticky=(N, S, E, W))
##e11.grid(column=1, row=1, sticky=(N, S, E, W))
##e12.grid(column=2, row=1, sticky=(N, S, E, W))
##e13.grid(column=3, row=1, sticky=(N, S, E, W))
##e14.grid(column=4, row=1, sticky=(N, S, E, W))
##
##e20.grid(column=0, row=2, sticky=(N, S, E, W))
##e21.grid(column=1, row=2, sticky=(N, S, E, W))
##e22.grid(column=2, row=2, sticky=(N, S, E, W))
##e23.grid(column=3, row=2, sticky=(N, S, E, W))
##e24.grid(column=4, row=2, sticky=(N, S, E, W))
##
##e30.grid(column=0, row=3, sticky=(N, S, E, W))
##e31.grid(column=1, row=3, sticky=(N, S, E, W))
##e32.grid(column=2, row=3, sticky=(N, S, E, W))
##e33.grid(column=3, row=3, sticky=(N, S, E, W))
##e34.grid(column=4, row=3, sticky=(N, S, E, W))
##
##e40.grid(column=0, row=4, sticky=(N, S, E, W))
##e41.grid(column=1, row=4, sticky=(N, S, E, W))
##e42.grid(column=2, row=4, sticky=(N, S, E, W))
##e43.grid(column=3, row=4, sticky=(N, S, E, W))
##e44.grid(column=4, row=4, sticky=(N, S, E, W))

boardframe.columnconfigure(0, weight=1)
boardframe.columnconfigure(1, weight=1)
boardframe.columnconfigure(2, weight=1)
boardframe.columnconfigure(3, weight=1)
boardframe.columnconfigure(4, weight=1)

boardframe.rowconfigure(0, weight=1)
boardframe.rowconfigure(1, weight=1)
boardframe.rowconfigure(2, weight=1)
boardframe.rowconfigure(3, weight=1)
boardframe.rowconfigure(4, weight=1)



root.mainloop()
