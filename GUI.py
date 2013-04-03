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
#root.aspect(3,1,3,1)

mainframe = ttk.Frame(root, padding=(3,3,12,12))
mainframe.grid(column=0, row=0, sticky=(N, S, E, W))
mainframe.columnconfigure(0, weight=0)
mainframe.columnconfigure(1, weight=1)
mainframe.columnconfigure(2, weight=1)
mainframe.rowconfigure(0, weight=0)
mainframe.rowconfigure(1, weight=1)

ttk.Label(mainframe, text="Board").grid(column=0,row=0)
ttk.Label(mainframe, text="Played Words").grid(column=1,row=0)
btnsearch = ttk.Button(mainframe, text="Search")
btnsearch.grid(column=2,row=0)
btnsearch['default'] = 'active'

#boardframe = ttk.Frame(mainframe,width=200, height=200)
#boardframe.grid(column=0,row=1,sticky=(N, W, E) )

historyframe = ttk.Frame(mainframe,width=200, height=200)
historyframe.grid(column=1,row=1,sticky=(N, W, E, S) )
historyframe.columnconfigure(0, weight=1)
historyframe.rowconfigure(0, weight=1)

wordsframe  = ttk.Frame(mainframe,width=200, height=200)
wordsframe.grid(column=2,row=1,sticky=(N, W, E, S) )
wordsframe.columnconfigure(0, weight=1)
wordsframe.rowconfigure(0, weight=1)

def getrowcol(x,y):
    col = x//sqsize
    row = y//sqsize
    return (row,col)

def nex(event):
    #(row,col) = getrowcol(event.x,event.y)
    #print(event.y,event.x)
    (row,col) = selected
    print(row,col)
    print('keyboard: %s' % (event.char))
    char = event.char.upper()
    if char in alpha:
        board.itemconfig(boardstuff[row][col][1],text=char)
    nextnum = (row*5 + col + 1) % 25
    nextrow = nextnum // 5
    nextcol = nextnum % 5
    selectsquare(nextrow,nextcol)
##    me = event.widget
##    newval = me.get()
##    if len(newval) > 1:
##        me.delete(1,END)
##        newval = me.get()
##    if len(newval) == 0:
##        return
##    if newval.upper() not in alpha:
##        me.delete(0,END)
##        return
##    if event.char.upper() in alpha:
##        merow = 0
##        mecol = 0
##        for row in range(5):
##            for col in range(5):
##                if e[row][col] == me:
##                    merow = row
##                    mecol = col
##        letters[merow][mecol].set(newval.upper())
##        nextwidget = (merow*5 + mecol + 1 ) % 25
##        nextwrow = nextwidget // 5
##        nextwcol = nextwidget % 5
##        e[nextwrow][nextwcol].focus()
##        e[nextwrow][nextwcol].selection_range(0, END)
##        me['state'] = 'hidden'

##def undo(widget,oldval):
##    me = boardframe.nametowidget(widget)
##    merow = 0
##    mecol = 0
##    for row in range(5):
##        for col in range(5):
##            if e[row][col] == me:
##                merow = row
##                mecol = col
##    letters[merow][mecol].set(oldval)

blue = ('cornflower blue','DodgerBlue2')
red = ('salmon','red')

def updatecolors(row,col,color):
    if color == 'blue':
        board.itemconfig(boardstuff[row][col][0],fill=blue[0])
    elif color == 'red':
        board.itemconfig(boardstuff[row][col][0],fill=red[0])
    else:
        board.itemconfig(boardstuff[row][col][0],fill='')
    #TODO defended check

def chgcolor(event):
    board.focus_set()

    #print('in chgcolor: %d,%d' % (event.x,event.y))
    (row,col) = getrowcol(event.x,event.y)
    selectsquare(row,col)
    color = board.itemcget(boardstuff[row][col][0],'fill')
    if color == '':
        updatecolors(row,col,'blue')
    elif color in blue:
        updatecolors(row,col,'red')
    elif color in red:
        updatecolors(row,col,'')
##    me = event.widget
##    curcolor = me['background']
##    if curcolor == 'white':
##        me['background'] in ('cornflower blue','DodgerBlue2') #dodger is defended
##    elif curcolor == 'cornflower blue':
##        me['background'] = 'salmon'
##    elif curcolor in ('salmon','red'): #red is defended
##        me['background'] = 'white'

##for row in range(5):
##    for col in range(5):
##        e[row][col] = Entry(boardframe,width=2,textvariable=letters[row][col],background='white')
##        e[row][col].bind('<KeyRelease>',nex)
##        e[row][col].grid(column=col, row=row, sticky=(N, S, E, W))
##        e[row][col].bind("<Button-3>", chgcolor) #so if you want to change the color
##        e[row][col].bind("<Button-1>", highlight) #so if you left-click on a square with a letter already in it, that letter is highlighted
##    boardframe.rowconfigure(row, weight=1)
##    boardframe.columnconfigure(row, weight=1) #can get away with this because it's square

boardstuff = [[None for x in range(5)] for y in range(5)]  #holds rectangles and text on the board
boardsize = 250
sqsize = boardsize//5

def selectsquare(selectrow,selectcol):
    global selected
    selected = (selectrow,selectcol)
    board.focus_set()
    for row in range(5):
        for col in range(5):
            board.itemconfig(boardstuff[row][col][0],outline='gray')
    board.itemconfig(boardstuff[selectrow][selectcol][0],outline='black')

def highlight(event):
    print(event.x,event.y)
    (row,col) = getrowcol(event.x, event.y)
    selectsquare(row,col)
    #me = event.widget
    #me.selection_range(0, END)

board = Canvas(mainframe, width=boardsize, height=boardsize,bg='white')
board.grid(row=1,column=0)
board.bind('<Key>',nex)  #to write that character to the square and select the next one
board.bind('<Button-1>',highlight)  #to tell which square is selected
board.bind('<Double-Button-1>',chgcolor)

for row in range(5):
    for col in range(5):
        top = row * sqsize
        left = col * sqsize
        bottom = row * sqsize + sqsize -1
        right = col * sqsize + sqsize -1
        rect = board.create_rectangle(left,top,right,bottom,outline='gray')
        text = board.create_text(left+sqsize/2, top+sqsize/2,text='',font='Helvetica 20')
        boardstuff[row][col] = (rect,text)

selected = (0,0)
selectsquare(selected[0],selected[1])


history = ttk.Treeview(historyframe)
history.grid(row=0,column=0,sticky=(N,S,E,W))

suggest = ttk.Treeview(wordsframe)
suggest.grid(row=0,column=0,sticky=(N,S,E,W))

root.mainloop()
