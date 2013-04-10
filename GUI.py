#-------------------------------------------------------------------------------
# Name:        GUI
# Purpose:
#
# Author:      CHRISTOPHER_IRWIN
#
# Created:     31/03/2013

#TODO
#need some way to tell the engine whose turn it is
#progress bar dialog
#can GUIplayer yield the words as they are endgame checked, and the GUI can insert them in the proper place?
#single-click searched word to display it on the board
#double-click searched word to add it to the history and update the board
#click on history to show the game at that move (first entry will be beginning of the analysis)
#maybe stretch the board on resize somehow?  or just fix everything with no stretching anywhere...
#menu
    #Concentrate
        #random board
        #clear board
        #search
    #Options
        #difficulty
            #word list choice (full size or reduced)
            #word length limit
        #theme
            #light
            #dark
            #pop, etc


from tkinter import *
from tkinter import ttk
from player import player0
from time import time
import arena

alpha = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

class concentrateGUI(ttk.Frame):

    def __init__(self, master):
        ttk.Frame.__init__(self, master, padding=(3,3,3,3))

        self.boardstuff = [[None for x in range(5)] for y in range(5)]  #holds rectangles and text on the board
        self.boardsize = 250
        self.sqsize = self.boardsize//5
        self.blue = ('light sky blue','RoyalBlue2')
        self.red = ('salmon','red')

        master.title("Concentrate")
        master.columnconfigure(0, weight=1)
        master.rowconfigure(0, weight=1)
        self.master = master
        self.grid(column=0, row=0, sticky=(N, S, E, W))
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=0) #scroll bar shouldn't stretch
        self.columnconfigure(3, weight=1)
        self.columnconfigure(4, weight=0) #scroll bar shouldn't stretch
        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=1)

        ttk.Label(self, text='Board').grid(column=0,row=0)
        ttk.Label(self, text='Played Words').grid(column=1,row=0,columnspan=2)
        btnclear = ttk.Button(self, text='Clear',command=self.canvasdraw)
        btnclear.grid(column=0,row=0,sticky='NW')
        btnrandom = ttk.Button(self, text='Random',command=self.randomboard)
        btnrandom.grid(column=0,row=0,sticky='NE')
        btnsearch = ttk.Button(self, text='Search',command=self.dosearch)
        btnsearch.grid(column=3,row=0,columnspan=2)
        btnsearch['default'] = 'active'

        self.history = ttk.Treeview(self,columns=('Word','Board'), displaycolumns=('Word'),selectmode='browse',show='tree')
        historyscroll = ttk.Scrollbar(self,orient=VERTICAL,command=self.history.yview)
        historyscroll.grid(row=1,column=2,sticky=(N,S,E))
        self.history['yscrollcommand'] = historyscroll.set
        self.history.grid(row=1,column=1,sticky=(N,S,W,E))
        self.history.column('#0',width=1)
        self.history.column(0,width=150)

        self.suggest = ttk.Treeview(self, columns=('Word', 'Score','Board'), displaycolumns=('Word', 'Score'),selectmode='browse',show='tree')
        suggestscroll = ttk.Scrollbar(self,orient=VERTICAL,command=self.suggest.yview)
        suggestscroll.grid(row=1,column=4,sticky=(N,S,E))
        self.suggest['yscrollcommand'] = suggestscroll.set

        self.suggest.grid(row=1,column=3,sticky=(N,S,W,E))
        self.suggest.column('#0',width=1)
        self.suggest.column(0,width=150)
        self.suggest.column(1,width=75)

        self.canvasdraw()
        self.player = GUIplayer()

        self.notbusywidgetcursors = dict() #for busy and notbusy

    def canvasdraw(self):
        self.board = Canvas(self, width=self.boardsize, height=self.boardsize, borderwidth=0, highlightthickness=0, bg='white')
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

        self.selectsquare(0,0)

    def randomboard(self):
        letters = arena.genletters()
        for x,c in enumerate(letters):
            row = x // 5
            col = x % 5
            self.board.itemconfig(self.boardstuff[row][col][1],text=c)


    def nex(self,event):
        (row,col) = self.selected
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
            return 'B'
        elif color in self.red:
            return 'R'
        else:
            return 'W'

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
            if 'B' not in ncolors and 'W' not in ncolors:
                self.board.itemconfig(self.boardstuff[row][col][0],fill=self.red[1])
            elif 'R' not in ncolors and 'W' not in ncolors:
                self.board.itemconfig(self.boardstuff[row][col][0],fill=self.blue[1])
            else:
                if mycolor == 'B':
                    self.board.itemconfig(self.boardstuff[row][col][0],fill=self.blue[0])
                elif mycolor == 'R':
                    self.board.itemconfig(self.boardstuff[row][col][0],fill=self.red[0])

    def updatecolors(self,row,col,color):
        if color == 'blue':
            self.board.itemconfig(self.boardstuff[row][col][0],fill=self.blue[0])
        elif color == 'red':
            self.board.itemconfig(self.boardstuff[row][col][0],fill=self.red[0])
        else:
            self.board.itemconfig(self.boardstuff[row][col][0],fill='')

        #check if I am defended
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
        self.selected = (selectrow,selectcol)
        self.board.focus_set()
        for row in range(5):
            for col in range(5):
                self.board.itemconfig(self.boardstuff[row][col][0],outline='gray')
        self.board.itemconfig(self.boardstuff[selectrow][selectcol][0],outline='black')

    def busy(self, widget=None):
        if widget == None:
            w = self.master
        else:
            w = widget
        if not str(w) in self.notbusywidgetcursors:
            try:
                # attach cursor to this widget
                cursor = w.cget("cursor")
                if cursor != "watch":
                    self.notbusywidgetcursors[str(w)] = (w, cursor)
                    w.config(cursor="watch")
            except TclError:
                pass

        for w in w.children.values():
            self.busy(w)


    def notbusy(self):
        for w, cursor in self.notbusywidgetcursors.values():
            try:
                w.config(cursor=cursor)
            except TclError:
                pass
        self.notbusywidgetcursors = dict()

    def dosearch(self):
        self.busy()
        for iid in self.suggest.get_children():
            self.suggest.delete(iid)
        letters = ''.join([self.board.itemcget(self.boardstuff[row][col][1], 'text') for row in range(5) for col in range(5)])
        if not(all([x in alpha for x in letters]) and len(letters) == 25):
            return  #TODO error message box
        score = ''.join(self.getcolor(row,col) for row in range(5) for col in range(5))
        print(letters,score)

        wordlist = self.player.search(letters,score,1)
        for i,word in enumerate(wordlist):
            self.suggest.insert('','end',values=(word[1],word[0]))
        self.notbusy()

class GUIplayer(player0):
    def __init__(self, difficulty=['A',5,25]):
        player0.__init__(self, difficulty)

    def search(self, allletters, score, move=1):
        '''returns a list for the GUI to display'''
        start = time()
        wordscores = self.decide(allletters,score,move)
        print(round(time()-start,2),'seconds to decide')
        start = time()
        results = list()
        for (score,word,groupsize,board) in wordscores:
            zeroletters,endingsoon,losing,newscore = self.endgamecheck(allletters,board,move)
            if newscore: #endgame check found a way for opponent to use all remaining squares
                results.append((newscore,word,self.displayscore(board)))
            else:
                results.append((score,word,self.displayscore(board)))
        print(round(time()-start,2),'seconds to endgame check')
        if move == 1:
            return sorted(results, reverse=True)
        else:
            return sorted(results)


if __name__ == '__main__':
    tk = Tk()
    gui = concentrateGUI(tk)
    tk.mainloop()

