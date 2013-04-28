#-------------------------------------------------------------------------------
# Name:        GUI
# Purpose:
#
# Author:      CHRISTOPHER_IRWIN
#
# Created:     31/03/2013

#TODO
#need some way to tell the engine whose turn it is, combo box at the top?
#progress bar dialog
#error message on invalid search
#double-click searched word to add it to the history and update the board
#click on history to show the game at that move (first entry will be beginning of the analysis)
#maybe stretch the board on resize somehow?  or just fix everything with no stretching anywhere...
#menu
    #Options
        #theme
            #light
            #dark
            #pop, etc


from tkinter import *
from tkinter import messagebox
from tkinter import ttk
from player import player0
from time import time
from string import ascii_uppercase
import arena

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
        self.rowconfigure(2, weight=0)

        ttk.Label(self, text='Board').grid(column=0,row=0)
        ttk.Label(self, text='Played Words').grid(column=1,row=0,columnspan=2)
        #btnclear = ttk.Button(self, text='Clear',command=self.canvasdraw)
        #btnclear.grid(column=0,row=0,sticky='NW')
        #btnrandom = ttk.Button(self, text='Random',command=self.randomboard)
        #btnrandom.grid(column=0,row=0,sticky='NE')
        btnsearch = ttk.Button(self, text='Search',command=self.dosearch)
        btnsearch.grid(column=3,row=0,columnspan=2)
        btnsearch['default'] = 'active'

        self.history = ttk.Treeview(self,columns=('Word','Score','Board'), displaycolumns=('Word','Score'),selectmode='browse',show='tree')
        historyscroll = ttk.Scrollbar(self,orient=VERTICAL,command=self.history.yview)
        historyscroll.grid(row=1,column=2,rowspan=2,sticky=(N,S,E))
        self.history['yscrollcommand'] = historyscroll.set
        self.history.grid(row=1,column=1,rowspan=2,sticky=(N,S,W,E))
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
        self.suggest.bind('<<TreeviewSelect>>',self.suggestclick)
        self.suggestselection = -1
        self.suggestignore = False

        self.btnsuggestselect = ttk.Button(self, text='Select',command=self.suggestselect)
        self.btnsuggestselect.grid(row=2,column=3,columnspan=2)
        self.btnsuggestselect.state(['disabled'])

        self.canvasdraw()
        master.bind('<Key>',self.nex)  #to write that character to the square and select the next one
        master.bind('<Up>',self.moveup)
        master.bind('<Down>',self.movedown)
        master.bind('<Left>',self.moveleft)
        master.bind('<Right>',self.moveright)
        master.bind('<BackSpace>',self.backspace)
        master.bind('<Delete>',self.delete)

        self.player = GUIplayer()

        self.menubar = Menu(self, tearoff=0)
        sys = master.tk.call('tk', 'windowingsystem') # will return x11, win32 or aqua

        if sys == 'aqua': #mac os x
            self.concentratemenu = Menu(self.menubar, tearoff=0)
            self.concentratemenu.add_command(label="Random Board", command=self.randomboard, accelerator='Command-R')
            master.bind('<Command-r>',self.randomboard)
            self.concentratemenu.add_command(label="Clear Letters and Colors",  command=self.canvasdraw, accelerator='Command-L')
            master.bind('<Command-l>',self.canvasdraw)
            self.concentratemenu.add_command(label="Clear Colors", command=self.whiteboard, accelerator='Command-C')
            master.bind('<Command-c>',self.whiteboard)
            self.concentratemenu.add_separator()
            self.concentratemenu.add_command(label="Search", command=self.dosearch, accelerator='Command-S')
            master.bind('<Command-s>',self.dosearch)
            self.menubar.add_cascade(label="Concentrate", menu=self.concentratemenu)

            self.optionsmenu = Menu(self.menubar, tearoff=0)
            self.difficulty = StringVar()
            self.optionsmenu.add_radiobutton(label="Easy", variable=self.difficulty, value = "E", command=self.chgdifficulty, accelerator='Command-1')
            master.bind('<Command-Key-1>',self.easydifficulty)
            self.optionsmenu.add_radiobutton(label="Medium", variable=self.difficulty, value = "M", command=self.chgdifficulty, accelerator='Command-2')
            master.bind('<Command-Key-2>',self.mediumdifficulty)
            self.optionsmenu.add_radiobutton(label="Hard", variable=self.difficulty, value = "H", command=self.chgdifficulty, accelerator='Command-3')
            master.bind('<Command-Key-3>',self.harddifficulty)
            self.optionsmenu.add_radiobutton(label="Extreme", variable=self.difficulty, value = "X", command=self.chgdifficulty, accelerator='Command-4')
            master.bind('<Command-Key-4>',self.extremedifficulty)
            self.difficulty.set('H')
            self.menubar.add_cascade(label="Options", menu=self.optionsmenu)


        else: #windows
            self.concentratemenu = Menu(self.menubar, tearoff=0)
            self.concentratemenu.add_command(label="Random Board", underline=0, command=self.randomboard, accelerator='Ctrl+R')
            master.bind('<Control-r>',self.randomboard)
            self.concentratemenu.add_command(label="Clear Letters and Colors", underline=6, command=self.canvasdraw, accelerator='Ctrl+L')
            master.bind('<Control-l>',self.canvasdraw)
            self.concentratemenu.add_command(label="Clear Colors", underline=6, command=self.whiteboard, accelerator='Ctrl+C')
            master.bind('<Control-c>',self.whiteboard)
            self.concentratemenu.add_separator()
            self.concentratemenu.add_command(label="Search", underline=0, command=self.dosearch, accelerator='Ctrl+S')
            master.bind('<Control-s>',self.dosearch)
            self.menubar.add_cascade(label="Board", underline=0, menu=self.concentratemenu)

            self.optionsmenu = Menu(self.menubar, tearoff=0)
            self.difficulty = StringVar()
            self.optionsmenu.add_radiobutton(label="Easy", variable=self.difficulty, value = "E", command=self.chgdifficulty, accelerator='Ctrl+1')
            master.bind('<Control-Key-1>',self.easydifficulty)
            self.optionsmenu.add_radiobutton(label="Medium", variable=self.difficulty, value = "M", command=self.chgdifficulty, accelerator='Ctrl+2')
            master.bind('<Control-Key-2>',self.mediumdifficulty)
            self.optionsmenu.add_radiobutton(label="Hard", variable=self.difficulty, value = "H", command=self.chgdifficulty, accelerator='Ctrl+3')
            master.bind('<Control-Key-3>',self.harddifficulty)
            self.optionsmenu.add_radiobutton(label="Extreme", variable=self.difficulty, value = "X", command=self.chgdifficulty, accelerator='Ctrl+4')
            master.bind('<Control-Key-4>',self.extremedifficulty)
            self.difficulty.set('H')
            self.menubar.add_cascade(label="Options", underline=0, menu=self.optionsmenu)


        master.bind('<Return>',self.dosearch)

        # display the menu
        master.config(menu=self.menubar)

        self.boardcolors = 'w'*25

        self.notbusywidgetcursors = dict() #for busy and notbusy

    def dummy(self):
        pass

    def whiteboard(self, x=1):
         self.updateboard('w'*25)

    def easydifficulty(self,x=0):
        self.difficulty.set('E')
        self.chgdifficulty()

    def mediumdifficulty(self,x=0):
        self.difficulty.set('M')
        self.chgdifficulty()

    def harddifficulty(self,x=0):
        self.difficulty.set('H')
        self.chgdifficulty()

    def extremedifficulty(self,x=0):
        self.difficulty.set('X')
        self.chgdifficulty()

    def chgdifficulty(self):
        self.clearsearch()
        if self.difficulty.get() == 'E':
            self.player.changedifficulty(['R',5,5])
            self.player.difficulty = ['R',5,5]
            self.player.cache = dict()

        elif self.difficulty.get() == 'M':
            self.player.changedifficulty(['R',5,8])

        elif self.difficulty.get() == 'H':
            self.player.changedifficulty(['R',5,25])

        else:
            self.player.changedifficulty(['A',5,25])

    def canvasdraw(self, x=1):
        self.clearsearch()
        self.board = Canvas(self, width=self.boardsize, height=self.boardsize, borderwidth=0, highlightthickness=0, bg='white')
        self.board.grid(row=1,column=0,rowspan=2)

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

    def randomboard(self, x=0):
        self.canvasdraw()
        self.whiteboard()
        letters = arena.genletters()
        for x,c in enumerate(letters):
            row = x // 5
            col = x % 5
            self.board.itemconfig(self.boardstuff[row][col][1],text=c)

    def moveup(self,event):
        (row,col) = self.selected
        nextnum = ((row-1)*5 + col) % 25
        nextrow = nextnum // 5
        nextcol = nextnum % 5
        self.selectsquare(nextrow,nextcol)

    def movedown(self,event):
        (row,col) = self.selected
        nextnum = ((row+1)*5 + col) % 25
        nextrow = nextnum // 5
        nextcol = nextnum % 5
        self.selectsquare(nextrow,nextcol)

    def moveleft(self,event):
        (row,col) = self.selected
        nextnum = (row*5 + col - 1) % 25
        nextrow = nextnum // 5
        nextcol = nextnum % 5
        self.selectsquare(nextrow,nextcol)

    def moveright(self,event):
        (row,col) = self.selected
        nextnum = (row*5 + col + 1) % 25
        nextrow = nextnum // 5
        nextcol = nextnum % 5
        self.selectsquare(nextrow,nextcol)

    def backspace(self,event):
        (row,col) = self.selected
        nextnum = (row*5 + col - 1) % 25
        nextrow = nextnum // 5
        nextcol = nextnum % 5
        self.selectsquare(nextrow,nextcol)
        self.board.itemconfig(self.boardstuff[nextrow][nextcol][1],text='')

    def delete(self,event):
        (row,col) = self.selected
        self.board.itemconfig(self.boardstuff[row][col][1],text='')

    def nex(self,event):
        (row,col) = self.selected
        char = event.char.upper()
        if char in ascii_uppercase and len(char) > 0: #len is used to avoid moving forward with Control/Command buttons
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

    def getdefendedcolor(self,row,col):
        color = self.board.itemcget(self.boardstuff[row][col][0],'fill')
        if color == self.blue[0]:
            return 'b'
        if color == self.blue[1]:
            return 'B'
        if color == self.red[0]:
            return 'r'
        if color == self.red[1]:
            return 'R'
        else:
            return '-'


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

    def clearsearch(self):
        for iid in self.suggest.get_children():
            self.suggest.delete(iid)

    def saveboard(self):
        '''saves the state of the board for later retrieval'''
        board = ''
        for row in range(5):
            for col in range(5):
                board += self.getdefendedcolor(row,col)
        self.boardcolors = board

    def restoreboard(self):
        '''restores the state of the board saved by saveboard'''
        self.updateboard(self.boardcolors)
        pass

    def updateboard(self, newboard):
        '''changes the colors of the board'''
        newboard = newboard.replace(' ','')
        #self.board.itemconfig(self.boardstuff[row][col][0],fill=self.blue[1])
        for row in range(5):
            for col in range(5):
                i = row*5+col
                l = newboard[i]
                color = ''
                if l == 'b':
                    color = self.blue[0]
                elif l == 'B':
                    color = self.blue[1]
                elif l == 'r':
                    color = self.red[0]
                elif l == 'R':
                    color = self.red[1]
                self.board.itemconfig(self.boardstuff[row][col][0],fill=color)

    def suggestclick(self, event):
        '''tied to suggest.<<TreeviewSelect>>'''
        if not self.suggestignore:
            #columns=('Word', 'Score','Board')
            #get item id clicked on
            clickediid = self.suggest.focus()
            if self.suggestselection != clickediid:
                self.suggestselection = clickediid
                txt = self.suggest.set(clickediid,'Word')
                board = self.suggest.set(clickediid,'Board')
                if txt == "click for more...":
                    #delete the last entry (click for more...)
                    last = ''
                    #get number of words in suggest
                    amt = 0
                    for iid in self.suggest.get_children():
                        last = iid
                        amt += 1
                    self.suggest.delete(last)
                    #call do search with lastdisplayed
                    self.dosearch(lastdisplayed=amt-1)

                else:
                    #update colors on the board to match the board of the word suggested
                    self.updateboard(board)
                    self.btnsuggestselect.state(['!disabled'])

            else:
                self.suggestignore = True
                self.suggest.selection_remove(clickediid)
                self.btnsuggestselect.state(['disabled'])
                self.suggestselection = -1
                self.restoreboard()
        else:
            self.suggestignore = False


    def suggestselect(self):
        item = self.suggest.focus()
        print ("you selected", self.suggest.set(item,'Word'))


    def dosearch(self, x=1, lastdisplayed=-1):
        self.busy()
        self.saveboard() #to restore back to when the user un-selects a word
        if lastdisplayed == -1:
            self.clearsearch()
        letters = ''.join([self.board.itemcget(self.boardstuff[row][col][1], 'text') for row in range(5) for col in range(5)])
        if not(all([x in ascii_uppercase for x in letters]) and len(letters) == 25):
            self.notbusy()
            messagebox.showwarning("Concentrate","The board must be completely filled with letters.")
            return
        score = ''.join(self.getcolor(row,col) for row in range(5) for col in range(5))

        wordlist = self.player.search(letters,score,1,lastdisplayed)
        for i,word in enumerate(wordlist):
            self.suggest.insert('','end',values=(word[1],word[0],word[2]))
        self.suggest.insert('','end',values=('click for more...',))
        self.notbusy()


