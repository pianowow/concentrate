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

        self.boardstuff = [[None for x in range(5)] for y in range(5)]  #holds rectangles and text on the board
        self.boardsize = 250
        self.sqsize = self.boardsize//5
        self.blue = ('light sky blue','RoyalBlue2')
        self.red = ('salmon','red')

        master.title("Concentrate")
        master.columnconfigure(0, weight=1)
        master.rowconfigure(0, weight=1)

        self.initialdraw()

        self.grid(row=0,column=0)


    def nex(self,event):
        #(row,col) = getrowcol(event.x,event.y)
        (row,col) = selected
        char = event.char.upper()
        if char in alpha:
            self.board.itemconfig(self.boardstuff[row][col][1],text=char)
            nextnum = (row*5 + col + 1) % 25
            nextrow = nextnum // 5
            nextcol = nextnum % 5
            self.selectsquare(nextrow,nextcol)

    def getrowcol(self,x,y):
        col = x//self.sqsize
        row = y//self.sqsize
        return (row,col)

    def getcolor(self,row,col):
        color = self.board.itemcget(self.boardstuff[row][col][0],'fill')
        if color in self.blue:
            return 'b'
        elif color in self.red:
            return 'r'
        else:
            return 'w'

    def checkdefended(self,row,col):
        ncolors = set()
        if row in range(5) and col in range(5):
            mycolor = self.getcolor(row,col)
            ncolors.add(mycolor)
            nrow,ncol = row,col-1
            if nrow in range(5) and ncol in range(5):
                ncolors.add(self.getcolor(nrow,ncol))
            nrow,ncol = row-1,col
            if nrow in range(5) and ncol in range(5):
                ncolors.add(self.getcolor(nrow,ncol))
            nrow,ncol = row,col+1
            if nrow in range(5) and ncol in range(5):
                ncolors.add(self.getcolor(nrow,ncol))
            nrow,ncol = row+1,col
            if nrow in range(5) and ncol in range(5):
                ncolors.add(self.getcolor(nrow,ncol))
            if 'b' not in ncolors and 'w' not in ncolors:
                self.board.itemconfig(self.boardstuff[row][col][0],fill=self.red[1])
            elif 'r' not in ncolors and 'w' not in ncolors:
                self.board.itemconfig(self.boardstuff[row][col][0],fill=self.blue[1])
            else:
                if mycolor == 'b':
                    self.board.itemconfig(self.boardstuff[row][col][0],fill=self.blue[0])
                elif mycolor == 'r':
                    self.board.itemconfig(self.boardstuff[row][col][0],fill=self.red[0])

    def updatecolors(self,row,col,color):
        if color == 'blue':
            self.board.itemconfig(self.boardstuff[row][col][0],fill=self.blue[0])
        elif color == 'red':
            self.board.itemconfig(self.boardstuff[row][col][0],fill=self.red[0])
        else:
            self.board.itemconfig(self.boardstuff[row][col][0],fill='')
        #TODO defended check
        #check if I am defneded
        self.checkdefended(row,col)
        #check if neighbors are defended
        self.checkdefended(row,col-1)
        self.checkdefended(row-1,col)
        self.checkdefended(row,col+1)
        self.checkdefended(row+1,col)


    def chgcolor(self,event):
        self.board.focus_set()
        (row,col) = self.getrowcol(event.x,event.y)
        self.selectsquare(row,col)
        color = self.board.itemcget(self.boardstuff[row][col][0],'fill')
        if color == '':
            self.updatecolors(row,col,'blue')
        elif color in self.blue:
            self.updatecolors(row,col,'red')
        elif color in self.red:
            self.updatecolors(row,col,'')

    def selectsquare(self,selectrow,selectcol):
        global selected
        selected = (selectrow,selectcol)
        self.board.focus_set()
        for row in range(5):
            for col in range(5):
                self.board.itemconfig(self.boardstuff[row][col][0],outline='gray')
        self.board.itemconfig(self.boardstuff[selectrow][selectcol][0],outline='black')

    def initialdraw(self):
        mainframe = ttk.Frame(self, padding=(3,3,12,12))
        mainframe.grid(column=0, row=0, sticky=(N, S, E, W))
        mainframe.columnconfigure(0, weight=0)
        mainframe.columnconfigure(1, weight=1)
        mainframe.columnconfigure(2, weight=1)
        mainframe.rowconfigure(0, weight=0)
        mainframe.rowconfigure(1, weight=1)

        ttk.Label(mainframe, text="Board").grid(column=0,row=0)
        ttk.Label(mainframe, text="Played Words").grid(column=1,row=0,columnspan=2)
        btnclear = ttk.Button(mainframe, text='Clear',command=self.initialdraw)
        btnclear.grid(column=0,row=0,sticky='NW')
        btnsearch = ttk.Button(mainframe, text="Search")
        btnsearch.grid(column=3,row=0,columnspan=2)
        btnsearch['default'] = 'active'

        self.board = Canvas(mainframe, width=self.boardsize, height=self.boardsize,bg='white')
        self.board.grid(row=1,column=0)
        self.board.bind('<Key>',self.nex)  #to write that character to the square and select the next one
        self.board.bind('<Button-1>',self.chgcolor)

        for row in range(5):
            for col in range(5):
                top = row * self.sqsize
                left = col * self.sqsize
                bottom = row * self.sqsize + self.sqsize -1
                right = col * self.sqsize + self.sqsize -1
                rect = self.board.create_rectangle(left,top,right,bottom,outline='gray',fill='')
                text = self.board.create_text(left+self.sqsize/2, top+self.sqsize/2,text='',font='Helvetica 20 bold')
                self.boardstuff[row][col] = (rect,text)

        selected = (0,0)
        self.selectsquare(0,0)


        historyscroll = ttk.Scrollbar(mainframe,orient=VERTICAL)
        historyscroll.grid(row=1,column=2,sticky=(N,S,E))

        history = ttk.Treeview(mainframe,columns='Word')
        history.grid(row=1,column=1,sticky=(N,S,W))
        history.column('#0',width=1)
        history.column(0,width=150)

        suggestscroll = ttk.Scrollbar(mainframe,orient=VERTICAL)
        suggestscroll.grid(row=1,column=4,sticky=(N,S,E))

        suggest = ttk.Treeview(mainframe, columns=('Word'))
        suggest.grid(row=1,column=3,sticky=(N,S,W))
        suggest.column('#0',width=1)
        suggest.column(0,width=150)

if __name__ == '__main__':
    tk = Tk()
    gui = concentrateGUI(tk)
    tk.mainloop()
