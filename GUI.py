#-------------------------------------------------------------------------------
# Name:        GUI
# Purpose:
#
# Author:      CHRISTOPHER IRWIN
#
# Created:     31/03/2013
# Copyright:   (c) CHRISTOPHER IRWIN 2013

#TODO

#progress bar dialog?

#menu
    #Options
        #theme
            #light
            #dark
            #pop, etc


from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
from tkinter import ttk
from player import player0
from time import time
from string import ascii_uppercase
from random import choice
from os import path
import arena
import pickle

class concentrateGUI(Tk):

    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)

        self.boardstuff = [[None for x in range(5)] for y in range(5)]  #holds rectangles and text on the board
        self.boardsize = 250
        self.sqsize = self.boardsize//5
        self.blue = ('light sky blue','RoyalBlue2')
        self.red = ('salmon','red')
        self.initialhist= '[Initial Position]'
        self.moretxt = 'Click for More...'
        self.notxt = 'No Results'
        self.titletx = 'Concentrate'
        self.titlesp = ' - '

        self.title("Concentrate")
        #self.columnconfigure(0, weight=1)
        #self.rowconfigure(0, weight=0)
        self.resizable(0,0)

        self.topframe = ttk.Frame(self)
        self.topframe.grid(row=0,column=0)
        

        #self.master = master
        #frame = Frame(self)
        #frame.grid(column=0, row=0, sticky=(N, S, E, W))
        self.topframe.columnconfigure(0, weight=0)
        self.topframe.columnconfigure(1, weight=0)
        self.topframe.columnconfigure(2, weight=0) #scroll bar 
        self.topframe.columnconfigure(3, weight=0)
        self.topframe.columnconfigure(4, weight=0) #scroll bar
        self.topframe.rowconfigure(0, weight=0)
        self.topframe.rowconfigure(1, weight=1)
        self.topframe.rowconfigure(2, weight=0)

        ttk.Label(self.topframe, text='Board').grid(column=0,row=0)
        ttk.Label(self.topframe, text='History').grid(column=1,row=0,columnspan=2)
        self.need = ttk.Entry(self.topframe)
        self.need.grid(column=3,row=0,padx=10,sticky=(W))
        btnsearch = ttk.Button(self.topframe, text='Search',command=self.dosearch)
        btnsearch.grid(column=3,row=0,padx=10,sticky=(E))
        btnsearch['default'] = 'active'

        self.history = ttk.Treeview(self.topframe,columns=('Word','Score','Board','Letters'), displaycolumns=('Word','Score'),selectmode='browse',show='tree')
        historyscroll = ttk.Scrollbar(self.topframe,orient=VERTICAL,command=self.history.yview)
        historyscroll.grid(row=1,column=2,rowspan=2,sticky=(N,S,E))
        self.history['yscrollcommand'] = historyscroll.set
        self.history.grid(row=1,column=1,rowspan=2,sticky=(N,S,W,E))
        self.history.column('#0',width=1)
        self.history.column(0,width=150)
        self.history.column(1,width=75)
        self.history.bind('<<TreeviewSelect>>',self.historyclick)
        self.history.tag_configure('red',foreground='red')
        self.history.tag_configure('blue',foreground='RoyalBlue2')
        self.historyselection = -1
        self.historyignore= False

        self.suggest = ttk.Treeview(self.topframe,columns=('Word','Score','Board'), displaycolumns=('Word','Score'),selectmode='browse',show='tree')
        suggestscroll = ttk.Scrollbar(self.topframe,orient=VERTICAL,command=self.suggest.yview)
        suggestscroll.grid(row=1,column=4,sticky=(N,S,E))
        self.suggest['yscrollcommand'] = suggestscroll.set

        self.suggest.grid(row=1,column=3,sticky=(N,S,W,E))
        self.suggest.column('#0',width=1)
        self.suggest.column(0,width=150)
        self.suggest.column(1,width=75)
        self.suggest.bind('<<TreeviewSelect>>',self.suggestclick)
        self.suggest.tag_configure('-',foreground='red')
        self.suggest.tag_configure('*',foreground='forest green')
        self.suggestselection = -1
        self.suggestignore = False

        self.btnsuggestselect = ttk.Button(self.topframe, text='Select',command=self.suggestselect)
        self.btnsuggestselect.grid(row=2,column=3,columnspan=2,pady=0,sticky=(N,S))
        self.btnsuggestselect.state(['disabled'])

        self.sys = self.tk.call('tk', 'windowingsystem') # will return x11, win32 or aqua
        self.move = IntVar()
        self.canvasdraw()

        self.player = GUIplayer()

        self.menubar = Menu(self, tearoff=0)

        self.file = None

        if self.sys == 'aqua': #mac os x
            self.filemenu= Menu(self.menubar, tearoff=0)
            self.filemenu.add_command(label="New", underline=0, command=self.new, accelerator='Command-N')
            self.bind('<Command-n>',self.new)
            self.filemenu.add_command(label="Open...", underline=0, command=self.open, accelerator='Command-O')
            self.bind('<Command-o>',self.open)
            self.filemenu.add_command(label="Save",underline=0, command=self.save, accelerator='Command-S')
            self.bind('<Command-s>',self.save)
            self.filemenu.add_command(label="Save As...", underline=5, command=self.saveas, accelerator='Command+A')
            self.bind('<Command-a>',self.saveas)
            self.menubar.add_cascade(label="Concentrate", underline=0, menu=self.filemenu)

            self.boardmenu = Menu(self.menubar, tearoff=0)

            self.boardmenu.add_command(label="Empty Board",  command=self.canvasdraw, accelerator='Command-E')
            self.bind('<Command-e>',self.canvasdraw)
            self.boardmenu.add_command(label="White Board", command=self.whiteboard, accelerator='Command-W')
            self.bind('<Command-w>',self.whiteboard)
            self.boardmenu.add_command(label="Random Letters", command=self.randomboard, accelerator='Command-R')
            self.bind('<Command-r>',self.randomboard)
            self.boardmenu.add_command(label="Random Colors", underline=7, command=self.randomcolors, accelerator='Command-C')
            self.bind('<Command-c>',self.randomcolors)
            self.boardmenu.add_separator()
            self.boardmenu.add_command(label="Search", command=self.dosearch, accelerator='Return')
            self.menubar.add_cascade(label="Board", menu=self.boardmenu)

            self.optionsmenu = Menu(self.menubar, tearoff=0)
            self.difficulty = StringVar()
            self.optionsmenu.add_radiobutton(label="Easy", variable=self.difficulty, value = "E", command=self.chgdifficulty, accelerator='Command-1')
            self.bind('<Command-Key-1>',self.easydifficulty)
            self.optionsmenu.add_radiobutton(label="Medium", variable=self.difficulty, value = "M", command=self.chgdifficulty, accelerator='Command-2')
            self.bind('<Command-Key-2>',self.mediumdifficulty)
            self.optionsmenu.add_radiobutton(label="Hard", variable=self.difficulty, value = "H", command=self.chgdifficulty, accelerator='Command-3')
            self.bind('<Command-Key-3>',self.harddifficulty)
            self.optionsmenu.add_radiobutton(label="Extreme", variable=self.difficulty, value = "X", command=self.chgdifficulty, accelerator='Command-4')
            self.bind('<Command-Key-4>',self.extremedifficulty)
            self.difficulty.set('H')
            self.optionsmenu.add_separator()
            self.optionsmenu.add_radiobutton(label="Blue to Play", variable=self.move, value = 1, command=self.blueturn)
            self.optionsmenu.add_radiobutton(label="Red to Play", variable=self.move, value = -1, command=self.redturn)
            self.move.set(1)
            self.menubar.add_cascade(label="Options", menu=self.optionsmenu)


        else: #windows
            self.filemenu= Menu(self.menubar, tearoff=0)
            self.filemenu.add_command(label="New", underline=0, command=self.new, accelerator='Ctrl+N')
            self.bind('<Control-n>',self.new)
            self.filemenu.add_command(label="Open...", underline=0, command=self.open, accelerator='Ctrl+O')
            self.bind('<Control-o>',self.open)
            self.filemenu.add_command(label="Save",underline=0, command=self.save, accelerator='Ctrl+S')
            self.bind('<Control-s>',self.save)
            self.filemenu.add_command(label="Save As...", underline=5, command=self.saveas, accelerator='Ctrl+A')
            self.bind('<Control-a>',self.saveas)
            self.menubar.add_cascade(label="File", underline=0, menu=self.filemenu)
            self.boardmenu = Menu(self.menubar, tearoff=0)
            self.boardmenu.add_command(label="Empty Board", underline=6, command=self.canvasdraw, accelerator='Ctrl+E')
            self.bind('<Control-e>',self.canvasdraw)
            self.boardmenu.add_command(label="White Board", underline=6, command=self.whiteboard, accelerator='Ctrl+W')
            self.bind('<Control-w>',self.whiteboard)
            self.boardmenu.add_command(label="Random Letters", underline=0, command=self.randomboard, accelerator='Ctrl+R')
            self.bind('<Control-r>',self.randomboard)
            self.boardmenu.add_command(label="Random Colors", underline=7, command=self.randomcolors, accelerator='Ctrl+C')
            self.bind('<Control-c>',self.randomcolors)
            self.boardmenu.add_separator()
            self.boardmenu.add_command(label="Search", underline=0, command=self.dosearch, accelerator='Enter')
            self.menubar.add_cascade(label="Board", underline=0, menu=self.boardmenu)
            self.optionsmenu = Menu(self.menubar, tearoff=0)
            self.difficulty = StringVar()
            self.optionsmenu.add_radiobutton(label="Easy", variable=self.difficulty, value = "E", command=self.chgdifficulty, accelerator='Ctrl+1')
            self.bind('<Control-Key-1>',self.easydifficulty)
            self.optionsmenu.add_radiobutton(label="Medium", variable=self.difficulty, value = "M", command=self.chgdifficulty, accelerator='Ctrl+2')
            self.bind('<Control-Key-2>',self.mediumdifficulty)
            self.optionsmenu.add_radiobutton(label="Hard", variable=self.difficulty, value = "H", command=self.chgdifficulty, accelerator='Ctrl+3')
            self.bind('<Control-Key-3>',self.harddifficulty)
            self.optionsmenu.add_radiobutton(label="Extreme", variable=self.difficulty, value = "X", command=self.chgdifficulty, accelerator='Ctrl+4')
            self.bind('<Control-Key-4>',self.extremedifficulty)
            self.difficulty.set('H')
            self.optionsmenu.add_separator()
            self.optionsmenu.add_radiobutton(label="Blue to Play", variable=self.move, value = 1, command=self.blueturn)
            self.optionsmenu.add_radiobutton(label="Red to Play", variable=self.move, value = -1, command=self.redturn)
            self.move.set(1)
            self.menubar.add_cascade(label="Options", underline=0, menu=self.optionsmenu)

        self.bind('<Return>',self.dosearch)

        # display the menu
        self.config(menu=self.menubar)

        self.boardcolors = 'w'*25

        self.notbusywidgetcursors = dict() #for busy and notbusy
        self.board.focus_set()

    def loophist(self,event):
        for iid in self.history.get_children():
            if iid == self.historyselection:
                print(iid,'<- selected')
            else:
                print(iid)

    def new(self,event=None):
        '''closes any previously open file, erases board, history, search'''
        if self.file != None:
            self.file = None
        self.title(self.titletx)
        self.canvasdraw()

    def open(self,event=None):
        '''presents file dialog box for selecting one file.  loads data to the board and history'''
        self.canvasdraw()
        fn = filedialog.askopenfilename(filetypes=[('Concentrate Game Document', '.cgd')])
        print(fn)
        if fn != '':
            self.file = fn
            f = open(self.file,'rb')
            lst = pickle.load(f)
            f.close()
            for iidr,word,score,board,letters,color in lst:
                insertid = self.history.insert('','end',iid=iidr,tag=color,values=(word,score,board,letters))
            if len(lst) > 0: #file could be an empty list
                for i,l in enumerate(letters):
                    row = i//5
                    col = i%5
                    self.board.itemconfig(self.boardstuff[row][col][1],text=l)
                #self.historyignore=True
                self.history.focus(iidr)
                self.history.selection_set(iidr)
                self.historyselection = iidr
                self.history.see(iidr)
                self.title(self.titletx+self.titlesp+path.basename(self.file))


    def save(self,event=None):
        '''loops over the history and saves to the current open file'''
        savelst = []
        if self.file == None:
            self.file = filedialog.asksaveasfilename(filetypes=[('Concentrate Game Document', '.cgd')])
            print(self.file[-4:])
            self.title(self.titletx+self.titlesp+path.basename(self.file))
        f = open(self.file,'wb')
        for iid in self.history.get_children():
            word = self.history.set(iid,'Word')
            score = self.history.set(iid,'Score')
            board = self.history.set(iid,'Board')
            letters = self.history.set(iid,'Letters')
            if self.history.tag_has('blue', item=iid):
                savelst.append((iid,word,score,board,letters,'blue'))
            elif self.history.tag_has('red', item=iid):
                savelst.append((iid,word,score,board,letters,'red'))
            else:
                savelst.append((iid,word,score,board,letters,''))
        pickle.dump(savelst,f)
        self.title(self.titletx+self.titlesp+path.basename(self.file))
        f.close()

    def saveas(self,event=None):
        '''loops over the history and presents the file save dialog box'''
        fn = filedialog.asksaveasfilename(filetypes=[('Concentrate Game Document', '.cgd')])
        if fn != '':
            self.file = fn
            self.save()
            self.title(self.titletx+self.titlesp+path.basename(self.file))

    def blueturn(self,event=None):
        self.move.set(1)

    def redturn(self,event=None):
        self.move.set(-1)

    def whiteboard(self, event=None):
         self.updateboard('w'*25)

    def easydifficulty(self,event=None):
        self.difficulty.set('E')
        self.chgdifficulty()

    def mediumdifficulty(self,event=None):
        self.difficulty.set('M')
        self.chgdifficulty()

    def harddifficulty(self,event=None):
        self.difficulty.set('H')
        self.chgdifficulty()

    def extremedifficulty(self,event=None):
        self.difficulty.set('X')
        self.chgdifficulty()

    def chgdifficulty(self):
        self.clearsearch()
        self.restoreboard()
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

    def canvasdraw(self, event=None):
        self.clearsearch()
        self.clearhistory()
        self.board = Canvas(self.topframe, width=self.boardsize, height=self.boardsize, borderwidth=0, highlightthickness=1, bg='white')
        self.board.grid(row=1,column=0,rowspan=2)
        self.move.set(1)

        self.board.bind('<Button-1>',self.chgcolor)
        self.board.bind('<Key>',self.nex)  #to write that character to the square and select the next one

        if self.sys != 'aqua': #these special key bindings are handled on the mac by the key binding above, self.nex
            self.board.bind('<Up>',self.moveup)
            self.board.bind('<Down>',self.movedown)
            self.board.bind('<Left>',self.moveleft)
            self.board.bind('<Right>',self.moveright)
            self.board.bind('<BackSpace>',self.backspace)
            self.board.bind('<Delete>',self.delete)

        for row in range(5):
            for col in range(5):
                top = row * self.sqsize + 1
                left = col * self.sqsize + 1
                bottom = row * self.sqsize + self.sqsize
                right = col * self.sqsize + self.sqsize
                rect = self.board.create_rectangle(left,top,right,bottom,outline='gray',fill='')
                text = self.board.create_text(left+self.sqsize/2, top+self.sqsize/2,text='',font='Helvetica 20')
                self.boardstuff[row][col] = (rect,text)
        self.board.focus_set()
        self.selectsquare(0,0)

    def randomboard(self, event=None):
        go = True
        if len(self.history.get_children()) > 0:
            if messagebox.askyesno('Are you sure?','Editing the letters on the board will clear the history and search box.  Proceed?'):
                self.clearhistory()
                self.clearsearch()
            else:
                go = False
        if go:
            letters = arena.genletters()
            for x,c in enumerate(letters):
                row = x // 5
                col = x % 5
                self.board.itemconfig(self.boardstuff[row][col][1],text=c)
            self.board.focus_set()

    def randomcolors(self, event=None):
        self.whiteboard()
        colors = [choice(['','blue','red']) for x in range(25)]
        for x,c in enumerate(colors):
            self.updatecolors(x//5,x%5,c)
        self.board.focus_set()
        #print(self.board.focus_get().winfo_class())

    def moveup(self,event):  #these methods work on windows, mac is handled by self.nex
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
        self.board.focus_set()
        self.board.focus()
        if self.sys == 'aqua':
            nomodifier = 0
        else:
            nomodifier = 8
        char = event.char.upper()
        if char in ascii_uppercase and len(char) > 0 and event.state == nomodifier: #len is used to avoid moving forward with Control/Command buttons alone
                                                                                    #event.state is used to avoid doing the same for Command-key on the mac
            go = True
            if len(self.history.get_children()) > 0:
                if messagebox.askyesno('Are you sure?','Editing the letters on the board will clear the history and search box.  Do you want to proceed?'):
                    self.clearhistory()
                    self.clearsearch()
                else:
                    go = False
            if go:
                self.board.itemconfig(self.boardstuff[row][col][1],text=char)
                nextnum = (row*5 + col + 1) % 25
                nextrow = nextnum // 5
                nextcol = nextnum % 5
                self.selectsquare(nextrow,nextcol)
        elif len(char) > 0:  #works on the mac, not on windows
            keynum = ord(event.char)
            if keynum == 63232: #up
                nextnum = ((row-1)*5 + col) % 25
                nextrow = nextnum // 5
                nextcol = nextnum % 5
                self.selectsquare(nextrow,nextcol)
            elif keynum == 63233: #down
                nextnum = ((row+1)*5 + col) % 25
                nextrow = nextnum // 5
                nextcol = nextnum % 5
                self.selectsquare(nextrow,nextcol)
            elif keynum == 63234: #left
                nextnum = (row*5 + col - 1) % 25
                nextrow = nextnum // 5
                nextcol = nextnum % 5
                self.selectsquare(nextrow,nextcol)
            elif keynum == 63235: #right
                nextnum = (row*5 + col + 1) % 25
                nextrow = nextnum // 5
                nextcol = nextnum % 5
                self.selectsquare(nextrow,nextcol)
            elif keynum == 127: #backspace
                nextnum = (row*5 + col - 1) % 25
                nextrow = nextnum // 5
                nextcol = nextnum % 5
                self.selectsquare(nextrow,nextcol)
                self.board.itemconfig(self.boardstuff[nextrow][nextcol][1],text='')
            elif keynum == 63272: #delete
                self.board.itemconfig(self.boardstuff[row][col][1],text='')
        #print(self.board.focus_get().winfo_class())

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
        for row in range(5):
            for col in range(5):
                self.board.itemconfig(self.boardstuff[row][col][0],outline='gray')
        self.board.itemconfig(self.boardstuff[selectrow][selectcol][0],outline='black')

    def busy(self, widget=None):
        if widget == None:
            w = self
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

    def clearhistory(self):
        for iid in self.history.get_children():
            self.history.delete(iid)
        self.historyselection=-1

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

    def historyclick(self, event):
        '''bound to history.<<TreeviewSelect>>'''

        if not self.historyignore:
            #get item id clicked on
            clickediid = self.history.focus()
            self.historyselection = clickediid
            txt = self.history.set(clickediid,'Word')
            board = self.history.set(clickediid,'Board')
            #update colors on the board to match the board of the word suggested
            self.updateboard(board)
            self.history.focus_set()
            #unselect suggest selection, if any
            sugselect = self.suggest.focus()
            self.suggestignore = True
            self.suggest.selection_remove(sugselect)
            self.btnsuggestselect.state(['disabled'])
            self.suggestselection = -1
            #set whose turn it is based on the selection
            if self.history.tag_has('red',clickediid):
                self.move.set(1)
            elif self.history.tag_has('blue',clickediid):
                self.move.set(-1)
            else:
                #untagged first id, look at next id
                nextid = self.history.next(clickediid)
                if self.history.tag_has('red',nextid):
                    self.move.set(-1)
                else:
                    self.move.set(1)

        else:
            self.historyignore = False


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
                if txt != self.notxt:
                    if txt == self.moretxt:
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
                        #remove selection from history
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
        #print ("you selected", self.suggest.set(item,'Word'))
        #clear history past the current selection
        txt = ''
        if self.historyselection != -1:
            txt = self.history.set(self.historyselection,'Word')
            todelete = []
            if txt == self.initialhist:
                todelete.append(self.historyselection)
            iid = self.history.next(self.historyselection)
            while iid != '':
                todelete.append(iid)
                iid = self.history.next(iid)
            for iid in todelete:
                self.history.delete(iid)
        #check if the history treeview is empty
        cnt = len(self.history.get_children())
        if cnt == 0:
            self.history.insert('','end',values=(self.initialhist,'' ,self.boardcolors,self.letters))
        #copy the word, board, and score to the end of the history treeview
        txt = self.suggest.set(item,'Word')
        score = self.suggest.set(item,'Score')
        board = self.suggest.set(item,'Board')
        #print('saving move:',txt,score,board)
        insertid = 0
        if self.move.get() == 1:
            insertid = self.history.insert('','end',tag='blue',values=(txt,score,board,self.letters))
        else:
            insertid = self.history.insert('','end',tag='red',values=(txt,score,board,self.letters))
        #select the inserted item in history
        self.historyignore=True
        self.history.selection_set(insertid)
        self.historyselection = insertid
        self.history.see(insertid)
        #change whose turn it is
        self.move.set(-self.move.get())
        self.clearsearch()
        self.need.delete(0,len(self.need.get()))
        if self.title()[-1] != '*':
            self.title(self.title()+'*')

    def dosearch(self, x=1, lastdisplayed=-1):
        self.busy()
        self.saveboard() #to restore back to when the user un-selects a word
        if lastdisplayed == -1:
            self.clearsearch()
        #self.letters is used by suggestselect to save the board letters to history
        self.letters = ''.join([self.board.itemcget(self.boardstuff[row][col][1], 'text') for row in range(5) for col in range(5)])
        if not(all([x in ascii_uppercase for x in self.letters]) and len(self.letters) == 25):
            self.notbusy()
            messagebox.showwarning("Concentrate","The board must be completely filled with letters.")
            return
        score = ''.join(self.getcolor(row,col) for row in range(5) for col in range(5))
        if 'W' not in score:
            self.notbusy()
            messagebox.showwarning("Concentrate","Game Over.")
            return
        #make the engine aware of which words are in the history
        words = list()
        for iid in self.history.get_children():
            txt = self.history.set(iid,'Word')
            if txt != self.initialhist:
                words.append(txt)
            if iid == self.historyselection:
                break
        needletters = self.need.get().upper()
        self.player.possible(self.letters)
        self.player.resetplayed(self.letters,words)
        wordlist,more = self.player.search(self.letters,score,needletters,self.move.get(),lastdisplayed)
        for i,word in enumerate(wordlist):
            if word[1][0] not in ascii_uppercase:
                self.suggest.insert('','end',tag=word[1][0],values=(word[1][1:],word[0],word[2]))
            else:
                self.suggest.insert('','end',values=(word[1],word[0],word[2]))
        if more:
            self.suggest.insert('','end',values=(self.moretxt,))
        elif len(self.suggest.get_children()) == 0:
            self.suggest.insert('','end',values=(self.notxt,))
        if lastdisplayed == -1:
            self.suggest.see(self.suggest.get_children()[0])
        self.notbusy()


class GUIplayer(player0):
    def __init__(self, difficulty=['R',5,25]):
        player0.__init__(self, difficulty)

    def search(self, allletters, score, needletters, move, lastdisplayed):
        '''returns a list for the GUI to display'''
        if lastdisplayed == -1:
            start = time()
            self.wordscores = self.decide(allletters,score,needletters,move)
            if move == 1:
                self.wordscores.sort(reverse=True)
            else:
                self.wordscores.sort()
            decidetime = time() - start
            plays = len(self.wordscores)
            rate = int(plays/decidetime)
            print(round(decidetime,2),'seconds to decide',allletters,score)
            print(plays,'plays found,',rate,'per second')
        start = time()
        results = list()
        amounttodisplay = 200
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
                print(round(time()-start,2),'seconds to endgame check')
                return results,True
        print(round(time()-start,2),'seconds to endgame check')
        return results,False

if __name__ == '__main__':
    concentrateGUI().mainloop()