class GUIplayer(player0):
    def __init__(self, difficulty=['R',5,25]):
        player0.__init__(self, difficulty)

    def search(self, allletters, score, move, lastdisplayed):
        '''returns a list for the GUI to display'''
        if lastdisplayed == -1:
            start = time()
            self.wordscores = self.decide(allletters,score,move)
            if move == 1:
                self.wordscores.sort(reverse=True)
            else:
                self.wordscores.sort()
            decidetime = round(time() - start,2)
            plays = len(self.wordscores)
            rate = int(plays/decidetime)
            print(decidetime,'seconds to decide')
            print(plays,'plays found,',rate,'per second')
        start = time()
        results = list()
        amounttodisplay = 20
        displayed = 0
        for wordnum,(score,word,groupsize,blue,red,bluedef,reddef) in enumerate(self.wordscores):
            if wordnum > lastdisplayed and displayed < amounttodisplay:
                zeroletters,endingsoon,losing,newscore = self.endgamecheck(allletters,blue,red,bluedef,reddef,move)
                if losing: #endgame check found a way for opponent to win
                   results.append((score,'-'+word,self.displayscore(blue,red,bluedef,reddef)))
                   displayed += 1
                elif endingsoon: #endgame check only found way for opponent to end game, but not win
                   results.append((score,'*'+word,self.displayscore(blue,red,bluedef,reddef)))
                   displayed += 1
                else:
                    results.append((score,word,self.displayscore(blue,red,bluedef,reddef)))
                    displayed += 1
            elif displayed >= amounttodisplay:
                break
        print(round(time()-start,2),'seconds to endgame check')
        return results


if __name__ == '__main__':
    tk = Tk()
    gui = concentrateGUI(tk)
    tk.mainloop()

