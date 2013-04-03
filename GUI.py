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

class concentrateGUI(Frame):

    def __init__(self, master):
        Frame.__init__(self, master)
        print('beginning')

        self.boardstuff = [[None for x in range(5)] for y in range(5)]  #holds rectangles and text on the board
        self.boardsize = 250
        self.sqsize = self.boardsize//5
        self.blue = ('cornflower blue','DodgerBlue2')
        self.red = ('salmon','red')
        self.initialdraw(master)

    def initialdraw(self,master):
        master.title("Concentrate")
        master.columnconfigure(0, weight=1)
        master.rowconfigure(0, weight=1)

        mainframe = ttk.Frame(master, padding=(3,3,12,12))
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

        self.board = Canvas(mainframe, width=self.boardsize, height=self.boardsize,bg='white')
        self.board.grid(row=1,column=0)
        self.board.bind('<Key>',self.nex)  #to write that character to the square and select the next one
        self.board.bind('<Button-1>',self.highlight)  #to tell which square is selected
        self.board.bind('<Double-Button-1>',self.chgcolor)

        for row in range(5):
            for col in range(5):
                top = row * self.sqsize
                left = col * self.sqsize
                bottom = row * self.sqsize + self.sqsize -1
                right = col * self.sqsize + self.sqsize -1
                rect = self.board.create_rectangle(left,top,right,bottom,outline='gray')
                text = self.board.create_text(left+self.sqsize/2, top+self.sqsize/2,text='',font='Helvetica 20')
                self.boardstuff[row][col] = (rect,text)


        selected = (0,0)
        self.selectsquare(0,0)

        history = ttk.Treeview(historyframe)
        history.grid(row=0,column=0,sticky=(N,S,E,W))

        suggest = ttk.Treeview(wordsframe)
        suggest.grid(row=0,column=0,sticky=(N,S,E,W))


    def getrowcol(self,x,y):
        col = x//self.sqsize
        row = y//self.sqsize
        return (row,col)

    def nex(self,event):
        #(row,col) = getrowcol(event.x,event.y)
        #print(event.y,event.x)
        (row,col) = selected
        print(row,col)
        print('keyboard: %s' % (event.char))
        char = event.char.upper()
        if char in alpha:
            self.board.itemconfig(self.boardstuff[row][col][1],text=char)
            nextnum = (row*5 + col + 1) % 25
            nextrow = nextnum // 5
            nextcol = nextnum % 5
            self.selectsquare(nextrow,nextcol)

    def updatecolors(self,row,col,color):
        if color == 'blue':
            self.board.itemconfig(self.boardstuff[row][col][0],fill=self.blue[0])
        elif color == 'red':
            self.board.itemconfig(self.boardstuff[row][col][0],fill=self.red[0])
        else:
            self.board.itemconfig(self.boardstuff[row][col][0],fill='')
        #TODO defended check

    def chgcolor(self,event):
        self.board.focus_set()
        #print('in chgcolor: %d,%d' % (event.x,event.y))
        (row,col) = self.getrowcol(event.x,event.y)
        self.selectsquare(row,col)
        color = self.board.itemcget(self.boardstuff[row][col][0],'fill')
        if color == '':
            self.updatecolors(row,col,'blue')
        elif color in self.blue:
            self.updatecolors(row,col,'red')
        elif color in self.red:
            self.updatecolors(row,col,'')
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



    def selectsquare(self,selectrow,selectcol):
        global selected
        selected = (selectrow,selectcol)
        self.board.focus_set()
        for row in range(5):
            for col in range(5):
                self.board.itemconfig(self.boardstuff[row][col][0],outline='gray')
        self.board.itemconfig(self.boardstuff[selectrow][selectcol][0],outline='black')

    def highlight(self,event):
        print(event.x,event.y)
        (row,col) = self.getrowcol(event.x, event.y)
        self.selectsquare(row,col)
        #me = event.widget
        #me.selection_range(0, END)



if __name__ == '__main__':
    tk = Tk()
    gui = concentrateGUI(tk)
    gui.mainloop()
