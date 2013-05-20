#-------------------------------------------------------------------------------
# Name:        GUI
# Purpose:
#
# Author:      CHRISTOPHER IRWIN
#
# Created:     31/03/2013
# Copyright:   (c) CHRISTOPHER IRWIN 2013


from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
from tkinter import ttk
from player import player0
from time import time
from string import ascii_uppercase
from random import choice, sample
from os import path
import arena
import pickle


class AnalysisGUI(Tk):

    def __init__(self, *args, **kwargs):
        Tk.__init__(self)

        #not working correctly TODO
##        img = PhotoImage('concentrate.gif')
##        self.tk.call('wm', 'iconphoto', self._w, img)

        dct = kwargs.get('dct',dict())

        self.file = kwargs.get('file','')
        title = kwargs.get('title','')
        self.themeName = kwargs.get('themeName','')

        self.boardStuff = [[None for x in range(5)] for y in range(5)]  #holds rectangles and text on the board
        self.boardSize = 250
        self.squareSize = self.boardSize//5

        self.initialHist= '[Initial Position]'
        self.moreText = 'Click for More...'
        self.titleText = 'Concentrate'
        self.noText= 'No Results'
        self.titleSeparator = ' - '

        #default theme is 'light'
        self.defaultColor = '#%02x%02x%02x' % (240, 240, 240)  # different from iOS app
        self.blue= ('#%02x%02x%02x' % (120, 200, 245), '#%02x%02x%02x' % (0, 162, 255))
        self.red = ('#%02x%02x%02x' % (247, 153, 141), '#%02x%02x%02x' % (255, 67, 47))
        self.defaultText= '#%02x%02x%02x' % (46, 45, 45)
        self.blueText= ('#%02x%02x%02x' % (24, 40, 49), '#%02x%02x%02x' % (0, 32, 51))
        self.redText = ('#%02x%02x%02x' % (49, 30, 28), '#%02x%02x%02x' % (51, 13, 9))
        #these are for PlayGUI, but wanted change_theme to be inherited, so defining in both places
        self.selectedBlue = ('#%02x%02x%02x' % (90, 190, 243), '#%02x%02x%02x' % (0, 139, 223))
        self.selectedRed = ('#%02x%02x%02x' % (249, 129, 112), '#%02x%02x%02x' % (255, 39, 15))
        self.selectedDefault = '#%02x%02x%02x' % (224, 224, 224)


        if title == '':
            self.title(self.titleText)
        else:
            self.title(title)

        #self.columnconfigure(0, weight=1)
        #self.rowconfigure(0, weight=0)
        self.resizable(0,0)

        self.topFrame = ttk.Frame(self)
        self.topFrame.grid(row=0,column=0)

        #self.master = master
        #frame = Frame(self)
        #frame.grid(column=0, row=0, sticky=(N, S, E, W))
        self.topFrame.columnconfigure(0, weight=0)
        self.topFrame.columnconfigure(1, weight=0)
        self.topFrame.columnconfigure(2, weight=0) #scroll bar
        self.topFrame.columnconfigure(3, weight=0)
        self.topFrame.columnconfigure(4, weight=0) #scroll bar
        self.topFrame.rowconfigure(0, weight=0)
        self.topFrame.rowconfigure(1, weight=1)
        self.topFrame.rowconfigure(2, weight=0)

        ttk.Label(self.topFrame, text='Board').grid(column=0,row=0)
        ttk.Label(self.topFrame, text='History').grid(column=1,row=0,columnspan=2)
        self.need = ttk.Entry(self.topFrame)
        self.need.grid(column=3,row=0,padx=10,sticky=(W))
        btnSearch = ttk.Button(self.topFrame, text='Search', command=self.do_search)
        btnSearch.grid(column=3, row=0, padx=10, sticky=(E))
        btnSearch['default'] = 'active'

        self.history = ttk.Treeview(self.topFrame,columns=('Word','Score','Board','Letters'), displaycolumns=('Word','Score'),selectmode='browse',show='tree')
        historyScroll = ttk.Scrollbar(self.topFrame,orient=VERTICAL,command=self.history.yview)
        historyScroll.grid(row=1,column=2,rowspan=2,sticky=(N,S,E))
        self.history['yscrollcommand'] = historyScroll.set
        self.history.grid(row=1,column=1,rowspan=2,sticky=(N,S,W,E))
        self.history.column('#0',width=1)
        self.history.column(0,width=150)
        self.history.column(1,width=75)
        self.history.bind('<<TreeviewSelect>>',self.history_click)
        self.history.tag_configure('red', foreground=self.red[1])
        self.history.tag_configure('blue', foreground=self.blue[1])
        self.historySelection = -1
        self.historyIgnore = False

        self.suggest = ttk.Treeview(self.topFrame,columns=('Word','Score','Board'), displaycolumns=('Word','Score'),selectmode='browse',show='tree')
        suggestScroll = ttk.Scrollbar(self.topFrame,orient=VERTICAL,command=self.suggest.yview)
        suggestScroll.grid(row=1,column=4,sticky=(N,S,E))
        self.suggest['yscrollcommand'] = suggestScroll.set

        self.suggest.grid(row=1,column=3,sticky=(N,S,W,E))
        self.suggest.column('#0',width=1)
        self.suggest.column(0,width=150)
        self.suggest.column(1,width=75)
        self.suggest.bind('<<TreeviewSelect>>',self.suggest_click)
        self.suggest.tag_configure('-',foreground='red')
        self.suggest.tag_configure('*',foreground='forest green')
        self.suggestSelection = -1
        self.suggestIgnore = False

        self.btnSuggestSelect = ttk.Button(self.topFrame, text='Select',command=self.suggest_select)
        self.btnSuggestSelect.grid(row=2,column=3,columnspan=2,pady=0,sticky=(N,S))
        self.btnSuggestSelect.state(['disabled'])

        self.sys = self.tk.call('tk', 'windowingsystem') # will return x11, win32 or aqua
        self.move = IntVar()
        self.move.set(1)
        self.theme = IntVar()
        self.theme.set(0)
        self.player = AnalysisPlayer()
        self.menuBar = Menu(self, tearoff=0)

        if self.sys == 'aqua':  # mac os x
            self.fileMenu= Menu(self.menuBar, tearoff=0)
            self.fileMenu.add_command(label="New", underline=0, command=self.new, accelerator='Command-N')
            self.bind('<Command-n>',self.new)
            self.fileMenu.add_command(label="Open...", underline=0, command=self.open, accelerator='Command-O')
            self.bind('<Command-o>',self.open)
            self.fileMenu.add_command(label="Save",underline=0, command=self.save, accelerator='Command-S')
            self.bind('<Command-s>',self.save)
            self.fileMenu.add_command(label="Save As...", underline=5, command=self.save_as, accelerator='Command+A')
            self.bind('<Command-a>',self.save_as)
            self.menuBar.add_cascade(label="Concentrate", underline=0, menu=self.fileMenu)

            self.boardMenu = Menu(self.menuBar, tearoff=0)

            self.boardMenu.add_command(label="Empty Board",  command=self.canvas_draw, accelerator='Command-E')
            self.bind('<Command-e>',self.canvas_draw)
            self.boardMenu.add_command(label="White Board", command=self.white_board, accelerator='Command-W')
            self.bind('<Command-w>',self.white_board)
            self.boardMenu.add_command(label="Random Letters", command=self.random_board, accelerator='Command-R')
            self.bind('<Command-r>',self.random_board)
            self.boardMenu.add_command(label="Random Colors", underline=7, command=self.random_colors, accelerator='Command-C')
            self.bind('<Command-c>',self.random_colors)
            self.boardMenu.add_separator()
            self.boardMenu.add_command(label="Search", command=self.do_search, accelerator='Return')
            self.menuBar.add_cascade(label="Board", menu=self.boardMenu)

            self.optionsMenu = Menu(self.menuBar, tearoff=0)
            self.optionsMenu.add_command(label="Play Against Concentrate", underline=0, command=self.play_against, accelerator='Tab')
            self.bind('<Tab>',self.play_against)
            self.optionsMenu.add_separator()

            self.themeMenu= Menu(self.optionsMenu, tearoff=0)
            self.themeMenu.add_radiobutton(label="Light", underline=0, variable=self.theme, value=0, command=lambda: self.change_theme('light'))
            self.themeMenu.add_radiobutton(label="Pop", underline=0, variable=self.theme, value=1, command=lambda: self.change_theme('pop'))
            self.themeMenu.add_radiobutton(label="Retro", underline=0, variable=self.theme, value=2, command=lambda: self.change_theme('retro'))
            self.themeMenu.add_radiobutton(label="Dark", underline=0, variable=self.theme, value=3, command=lambda: self.change_theme('dark'))
            self.themeMenu.add_radiobutton(label="Forest", underline=0, variable=self.theme, value=4, command=lambda: self.change_theme('forest'))
            self.themeMenu.add_radiobutton(label="Glow", underline=0, variable=self.theme, value=5, command=lambda: self.change_theme('glow'))
            self.themeMenu.add_radiobutton(label="Pink", underline=1, variable=self.theme, value=6, command=lambda: self.change_theme('pink'))
            self.themeMenu.add_radiobutton(label="Contrast", underline=0, variable=self.theme, value=7, command=lambda: self.change_theme('contrast'))
            self.optionsMenu.add_cascade(label="Theme", underline=0, menu=self.themeMenu)
            self.optionsMenu.add_separator()

            self.difficulty = StringVar()
            self.optionsMenu.add_radiobutton(label="Dunce", underline=0, variable=self.difficulty, value="R", command=self.change_difficulty, accelerator='Command-1')
            self.bind('<Command-Key-1>', lambda x: self.change_difficulty('R'))
            self.optionsMenu.add_radiobutton(label="Easy", underline=0, variable=self.difficulty, value="E", command=self.change_difficulty, accelerator='Command-2')
            self.bind('<Command-Key-2>', lambda x: self.change_difficulty('E'))
            self.optionsMenu.add_radiobutton(label="Medium", underline=0, variable=self.difficulty, value="M", command=self.change_difficulty, accelerator='Command-3')
            self.bind('<Command-Key-3>', lambda x: self.change_difficulty('M'))
            self.optionsMenu.add_radiobutton(label="Hard", underline=0, variable=self.difficulty, value="H", command=self.change_difficulty, accelerator='Command-4')
            self.bind('<Command-Key-4>', lambda x: self.change_difficulty('H'))
            self.optionsMenu.add_radiobutton(label="Extreme", underline=1, variable=self.difficulty, value="X", command=self.change_difficulty, accelerator='Command-5')
            self.bind('<Command-Key-5>', lambda x: self.change_difficulty('X'))
            self.difficulty.set('H')
            self.optionsMenu.add_separator()
            self.optionsMenu.add_radiobutton(label="Blue to Play", variable=self.move, value = 1,
                                             command=self.blue_turn)
            self.optionsMenu.add_radiobutton(label="Red to Play", variable=self.move, value = -1, command=self.red_turn)
            self.menuBar.add_cascade(label="Options", menu=self.optionsMenu)

        else:  # windows
            self.fileMenu= Menu(self.menuBar, tearoff=0)
            self.fileMenu.add_command(label="New", underline=0, command=self.new, accelerator='Ctrl+N')
            self.bind('<Control-n>',self.new)
            self.fileMenu.add_command(label="Open...", underline=0, command=self.open, accelerator='Ctrl+O')
            self.bind('<Control-o>',self.open)
            self.fileMenu.add_command(label="Save",underline=0, command=self.save, accelerator='Ctrl+S')
            self.bind('<Control-s>',self.save)
            self.fileMenu.add_command(label="Save As...", underline=5, command=self.save_as, accelerator='Ctrl+A')
            self.bind('<Control-a>',self.save_as)
            self.menuBar.add_cascade(label="File", underline=0, menu=self.fileMenu)
            self.boardMenu = Menu(self.menuBar, tearoff=0)
            self.boardMenu.add_command(label="Empty Board", underline=6, command=self.canvas_draw, accelerator='Ctrl+E')
            self.bind('<Control-e>',self.canvas_draw)
            self.boardMenu.add_command(label="White Board", underline=6, command=self.white_board, accelerator='Ctrl+W')
            self.bind('<Control-w>',self.white_board)
            self.boardMenu.add_command(label="Random Letters", underline=0, command=self.random_board, accelerator='Ctrl+R')
            self.bind('<Control-r>',self.random_board)
            self.boardMenu.add_command(label="Random Colors", underline=7, command=self.random_colors, accelerator='Ctrl+C')
            self.bind('<Control-c>',self.random_colors)
            self.boardMenu.add_separator()
            self.boardMenu.add_command(label="Search", underline=0, command=self.do_search, accelerator='Enter')
            self.menuBar.add_cascade(label="Board", underline=0, menu=self.boardMenu)

            self.optionsMenu = Menu(self.menuBar, tearoff=0)
            self.optionsMenu.add_command(label="Play Against Concentrate", underline=0, command=self.play_against, accelerator='Tab')
            self.bind('<Tab>',self.play_against)
            self.optionsMenu.add_separator()

            self.themeMenu= Menu(self.optionsMenu, tearoff=0)
            self.themeMenu.add_radiobutton(label="Light", underline=0, variable=self.theme, value=0, command=lambda: self.change_theme('light'))
            self.themeMenu.add_radiobutton(label="Pop", underline=0, variable=self.theme, value=1, command=lambda: self.change_theme('pop'))
            self.themeMenu.add_radiobutton(label="Retro", underline=0, variable=self.theme, value=2, command=lambda: self.change_theme('retro'))
            self.themeMenu.add_radiobutton(label="Dark", underline=0, variable=self.theme, value=3, command=lambda: self.change_theme('dark'))
            self.themeMenu.add_radiobutton(label="Forest", underline=0, variable=self.theme, value=4, command=lambda: self.change_theme('forest'))
            self.themeMenu.add_radiobutton(label="Glow", underline=0, variable=self.theme, value=5, command=lambda: self.change_theme('glow'))
            self.themeMenu.add_radiobutton(label="Pink", underline=1, variable=self.theme, value=6, command=lambda: self.change_theme('pink'))
            self.themeMenu.add_radiobutton(label="Contrast", underline=0, variable=self.theme, value=7, command=lambda: self.change_theme('contrast'))
            self.optionsMenu.add_cascade(label="Theme", underline=0, menu=self.themeMenu)
            self.optionsMenu.add_separator()

            self.difficulty = StringVar()
            self.optionsMenu.add_radiobutton(label="Dunce", underline=0, variable=self.difficulty, value="R", command=self.change_difficulty, accelerator='Ctrl+1')
            self.bind('<Control-Key-1>', lambda x: self.change_difficulty('R'))
            self.optionsMenu.add_radiobutton(label="Easy", underline=0, variable=self.difficulty, value="E", command=self.change_difficulty, accelerator='Ctrl+2')
            self.bind('<Control-Key-2>', lambda x: self.change_difficulty('E'))
            self.optionsMenu.add_radiobutton(label="Medium", underline=0, variable=self.difficulty, value="M", command=self.change_difficulty, accelerator='Ctrl+3')
            self.bind('<Control-Key-3>', lambda x: self.change_difficulty('M'))
            self.optionsMenu.add_radiobutton(label="Hard", underline=0, variable=self.difficulty, value="H", command=self.change_difficulty, accelerator='Ctrl+4')
            self.bind('<Control-Key-4>', lambda x: self.change_difficulty('H'))
            self.optionsMenu.add_radiobutton(label="Extreme", underline=1, variable=self.difficulty, value="X", command=self.change_difficulty, accelerator='Ctrl+5')
            self.bind('<Control-Key-5>', lambda x: self.change_difficulty('X'))
            self.difficulty.set('H')
            self.optionsMenu.add_separator()
            self.optionsMenu.add_radiobutton(label="Blue to Play", variable=self.move, value=1, command=self.blue_turn)
            self.optionsMenu.add_radiobutton(label="Red to Play", variable=self.move, value=-1, command=self.red_turn)
            self.menuBar.add_cascade(label="Options", underline=0, menu=self.optionsMenu)

        self.bind('<Return>',self.do_search)

        # display the menu
        self.config(menu=self.menuBar)
        self.canvas_draw()
        self.boardColors = 'w'*25

        if self.themeName != '':
            self.change_theme(self.themeName)

        #restore from dct passed in
        if dct != dict():
            self.restore_from_dict(dct)

        self.notBusyWidgetCursors = dict() #for busy and notbusy
        self.board.focus_set()

    def change_theme(self, theme):
        self.save_board_colors()
        if theme == 'light':
            self.theme.set(0)
            self.defaultColor = '#%02x%02x%02x' % (240, 240, 240)  # different from iOS app
            self.blue= ('#%02x%02x%02x' % (120, 200, 245), '#%02x%02x%02x' % (0, 162, 255))
            self.red = ('#%02x%02x%02x' % (247, 153, 141), '#%02x%02x%02x' % (255, 67, 47))
            self.defaultText= '#%02x%02x%02x' % (46, 45, 45)
            self.blueText= ('#%02x%02x%02x' % (24, 40, 49), '#%02x%02x%02x' % (0, 32, 51))
            self.redText = ('#%02x%02x%02x' % (49, 30, 28), '#%02x%02x%02x' % (51, 13, 9))
            self.selectedBlue = ('#%02x%02x%02x' % (90, 190, 243), '#%02x%02x%02x' % (0, 139, 223))
            self.selectedRed = ('#%02x%02x%02x' % (249, 129, 112), '#%02x%02x%02x' % (255, 39, 15))
            self.selectedDefault = '#%02x%02x%02x' % (224, 224, 224)
        elif theme == 'dark':
            self.theme.set(3)
            self.defaultColor = '#%02x%02x%02x' % (57, 57, 57)
            self.blue= ('#%02x%02x%02x' % (24, 117, 152), '#%02x%02x%02x' % (0, 186, 255))
            self.red = ('#%02x%02x%02x' % (152, 58, 48), '#%02x%02x%02x' % (255, 67, 47))
            self.defaultText= '#%02x%02x%02x' % (215, 215, 215)
            self.blueText= ('#%02x%02x%02x' % (208, 227, 234), '#%02x%02x%02x' % (0, 37, 51))
            self.redText = ('#%02x%02x%02x' % (234, 215, 213), '#%02x%02x%02x' % (51, 13, 9))
            self.selectedBlue = ('#%02x%02x%02x' % (29, 138, 180), '#%02x%02x%02x' % (0, 162, 223))
            self.selectedRed = ('#%02x%02x%02x' % (176, 67, 55), '#%02x%02x%02x' % (255, 39, 15))
            self.selectedDefault = '#%02x%02x%02x' % (73, 73, 73)
        elif theme == 'contrast':
            self.theme.set(7)
            self.defaultColor = '#%02x%02x%02x' % (240, 240, 240)  # different from iOS app
            self.blue= ('#%02x%02x%02x' % (143, 255, 127), '#%02x%02x%02x' % (32, 255, 0))
            self.red = ('#%02x%02x%02x' % (127, 127, 127), '#%02x%02x%02x' % (0, 0, 0))
            self.defaultText= '#%02x%02x%02x' % (48, 48, 48)
            self.blueText= ('#%02x%02x%02x' % (28, 51, 25), '#%02x%02x%02x' % (6, 51, 0))
            self.redText = ('#%02x%02x%02x' % (25, 25, 25), '#%02x%02x%02x' % (204, 204, 204))
            self.selectedBlue = ('#%02x%02x%02x' % (116, 255, 96), '#%02x%02x%02x' % (28, 223, 0))
            self.selectedRed = ('#%02x%02x%02x' % (111, 111, 111), '#%02x%02x%02x' % (35, 35, 35))
            self.selectedDefault = '#%02x%02x%02x' % (228, 228, 228)
        elif theme == 'forest':
            self.theme.set(4)
            self.defaultColor = '#%02x%02x%02x' % (215, 221, 207)
            self.blue= ('#%02x%02x%02x' % (239, 193, 108), '#%02x%02x%02x' % (255, 156, 0))
            self.red = ('#%02x%02x%02x' % (122, 164, 137), '#%02x%02x%02x' % (21, 99, 59))
            self.defaultText= '#%02x%02x%02x' % (43, 44, 41)
            self.blueText= ('#%02x%02x%02x' % (47, 38, 21), '#%02x%02x%02x' % (51, 31, 0))
            self.redText = ('#%02x%02x%02x' % (24, 32, 27), '#%02x%02x%02x' % (208, 223, 215))
            self.selectedBlue = ('#%02x%02x%02x' % (236, 181, 79), '#%02x%02x%02x' % (223, 134, 0))
            self.selectedRed = ('#%02x%02x%02x' % (103, 152, 120), '#%02x%02x%02x' % (27, 124, 73))
            self.selectedDefault = '#%02x%02x%02x' % (199, 207, 108)
        elif theme == 'glow':
            self.theme.set(5)
            self.defaultColor = '#%02x%02x%02x' % (57, 57, 57)
            self.blue= ('#%02x%02x%02x' % (73, 152, 119), '#%02x%02x%02x' % (97, 255, 190))
            self.red = ('#%02x%02x%02x' % (141, 24, 77), '#%02x%02x%02x' % (234, 0, 105))
            self.defaultText= '#%02x%02x%02x' % (215, 215, 215)
            self.blueText= ('#%02x%02x%02x' % (14, 30, 23), '#%02x%02x%02x' % (19, 51, 38))
            self.redText = ('#%02x%02x%02x' % (232, 208, 219), '#%02x%02x%02x' % (46, 0, 21))
            self.selectedBlue = ('#%02x%02x%02x' % (63, 131, 102), '#%02x%02x%02x' % (45, 255, 171))
            self.selectedRed = ('#%02x%02x%02x' % (115, 19, 63), '#%02x%02x%02x' % (202, 0, 91))
            self.selectedDefault = '#%02x%02x%02x' % (73, 73, 73)
        elif theme == 'pink':
            self.theme.set(6)
            self.defaultColor = '#%02x%02x%02x' % (245, 215, 227)
            self.blue= ('#%02x%02x%02x' % (255, 112, 232), '#%02x%02x%02x' % (255, 0, 228))
            self.red = ('#%02x%02x%02x' % (171, 140, 142), '#%02x%02x%02x' % (87, 56, 47))
            self.defaultText= '#%02x%02x%02x' % (48, 43, 45)
            self.blueText= ('#%02x%02x%02x' % (51, 22, 46), '#%02x%02x%02x' % (51, 0, 45))
            self.redText = ('#%02x%02x%02x' % (34, 28, 28), '#%02x%02x%02x' % (221, 215, 213))
            self.selectedBlue = ('#%02x%02x%02x' % (255, 81, 228), '#%02x%02x%02x' % (223, 0, 201))
            self.selectedRed = ('#%02x%02x%02x' % (157, 121, 124), '#%02x%02x%02x' % (107, 69, 58))
            self.selectedDefault = '#%02x%02x%02x' % (238, 189, 208)
        elif theme == 'pop':
            self.theme.set(1)
            self.defaultColor = '#%02x%02x%02x' % (57, 57, 57)
            self.blue= ('#%02x%02x%02x' % (87, 152, 24), '#%02x%02x%02x' % (126, 255, 0))
            self.red = ('#%02x%02x%02x' % (152, 24, 123), '#%02x%02x%02x' % (255, 0, 198))
            self.defaultText= '#%02x%02x%02x' % (215, 215, 215)
            self.blueText= ('#%02x%02x%02x' % (221, 234, 208), '#%02x%02x%02x' % (25, 51, 0))
            self.redText = ('#%02x%02x%02x' % (234, 208, 228), '#%02x%02x%02x' % (51, 0, 39))
            self.selectedBlue = ('#%02x%02x%02x' % (104, 180, 29), '#%02x%02x%02x' % (112, 223, 0))
            self.selectedRed = ('#%02x%02x%02x' % (180, 29, 146), '#%02x%02x%02x' % (223, 0, 173))
            self.selectedDefault = '#%02x%02x%02x' % (73, 73, 73)
        elif theme == 'retro':
            self.theme.set(2)
            self.defaultColor = '#%02x%02x%02x' % (241, 226, 189)
            self.blue= ('#%02x%02x%02x' % (195, 136, 226), '#%02x%02x%02x' % (140, 37, 255))
            self.red = ('#%02x%02x%02x' % (244, 166, 133), '#%02x%02x%02x' % (237, 97, 70))
            self.defaultText= '#%02x%02x%02x' % (48, 45, 37)
            self.blueText= ('#%02x%02x%02x' % (39, 27, 45), '#%02x%02x%02x' % (232, 211, 255))
            self.redText = ('#%02x%02x%02x' % (48, 33, 26), '#%02x%02x%02x' % (47, 19, 14))
            self.selectedBlue = ('#%02x%02x%02x' % (182, 109, 220), '#%02x%02x%02x' % (157, 68, 255))
            self.selectedRed = ('#%02x%02x%02x' % (241, 145, 103), '#%02x%02x%02x' % (234, 69, 40))
            self.selectedDefault = '#%02x%02x%02x' % (235, 214, 163)
        self.history.tag_configure('red', foreground=self.red[1])
        self.history.tag_configure('blue', foreground=self.blue[1])
        self.restore_board_colors()
        self.themeName = theme

    def play_against(self,event=None):
        #get the board and history data
        boarddct = self.make_save_dict()
        ttl = self.title()
        thm = self.themeName
        #close me
        self.destroy()
        #call playGUI with data
        PlayGUI(dct=boarddct,file=self.file,title=ttl,themeName=thm).mainloop()

    def new(self,event=None):
        """closes any previously open file, erases board, history, search"""
        if self.file != '':
            self.file = ''
        self.title(self.titleText)
        self.canvas_draw()

    def restore_from_dict(self,dct):
        letters = dct['letters']
        for i,l in enumerate(letters):
            row = i//5
            col = i%5
            self.board.itemconfig(self.boardStuff[row][col][1],text=l)
        lst = dct['history']
        for id, word, score, board, letters, color in lst:
            self.history.insert('', 'end', iid=id, tag=color, values=(word, score, board, letters))
        selected = dct['selected']
        if len(lst) > 0: #there could be no history
            self.history.focus(selected)
            self.history.selection_set(selected)
            self.historySelection = selected
            self.history.see(selected)
        colors = dct['colors']
        self.update_board_colors(colors)

    def open(self,event=None):
        """presents file dialog box for selecting one file.  loads data to the board and history"""
        fn = filedialog.askopenfilename(filetypes=[('Concentrate Game Document', '.cgd')])
        if fn != '':
            self.canvas_draw()
            self.file = fn
            f = open(self.file,'rb')
            dct = pickle.load(f)
            f.close()
            self.restore_from_dict(dct)
            self.title(self.titleText+self.titleSeparator+path.basename(self.file))

    def make_save_dict(self):
        saveDict = dict()
        saveList = []
        for iid in self.history.get_children():
            word = self.history.set(iid,'Word')
            score = self.history.set(iid,'Score')
            board = self.history.set(iid,'Board')
            letters = self.history.set(iid,'Letters')
            if self.history.tag_has('blue', item=iid):
                saveList.append((iid,word,score,board,letters,'blue'))
            elif self.history.tag_has('red', item=iid):
                saveList.append((iid,word,score,board,letters,'red'))
            else:
                saveList.append((iid,word,score,board,letters,''))
        saveDict['history']=saveList
        self.letters = ''.join([self.board.itemcget(self.boardStuff[row][col][1], 'text') for row in range(5) for col in range(5)])
        saveDict['letters']=self.letters
        colors = ''.join(self.get_defended_color(row,col) for row in range(5) for col in range(5))
        saveDict['colors']=colors
        iid = self.history.focus()
        saveDict['selected']=iid
        return saveDict

    def file_name_check(self,fn):
        if fn.upper()[-4:] != '.CGD':
            fn += '.cgd'
        return fn

    def save(self,event=None):
        """loops over the history and saves to the current open file"""
        if self.file == '':
            fn = filedialog.asksaveasfilename(filetypes=[('Concentrate Game Document', '.cgd')])
            if fn != '': #pressed cancel on the dialog
                self.file = fn
                self.file = self.file_name_check(self.file)
                f = open(self.file,'wb')
                saveDict = self.make_save_dict()
                pickle.dump(saveDict,f)
                self.title(self.titleText+self.titleSeparator+path.basename(self.file))
                f.close()
                self.title(self.titleText+self.titleSeparator+path.basename(self.file))
        else:
            f = open(self.file,'wb')
            saveDict = self.make_save_dict()
            pickle.dump(saveDict,f)
            self.title(self.titleText+self.titleSeparator+path.basename(self.file))
            f.close()

    def save_as(self,event=None):
        """loops over the history and presents the file save dialog box"""
        fn = filedialog.asksaveasfilename(filetypes=[('Concentrate Game Document', '.cgd')])
        if fn != '':
            self.file = fn
            self.file = self.file_name_check(self.file)
            self.save()
            self.title(self.titleText+self.titleSeparator+path.basename(self.file))

    def blue_turn(self,event=None):
        self.move.set(1)

    def red_turn(self,event=None):
        self.move.set(-1)

    def white_board(self, event=None):
         self.update_board_colors('w'*25)

    def change_difficulty(self, d=''):
        if d != '':
            self.difficulty.set(d)
        self.clear_search()
        if self.difficulty.get() == 'R':
            self.player.changedifficulty(['R', 5, 8, 'R'])
        elif self.difficulty.get() == 'E':
            self.player.changedifficulty(['R', 5, 5, 'S'])
        elif self.difficulty.get() == 'M':
            self.player.changedifficulty(['R', 5, 8, 'S'])
        elif self.difficulty.get() == 'H':
            self.player.changedifficulty(['R', 5, 25, 'S'])
        else:
            self.player.changedifficulty(['A', 5, 25, 'S'])

    def canvas_draw(self, event=None):
        self.clear_search()
        self.clear_history()
        self.board = Canvas(self.topFrame, width=self.boardSize, height=self.boardSize, borderwidth=0, highlightthickness=1, bg='white')
        self.board.grid(row=1,column=0,rowspan=2)
        self.move.set(1)

        self.board.bind('<Button-1>',self.change_color)
        self.board.bind('<Key>',self.nex)  # to write that character to the square and select the next one

        if self.sys != 'aqua':  # these special key bindings are handled on the mac by the key binding above, self.nex
            self.board.bind('<Up>',self.move_up)
            self.board.bind('<Down>',self.move_down)
            self.board.bind('<Left>',self.move_left)
            self.board.bind('<Right>',self.move_right)
            self.board.bind('<BackSpace>',self.backspace)
            self.board.bind('<Delete>',self.delete)

        for row in range(5):
            for col in range(5):
                top = row * self.squareSize + 1
                left = col * self.squareSize + 1
                bottom = row * self.squareSize + self.squareSize
                right = col * self.squareSize + self.squareSize
                rect = self.board.create_rectangle(left,top,right,bottom,outline='gray',fill=self.defaultColor)
                text = self.board.create_text(left+self.squareSize/2, top+self.squareSize/2,text=' ',font='Helvetica 20',fill=self.defaultText)
                self.boardStuff[row][col] = (rect,text)
        self.board.focus_set()
        self.select_square(0,0)

    def random_board(self, event=None):
        go = True
        if len(self.history.get_children()) > 0:
            if messagebox.askyesno('Are you sure?','Editing the letters on the board will clear the history and search box.  Proceed?'):
                self.clear_history()
                self.clear_search()
                if self.title()[-1] != '*' and self.file != '':
                    self.title(self.title()+'*')
            else:
                go = False
        if go:
            letters = arena.genletters()
            for x,c in enumerate(letters):
                row = x // 5
                col = x % 5
                self.board.itemconfig(self.boardStuff[row][col][1],text=c)
            self.board.focus_set()

    def random_colors(self, event=None):
        self.white_board()
        colors = [choice(['','blue','red']) for x in range(25)]
        for x,c in enumerate(colors):
            self.update_colors(x//5,x%5,c)
        self.board.focus_set()
        #print(self.board.focus_get().winfo_class())

    def move_up(self,event):  #these methods work on windows, mac is handled by self.nex
        (row, col) = self.selected
        nextNum = ((row-1)*5 + col) % 25
        nextRow = nextNum // 5
        nextCol = nextNum % 5
        self.select_square(nextRow, nextCol)

    def move_down(self,event):
        (row, col) = self.selected
        nextNum = ((row+1)*5 + col) % 25
        nextRow = nextNum // 5
        nextCol = nextNum % 5
        self.select_square(nextRow, nextCol)

    def move_left(self,event):
        (row, col) = self.selected
        nextNum = (row*5 + col - 1) % 25
        nextRow = nextNum // 5
        nextCol = nextNum % 5
        self.select_square(nextRow, nextCol)

    def move_right(self,event):
        (row, col) = self.selected
        nextNum = (row*5 + col + 1) % 25
        nextRow = nextNum // 5
        nextCol = nextNum % 5
        self.select_square(nextRow, nextCol)

    def backspace(self,event):
        (row, col) = self.selected
        nextNum = (row*5 + col - 1) % 25
        nextRow = nextNum // 5
        nextCol = nextNum % 5
        self.select_square(nextRow, nextCol)
        self.board.itemconfig(self.boardStuff[nextRow][nextCol][1],text='')

    def delete(self,event):
        (row, col) = self.selected
        self.board.itemconfig(self.boardStuff[row][col][1],text='')

    def nex(self,event):
        (row, col) = self.selected
        self.board.focus_set()
        self.board.focus()
        if self.sys == 'aqua':
            noModifier = {0}
        else:
            noModifier = {8,9,10} #8 is none, 9 is shift, 10 is capslock
        char = event.char.upper()
        if char in ascii_uppercase and len(char) > 0 and event.state in noModifier: #len is used to avoid moving forward with Control/Command buttons alone
                                                                                    #event.state is used to avoid doing the same for Command-key on the mac
            go = True
            if len(self.history.get_children()) > 0:
                if messagebox.askyesno('Are you sure?','Editing the letters on the board will clear the history and search box.  Do you want to proceed?'):
                    self.clear_history()
                    self.clear_search()
                    if self.title()[-1] != '*' and self.file != '':
                        self.title(self.title()+'*')
                else:
                    go = False
            if go:
                self.board.itemconfig(self.boardStuff[row][col][1],text=char)
                nextNum = (row*5 + col + 1) % 25
                nextRow = nextNum // 5
                nextCol = nextNum % 5
                self.select_square(nextRow, nextCol)
        elif len(char) > 0:  # works on the mac, not on windows
            keyNum = ord(event.char)
            if keyNum == 63232:  # up
                nextNum = ((row-1)*5 + col) % 25
                nextRow = nextNum // 5
                nextCol = nextNum % 5
                self.select_square(nextRow, nextCol)
            elif keyNum == 63233:  # down
                nextNum = ((row+1)*5 + col) % 25
                nextRow = nextNum // 5
                nextCol = nextNum % 5
                self.select_square(nextRow, nextCol)
            elif keyNum == 63234:  # left
                nextNum = (row*5 + col - 1) % 25
                nextRow = nextNum // 5
                nextCol = nextNum % 5
                self.select_square(nextRow, nextCol)
            elif keyNum == 63235:  # right
                nextNum = (row*5 + col + 1) % 25
                nextRow = nextNum // 5
                nextCol = nextNum % 5
                self.select_square(nextRow, nextCol)
            elif keyNum == 127:  # backspace
                nextNum = (row*5 + col - 1) % 25
                nextRow = nextNum // 5
                nextCol = nextNum % 5
                self.select_square(nextRow, nextCol)
                self.board.itemconfig(self.boardStuff[nextRow][nextCol][1],text='')
            elif keyNum == 63272:  # delete
                self.board.itemconfig(self.boardStuff[row][col][1],text='')
        #print(self.board.focus_get().winfo_class())

    def get_row_col(self, x, y):
        col = x//self.squareSize
        row = y//self.squareSize
        return (row, col)

    def get_color(self, row, col):
        color = self.board.itemcget(self.boardStuff[row][col][0],'fill')
        if color in self.blue:
            return 'B'
        elif color in self.red:
            return 'R'
        else:
            return 'W'

    def get_defended_color(self, row, col):
        color = self.board.itemcget(self.boardStuff[row][col][0],'fill')
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

    def check_defended(self, row, col):
        nColors = set()
        if row in range(5) and col in range(5):
            myColor = self.get_color(row, col)
            nColors.add(myColor)
            nRow, nCol = row, col-1
            if nRow in range(5) and nCol in range(5):
                nColors.add(self.get_color(nRow, nCol))
            nRow, nCol = row-1, col
            if nRow in range(5) and nCol in range(5):
                nColors.add(self.get_color(nRow, nCol))
            nRow, nCol = row, col+1
            if nRow in range(5) and nCol in range(5):
                nColors.add(self.get_color(nRow, nCol))
            nRow, nCol = row+1, col
            if nRow in range(5) and nCol in range(5):
                nColors.add(self.get_color(nRow, nCol))
            if 'B' not in nColors and 'W' not in nColors:
                self.board.itemconfig(self.boardStuff[row][col][0], fill=self.red[1])
                self.board.itemconfig(self.boardStuff[row][col][1], fill=self.redText[1])
            elif 'R' not in nColors and 'W' not in nColors:
                self.board.itemconfig(self.boardStuff[row][col][0], fill=self.blue[1])
                self.board.itemconfig(self.boardStuff[row][col][1], fill=self.blueText[1])
            else:
                if myColor == 'B':
                    self.board.itemconfig(self.boardStuff[row][col][0], fill=self.blue[0])
                    self.board.itemconfig(self.boardStuff[row][col][1], fill=self.blueText[0])
                elif myColor == 'R':
                    self.board.itemconfig(self.boardStuff[row][col][0], fill=self.red[0])
                    self.board.itemconfig(self.boardStuff[row][col][1], fill=self.redText[0])

    def update_colors(self, row, col, color):
        if color == 'blue':
            self.board.itemconfig(self.boardStuff[row][col][0], fill=self.blue[0])
            self.board.itemconfig(self.boardStuff[row][col][1], fill=self.blueText[0])
        elif color == 'red':
            self.board.itemconfig(self.boardStuff[row][col][0], fill=self.red[0])
            self.board.itemconfig(self.boardStuff[row][col][1], fill=self.redText[0])
        else:
            self.board.itemconfig(self.boardStuff[row][col][0], fill=self.defaultColor)
            self.board.itemconfig(self.boardStuff[row][col][1], fill=self.defaultText)

        #check if I am defended
        self.check_defended(row,col)
        #check if neighbors are defended
        self.check_defended(row,col-1)
        self.check_defended(row-1,col)
        self.check_defended(row,col+1)
        self.check_defended(row+1,col)

    def change_color(self,event):
        self.board.focus_set()
        (row, col) = self.get_row_col(event.x, event.y)
        self.select_square(row,col)
        color = self.board.itemcget(self.boardStuff[row][col][0], 'fill')
        if color == self.defaultColor:
            self.update_colors(row,col,'blue')
        elif color in self.blue:
            self.update_colors(row,col,'red')
        elif color in self.red:
            self.update_colors(row,col,'')

    def select_square(self,selectRow, selectCol):
        self.selected = (selectRow,selectCol)
        for row in range(5):
            for col in range(5):
                self.board.itemconfig(self.boardStuff[row][col][0], outline='gray')
        self.board.itemconfig(self.boardStuff[selectRow][selectCol][0], outline='black')

    def busy(self, widget=None):
        if widget is None:
            w = self
        else:
            w = widget
        if not str(w) in self.notBusyWidgetCursors:
            try:
                # attach cursor to this widget
                cursor = w.cget("cursor")
                if cursor != "watch":
                    self.notBusyWidgetCursors[str(w)] = (w, cursor)
                    w.config(cursor="watch")
            except TclError:
                pass

        for w in w.children.values():
            self.busy(w)

    def not_busy(self):
        for w, cursor in self.notBusyWidgetCursors.values():
            try:
                w.config(cursor=cursor)
            except TclError:
                pass
        self.notBusyWidgetCursors = dict()

    def clear_history(self):
        for iid in self.history.get_children():
            self.history.delete(iid)
        self.historySelection=-1

    def clear_search(self):
        for iid in self.suggest.get_children():
            self.suggest.delete(iid)

    def is_square_selected(self, row, col):
        selectedColors = tuple(self.selectedDefault) + self.selectedBlue + self.selectedRed
        color = self.board.itemcget(self.boardStuff[row][col][1],'fill')
        return (color in selectedColors)

    def save_board_colors(self):
        """saves the state of the board colors for later retrieval"""
        board = ''
        selected = ''
        for row in range(5):
            for col in range(5):
                board += self.get_defended_color(row,col)
                if self.is_square_selected(row, col):
                    selected += 'Y'
                else:
                    selected += 'N'
        self.boardSelected = selected
        self.boardColors = board

    def restore_board_colors(self):
        """restores the state of the board saved by save_board_colors"""
        self.update_board_colors(self.boardColors, self.boardSelected)

    def update_board_colors(self, newBoard, selected='N'*25):
        """changes the colors of the board"""
        newBoard = newBoard.replace(' ','')
        for row in range(5):
            for col in range(5):
                i = row*5+col
                l = newBoard[i]
                s = selected[i] == 'Y'
                bgColor = self.defaultColor
                if s:
                    txtColor = self.selectedDefault
                else:
                    txtColor = self.defaultText
                if l == 'b':
                    bgColor = self.blue[0]
                    if s:
                        txtColor = self.selectedBlue[0]
                    else:
                        txtColor = self.blueText[0]
                elif l == 'B':
                    bgColor = self.blue[1]
                    if s:
                        txtColor = self.selectedBlue[1]
                    else:
                        txtColor = self.blueText[1]
                elif l == 'r':
                    bgColor = self.red[0]
                    if s:
                        txtColor = self.selectedRed[0]
                    else:
                        txtColor = self.redText[0]
                elif l == 'R':
                    bgColor = self.red[1]
                    if s:
                        txtColor = self.selectedRed[1]
                    else:
                        txtColor = self.redText[1]
                self.board.itemconfig(self.boardStuff[row][col][0],fill=bgColor)
                self.board.itemconfig(self.boardStuff[row][col][1],fill=txtColor)

    def history_click(self, event):
        """bound to history.<<TreeviewSelect>>"""

        if not self.historyIgnore:
            #get item id clicked on
            clickedIID = self.history.focus()
            self.historySelection = clickedIID
            txt = self.history.set(clickedIID,'Word')
            board = self.history.set(clickedIID,'Board')
            #update colors on the board to match the board of the word suggested
            self.update_board_colors(board)
            self.history.focus_set()
            #unselect suggest selection, if any
            suggestSelect = self.suggest.focus()
            self.suggestIgnore = True
            self.suggest.selection_remove(suggestSelect)
            self.btnSuggestSelect.state(['disabled'])
            self.suggestSelection = -1
            #set whose turn it is based on the selection
            if self.history.tag_has('red',clickedIID):
                self.move.set(1)
            elif self.history.tag_has('blue',clickedIID):
                self.move.set(-1)
            else:
                #untagged first id, look at next id
                nextid = self.history.next(clickedIID)
                if self.history.tag_has('red',nextid):
                    self.move.set(-1)
                else:
                    self.move.set(1)

        else:
            self.historyIgnore = False

    def suggest_click(self, event):
        """tied to suggest.<<TreeviewSelect>>"""
        if not self.suggestIgnore:
            #columns=('Word', 'Score','Board')
            #get item id clicked on
            clickedIID = self.suggest.focus()
            if self.suggestSelection != clickedIID:
                self.suggestSelection = clickedIID
                txt = self.suggest.set(clickedIID,'Word')
                board = self.suggest.set(clickedIID,'Board')
                if txt != self.noText:
                    if txt == self.moreText:
                        #delete the last entry (click for more...)
                        last = ''
                        #get number of words in suggest
                        amt = 0
                        for iid in self.suggest.get_children():
                            last = iid
                            amt += 1
                        self.suggest.delete(last)
                        #call do search with lastdisplayed
                        self.do_search(lastDisplayed=amt-1)

                    else:
                        #update colors on the board to match the board of the word suggested
                        self.update_board_colors(board)
                        self.btnSuggestSelect.state(['!disabled'])
                        #remove selection from history
            else:
                self.suggestIgnore = True
                self.suggest.selection_remove(clickedIID)
                self.btnSuggestSelect.state(['disabled'])
                self.suggestSelection = -1
                self.restore_board_colors()
        else:
            self.suggestIgnore = False

    def suggest_select(self):
        item = self.suggest.focus()
        #print ("you selected", self.suggest.set(item,'Word'))
        #clear history past the current selection
        txt = ''
        if self.historySelection != -1:
            txt = self.history.set(self.historySelection,'Word')
            toDelete = []
            if txt == self.initialHist:
                toDelete.append(self.historySelection)
            iid = self.history.next(self.historySelection)
            while iid != '':
                toDelete.append(iid)
                iid = self.history.next(iid)
            for iid in toDelete:
                self.history.delete(iid)
        #check if the history treeview is empty
        cnt = len(self.history.get_children())
        if cnt == 0:
            self.history.insert('','end',values=(self.initialHist,'' ,self.boardColors,self.letters))
        #copy the word, board, and score to the end of the history treeview
        txt = self.suggest.set(item,'Word')
        score = self.suggest.set(item,'Score')
        board = self.suggest.set(item,'Board')
        #print('saving move:',txt,score,board)
        if self.move.get() == 1:
            insertID = self.history.insert('', 'end', tag='blue', values=(txt, score, board, self.letters))
        else:
            insertID = self.history.insert('', 'end', tag='red', values=(txt, score, board, self.letters))
        #select the inserted item in history
        self.historyIgnore=True
        self.history.selection_set(insertID)
        self.history.focus(insertID)
        self.historySelection = insertID
        self.history.see(insertID)
        #change whose turn it is
        self.move.set(-self.move.get())
        self.clear_search()
        self.need.delete(0,len(self.need.get()))
        if self.title()[-1] != '*' and self.file != '':
            self.title(self.title()+'*')
        self.btnSuggestSelect.state(['disabled'])

    def do_search(self, event=None, lastDisplayed=-1):
        self.busy()
        self.save_board_colors()  # to restore back to when the user un-selects a word
        if lastDisplayed == -1:
            self.clear_search()
        self.letters = ''.join([self.board.itemcget(self.boardStuff[row][col][1], 'text') for row in range(5) for col in range(5)])
        if not(all([x in ascii_uppercase for x in self.letters]) and len(self.letters) == 25):
            self.not_busy()
            messagebox.showwarning("Concentrate","The board must be completely filled with letters.")
            return
        score = ''.join(self.get_color(row,col) for row in range(5) for col in range(5))
        if 'W' not in score:
            self.not_busy()
            messagebox.showwarning("Concentrate","Game Over.")
            return
        #make the engine aware of which words are in the history
        words = list()
        for iid in self.history.get_children():
            txt = self.history.set(iid,'Word')
            if txt != self.initialHist:
                words.append(txt)
            if iid == self.historySelection:
                break
        needLetters = self.need.get().upper()
        self.player.possible(self.letters)
        self.player.resetplayed(self.letters, words)
        wordList, more = self.player.search(self.letters, score, needLetters, self.move.get(), lastDisplayed)
        for i, word in enumerate(wordList):
            if word[1][0] not in ascii_uppercase:
                self.suggest.insert('', 'end', tag=word[1][0], values=(word[1][1:], word[0], word[2]))
            else:
                self.suggest.insert('', 'end',values=(word[1], word[0], word[2]))
        if more:
            self.suggest.insert('', 'end', values=(self.moreText,))
        elif len(self.suggest.get_children()) == 0:
            self.suggest.insert('', 'end', values=(self.noText,))
        if lastDisplayed == -1:
            self.suggest.see(self.suggest.get_children()[0])
        self.not_busy()


class AnalysisPlayer(player0):
    def __init__(self, difficulty=['R', 5, 25, 'S']):
        player0.__init__(self, difficulty)

    def search(self, allLetters, score, needLetters, move, lastDisplayed):
        """returns a list for the GUI to display"""
        if lastDisplayed == -1:
            start = time()
            self.wordScores = self.decide(allLetters, score, needLetters, move)
            if self.difficulty[3] == 'S':
                if move == 1:
                    self.wordScores.sort(reverse=True)
                else:
                    self.wordScores.sort()
            else:
                self.displayed = list()
            decideTime = time() - start
            plays = len(self.wordScores)
            rate = int(plays/decideTime)
            #print(round(decideTime,2), 'seconds to decide', allLetters, score)
            #print(plays, 'plays found,', rate, 'per second')
        start = time()
        results = list()
        amountToDisplay = 200
        displayed = 0
        if self.difficulty[3] == 'S':
            for wordNum, (score, word, groupSize, blue, red, blueDef, redDef) in enumerate(self.wordScores):
                if wordNum > lastDisplayed and displayed < amountToDisplay:
                    zeroLetters,endingSoon, losing, newScore = self.endgamecheck(allLetters, blue, red, blueDef, redDef, move)
                    if losing:  # endgame check found a way for opponent to win
                        results.append((score, '-'+word, self.displayscore(blue, red, blueDef, redDef)))
                        displayed += 1
                    elif endingSoon:  # endgame check only found way for opponent to end game, but not win
                        results.append((score, '*'+word, self.displayscore(blue, red, blueDef, redDef)))
                        displayed += 1
                    else:
                        results.append((score, word, self.displayscore(blue, red, blueDef, redDef)))
                        displayed += 1
                elif displayed >= amountToDisplay:
                    #print(round(time()-start,2),'seconds to endgame check')
                    return results, True
            #print(round(time()-start,2),'seconds to endgame check')
            return results, False
        else:
            notDisplayed = [x for x in range(len(self.wordScores)) if x not in self.displayed]
            if len(notDisplayed) > amountToDisplay:
                lst = sample(notDisplayed, amountToDisplay)
                for i in lst:
                    (score, word, groupSize, blue, red, blueDef, redDef) = self.wordScores[i]
                    results.append((score, word, self.displayscore(blue, red, blueDef, redDef)))
                self.displayed += lst
                return results, True
            else:
                lst = notDisplayed
                for i in lst:
                    (score, word, groupSize, blue, red, blueDef, redDef) = self.wordScores[i]
                    results.append((score, word, self.displayscore(blue, red, blueDef, redDef)))
                self.displayed += lst
                return results, False




class PlayGUI(AnalysisGUI):

    def __init__(self, *args, **kwargs):
        Tk.__init__(self)

        #not working correctly TODO
##        img = PhotoImage('concentrate2.gif')
##        self.tk.call('wm', 'iconphoto', self._w, img)

        dct = kwargs.get('dct',dict())

        self.file = kwargs.get('file','')
        title = kwargs.get('title','')
        self.themeName = kwargs.get('themeName','')

        self.boardStuff = [[None for x in range(5)] for y in range(5)]  #holds rectangles and text on the board
        self.boardSize = 250
        self.squareSize = self.boardSize//5

        self.initialHist= '[Initial Position]'
        self.titleText = 'Concentrate'
        self.titleSeparator = ' - '

        #default theme is 'light'
        self.defaultColor = '#%02x%02x%02x' % (240, 240, 240)  # different from iOS app
        self.blue= ('#%02x%02x%02x' % (120, 200, 245), '#%02x%02x%02x' % (0, 162, 255))
        self.red = ('#%02x%02x%02x' % (247, 153, 141), '#%02x%02x%02x' % (255, 67, 47))
        self.defaultText= '#%02x%02x%02x' % (46, 45, 45)
        self.blueText= ('#%02x%02x%02x' % (24, 40, 49), '#%02x%02x%02x' % (0, 32, 51))
        self.redText = ('#%02x%02x%02x' % (49, 30, 28), '#%02x%02x%02x' % (51, 13, 9))
        #self.selectedBlue = ('SkyBlue2','RoyalBlue3')
        #self.selectedRed = ('IndianRed2','IndianRed3')
        self.selectedBlue = ('#%02x%02x%02x' % (90, 190, 243), '#%02x%02x%02x' % (0, 139, 223))
        self.selectedRed = ('#%02x%02x%02x' % (249, 129, 112), '#%02x%02x%02x' % (255, 39, 15))
        self.selectedDefault = '#%02x%02x%02x' % (224, 224, 224)

        if title == '':
            self.title(self.titleText)
        else:
            self.title(title)
        #self.columnconfigure(0, weight=1)
        #self.rowconfigure(0, weight=0)

        self.resizable(0,0)

        self.topFrame = ttk.Frame(self)
        self.topFrame.grid(row=0,column=0)

        #self.master = master
        #frame = Frame(self)
        #frame.grid(column=0, row=0, sticky=(N, S, E, W))
        self.topFrame.columnconfigure(0, weight=0)
        self.topFrame.columnconfigure(1, weight=0)
        self.topFrame.columnconfigure(2, weight=0)
        self.topFrame.columnconfigure(3, weight=0) #scroll bar
        self.topFrame.rowconfigure(0, weight=0)
        self.topFrame.rowconfigure(1, weight=1)
        self.topFrame.rowconfigure(2, weight=0)

        ttk.Label(self.topFrame, text='Board').grid(column=0,row=0)
        ttk.Label(self.topFrame, text='History').grid(column=1,row=0,columnspan=2)

        self.history = ttk.Treeview(self.topFrame,columns=('Word','Score','Board','Letters'), displaycolumns=('Word','Score'),selectmode='browse',show='tree')
        historyScroll = ttk.Scrollbar(self.topFrame,orient=VERTICAL,command=self.history.yview)
        historyScroll.grid(row=1,column=3,sticky=(N,S,E))
        self.history['yscrollcommand'] = historyScroll.set
        self.history.grid(row=1,column=1,columnspan=2,sticky=(N,S,W,E))
        self.history.column('#0',width=1)
        self.history.column(0,width=150)
        self.history.column(1,width=75)
        self.history.bind('<<TreeviewSelect>>',self.history_click)
        self.history.tag_configure('red', foreground=self.red[1])
        self.history.tag_configure('blue', foreground=self.blue[1])
        self.historySelection = -1
        self.historyIgnore= False

        self.sys = self.tk.call('tk', 'windowingsystem') # will return x11, win32 or aqua
        self.canvas_draw()

        self.play = ttk.Label(self.topFrame,text='',font='Helvetica 11')
        self.play.grid(row=2,column=0)
        self.play.bind('<1>',self.clear_play)

        self.btnPlay = ttk.Button(self.topFrame, text='Play', command=self.play_word)
        self.btnPlay.grid(row=2,column=1)
        self.btnPlay.state(['disabled'])

        btnPass = ttk.Button(self.topFrame, text='Pass', command=self.pass_turn)
        btnPass.grid(row=2,column=2)

        self.player = AnalysisPlayer()
        self.refPlayer = AnalysisPlayer(difficulty=['A',5,25])

        self.menuBar = Menu(self, tearoff=0)

        self.theme = IntVar()
        self.theme.set(0)

        if self.sys == 'aqua': #mac os x
            self.fileMenu= Menu(self.menuBar, tearoff=0)
            self.fileMenu.add_command(label="New", underline=0, command=self.new, accelerator='Command-N')
            self.bind('<Command-n>',self.new)
            self.fileMenu.add_command(label="Open...", underline=0, command=self.open, accelerator='Command-O')
            self.bind('<Command-o>',self.open)
            self.fileMenu.add_command(label="Save",underline=0, command=self.save, accelerator='Command-S')
            self.bind('<Command-s>',self.save)
            self.fileMenu.add_command(label="Save As...", underline=5, command=self.save_as, accelerator='Command+A')
            self.bind('<Command-a>',self.save_as)
            self.menuBar.add_cascade(label="Concentrate", underline=0, menu=self.fileMenu)

            self.optionsMenu = Menu(self.menuBar, tearoff=0)
            self.optionsMenu.add_command(label="Analyze Game", underline=0, command=self.analyze, accelerator='Tab')
            self.bind('<Tab>',self.analyze)
            self.optionsMenu.add_separator()

            self.themeMenu= Menu(self.optionsMenu, tearoff=0)
            self.themeMenu.add_radiobutton(label="Light", underline=0, variable=self.theme, value=0, command=lambda: self.change_theme('light'))
            self.themeMenu.add_radiobutton(label="Pop", underline=0, variable=self.theme, value=1, command=lambda: self.change_theme('pop'))
            self.themeMenu.add_radiobutton(label="Retro", underline=0, variable=self.theme, value=2, command=lambda: self.change_theme('retro'))
            self.themeMenu.add_radiobutton(label="Dark", underline=0, variable=self.theme, value=3, command=lambda: self.change_theme('dark'))
            self.themeMenu.add_radiobutton(label="Forest", underline=0, variable=self.theme, value=4, command=lambda: self.change_theme('forest'))
            self.themeMenu.add_radiobutton(label="Glow", underline=0, variable=self.theme, value=5, command=lambda: self.change_theme('glow'))
            self.themeMenu.add_radiobutton(label="Pink", underline=1, variable=self.theme, value=6, command=lambda: self.change_theme('pink'))
            self.themeMenu.add_radiobutton(label="Contrast", underline=0, variable=self.theme, value=7, command=lambda: self.change_theme('contrast'))
            self.optionsMenu.add_cascade(label="Theme", underline=0, menu=self.themeMenu)
            self.optionsMenu.add_separator()

            self.difficulty = StringVar()
            self.optionsMenu.add_radiobutton(label="Dunce", underline=0, variable=self.difficulty, value = "R", command=self.change_difficulty, accelerator='Command-1')
            self.bind('<Command-Key-1>', lambda x: self.change_difficulty('R'))
            self.optionsMenu.add_radiobutton(label="Easy", underline=0, variable=self.difficulty, value = "E", command=self.change_difficulty, accelerator='Command-2')
            self.bind('<Command-Key-2>', lambda x: self.change_difficulty('E'))
            self.optionsMenu.add_radiobutton(label="Medium", underline=0, variable=self.difficulty, value = "M", command=self.change_difficulty, accelerator='Command-3')
            self.bind('<Command-Key-3>', lambda x: self.change_difficulty('M'))
            self.optionsMenu.add_radiobutton(label="Hard", underline=0, variable=self.difficulty, value = "H", command=self.change_difficulty, accelerator='Command-4')
            self.bind('<Command-Key-4>', lambda x: self.change_difficulty('H'))
            self.optionsMenu.add_radiobutton(label="Extreme", underline=1, variable=self.difficulty, value = "X", command=self.change_difficulty, accelerator='Command-5')
            self.bind('<Command-Key-5>', lambda x: self.change_difficulty('X'))
            self.difficulty.set('H')
            self.menuBar.add_cascade(label="Options", menu=self.optionsMenu)

        else: #windows
            self.fileMenu= Menu(self.menuBar, tearoff=0)
            self.fileMenu.add_command(label="New", underline=0, command=self.new, accelerator='Ctrl+N')
            self.bind('<Control-n>',self.new)
            self.fileMenu.add_command(label="Open...", underline=0, command=self.open, accelerator='Ctrl+O')
            self.bind('<Control-o>',self.open)
            self.fileMenu.add_command(label="Save",underline=0, command=self.save, accelerator='Ctrl+S')
            self.bind('<Control-s>',self.save)
            self.fileMenu.add_command(label="Save As...", underline=5, command=self.save_as, accelerator='Ctrl+A')
            self.bind('<Control-a>',self.save_as)
            self.menuBar.add_cascade(label="File", underline=0, menu=self.fileMenu)

            self.optionsMenu = Menu(self.menuBar, tearoff=0)
            self.optionsMenu.add_command(label="Analyze Game", underline=0, command=self.analyze, accelerator='Tab')
            self.bind('<Tab>',self.analyze)
            self.optionsMenu.add_separator()
            self.themeMenu= Menu(self.optionsMenu, tearoff=0)
            self.themeMenu.add_radiobutton(label="Light", underline=0, variable=self.theme, value=0, command=lambda: self.change_theme('light'))
            self.themeMenu.add_radiobutton(label="Pop", underline=0, variable=self.theme, value=1, command=lambda: self.change_theme('pop'))
            self.themeMenu.add_radiobutton(label="Retro", underline=0, variable=self.theme, value=2, command=lambda: self.change_theme('retro'))
            self.themeMenu.add_radiobutton(label="Dark", underline=0, variable=self.theme, value=3, command=lambda: self.change_theme('dark'))
            self.themeMenu.add_radiobutton(label="Forest", underline=0, variable=self.theme, value=4, command=lambda: self.change_theme('forest'))
            self.themeMenu.add_radiobutton(label="Glow", underline=0, variable=self.theme, value=5, command=lambda: self.change_theme('glow'))
            self.themeMenu.add_radiobutton(label="Pink", underline=1, variable=self.theme, value=6, command=lambda: self.change_theme('pink'))
            self.themeMenu.add_radiobutton(label="Contrast", underline=0, variable=self.theme, value=7, command=lambda: self.change_theme('contrast'))
            self.optionsMenu.add_cascade(label="Theme", underline=0, menu=self.themeMenu)
            self.optionsMenu.add_separator()
            self.difficulty = StringVar()
            self.optionsMenu.add_radiobutton(label="Dunce", underline=0, variable=self.difficulty, value = "R", command=self.change_difficulty, accelerator='Ctrl+1')
            self.bind('<Control-Key-1>', lambda x: self.change_difficulty('R'))
            self.optionsMenu.add_radiobutton(label="Easy", underline=0, variable=self.difficulty, value = "E", command=self.change_difficulty, accelerator='Ctrl+2')
            self.bind('<Control-Key-2>', lambda x: self.change_difficulty('E'))
            self.optionsMenu.add_radiobutton(label="Medium", underline=0, variable=self.difficulty, value = "M", command=self.change_difficulty, accelerator='Ctrl+3')
            self.bind('<Control-Key-3>', lambda x: self.change_difficulty('M'))
            self.optionsMenu.add_radiobutton(label="Hard", underline=0, variable=self.difficulty, value = "H", command=self.change_difficulty, accelerator='Ctrl+4')
            self.bind('<Control-Key-4>', lambda x: self.change_difficulty('H'))
            self.optionsMenu.add_radiobutton(label="Extreme", underline=1, variable=self.difficulty, value = "X", command=self.change_difficulty, accelerator='Ctrl+5')
            self.bind('<Control-Key-5>', lambda x: self.change_difficulty('X'))
            self.difficulty.set('H')
            self.menuBar.add_cascade(label="Options", underline=0, menu=self.optionsMenu)

        # display the menu
        self.config(menu=self.menuBar)

        if self.themeName != '':
            self.change_theme(self.themeName)

        #random board or display passed in board
        if dct.get('letters','').strip() == '':
            self.random_board()
        else:
            self.restore_from_dict(dct)
        self.save_board_colors()

        #get valid plays
        self.make_word_set()

        self.notBusyWidgetCursors = dict() #for busy and notbusy
        self.board.focus_set()

    def analyze(self,event=None):
        #get the board and history data
        self.restore_board_colors()
        boardDict = self.make_save_dict()
        ttl = self.title()
        thm = self.themeName
        #close me
        self.destroy()
        #call analysisGUI with data
        AnalysisGUI(dct=boardDict, file=self.file, title=ttl, themeName=thm).mainloop()

    def new(self,event=None):
        """closes any previously open file, erases board, history"""
        if self.file != '':
            self.file = ''
        self.title(self.titleText)
        self.clear_play()
        self.canvas_draw()
        self.random_board()
        self.make_word_set()
        self.save_board_colors()

    def open(self,event=None):
        """presents file dialog box for selecting one file.  loads data to the board and history"""
        fn = filedialog.askopenfilename(filetypes=[('Concentrate Game Document', '.cgd')])
        if fn != '':
            self.canvas_draw()
            self.file = fn
            f = open(self.file,'rb')
            dct = pickle.load(f)
            f.close()
            self.restore_from_dict(dct)
            self.title(self.titleText+self.titleSeparator+path.basename(self.file))
            self.make_word_set()

    def canvas_draw(self, event=None):
        self.clear_history()
        self.board = Canvas(self.topFrame, width=self.boardSize, height=self.boardSize, borderwidth=0, highlightthickness=1, bg='white')
        self.board.grid(row=1,column=0)

        self.board.bind('<Button-1>',self.select_letter)

        for row in range(5):
            for col in range(5):
                top = row * self.squareSize + 1
                left = col * self.squareSize + 1
                bottom = row * self.squareSize + self.squareSize
                right = col * self.squareSize + self.squareSize
                rect = self.board.create_rectangle(left,top,right,bottom,outline='gray',fill=self.defaultColor)
                text = self.board.create_text(left+self.squareSize/2, top+self.squareSize/2,text='',font='Helvetica 20')
                self.boardStuff[row][col] = (rect, text)

    def make_word_set(self):
        self.letters = ''.join([self.board.itemcget(self.boardStuff[row][col][1], 'text') for row in range(5) for col in range(5)])
        self.wordSet = set(self.refPlayer.concentrate(self.letters))

    def check_defended(self, row, col):
        nColors = set()
        if row in range(5) and col in range(5):
            myColor = self.get_color(row, col)
            nColors.add(myColor)
            nRow, nCol = row, col-1
            if nRow in range(5) and nCol in range(5):
                nColors.add(self.get_color(nRow, nCol))
            nRow, nCol = row-1, col
            if nRow in range(5) and nCol in range(5):
                nColors.add(self.get_color(nRow, nCol))
            nRow, nCol = row, col+1
            if nRow in range(5) and nCol in range(5):
                nColors.add(self.get_color(nRow, nCol))
            nRow, nCol = row+1, col
            if nRow in range(5) and nCol in range(5):
                nColors.add(self.get_color(nRow, nCol))
            if 'B' not in nColors and 'W' not in nColors:
                self.board.itemconfig(self.boardStuff[row][col][0], fill=self.red[1])
                fgColor = self.board.itemcget(self.boardStuff[row][col][1], 'fill')
                if fgColor not in (tuple(self.defaultText) + self.blueText + self.redText):
                    self.board.itemconfig(self.boardStuff[row][col][0], fill=self.selectedRed[1])
            elif 'R' not in nColors and 'W' not in nColors:
                self.board.itemconfig(self.boardStuff[row][col][0], fill=self.blue[1])
                fgColor = self.board.itemcget(self.boardStuff[row][col][1], 'fill')
                if fgColor not in (tuple(self.defaultText) + self.blueText + self.redText):
                    self.board.itemconfig(self.boardStuff[row][col][1], fill=self.selectedBlue[1])
            else:
                if myColor == 'B':
                    self.board.itemconfig(self.boardStuff[row][col][0], fill=self.blue[0])
                    fgColor = self.board.itemcget(self.boardStuff[row][col][1], 'fill')
                    if fgColor not in (tuple(self.defaultText) + self.blueText + self.redText):
                        self.board.itemconfig(self.boardStuff[row][col][1], fill=self.selectedBlue[0])
                elif myColor == 'R':
                    self.board.itemconfig(self.boardStuff[row][col][0], fill=self.red[0])
                    fgColor = self.board.itemcget(self.boardStuff[row][col][1], 'fill')
                    if fgColor not in (tuple(self.defaultText) + self.blueText + self.redText):
                        self.board.itemconfig(self.boardStuff[row][col][1], fill=self.selectedRed[0])


    def update_colors(self, row, col, color):
        if color == 'blue':
            self.board.itemconfig(self.boardStuff[row][col][0], fill=self.blue[0])
        elif color == 'red':
            self.board.itemconfig(self.boardStuff[row][col][0], fill=self.red[0])
        else:
            self.board.itemconfig(self.boardStuff[row][col][0], fill='')
        #check if I am defended
        self.check_defended(row,col)
        #check if neighbors are defended
        self.check_defended(row,col-1)
        self.check_defended(row-1,col)
        self.check_defended(row,col+1)
        self.check_defended(row+1,col)


    def select_letter(self, event):
        self.board.focus_set()
        (row, col) = self.get_row_col(event.x, event.y)

        letter = self.board.itemcget(self.boardStuff[row][col][1], 'text')
        fgColor = self.board.itemcget(self.boardStuff[row][col][1], 'fill')
        bgColor = self.board.itemcget(self.boardStuff[row][col][0], 'fill')

        selectedColors = set(self.selectedBlue + self.selectedRed)
        selectedColors.add(self.selectedDefault)
        if fgColor not in selectedColors:
            i = row * 5 + col
            #if the square isn't defended by red
            c = self.boardColors[i]
            if c != 'R':
                self.update_colors(row, col, 'blue')
                bgColor = self.board.itemcget(self.boardStuff[row][col][0], 'fill')
            #make text color almost the same as its current background
            newColor = self.selectedDefault
            if bgColor in self.blue:
                i = self.blue.index(bgColor)
                newColor = self.selectedBlue[i]
            elif bgColor in self.red:
                i = self.red.index(bgColor)
                newColor = self.selectedRed[i]
            self.board.itemconfigure(self.boardStuff[row][col][1], fill=newColor)
            #add the letter to the label below the board
            playWord = self.play.config()['text'][-1] + letter
            self.play.config(text=playWord)
            #check if a valid play, if so enable play button
            if playWord in self.wordSet:
                self.btnPlay.state(['!disabled'])
            else:
                self.btnPlay.state(['disabled'])

    def set_text_black(self):
        for row in range(5):
            for col in range(5):
                self.board.itemconfigure(self.boardStuff[row][col][1],fill='black')

    def clear_play(self,event=None):
        self.play.config(text='')
        self.set_text_black()
        self.btnPlay.state(['disabled'])
        self.restore_board_colors()

    def history_click(self, event):
        """bound to history.<<TreeviewSelect>>"""
        if not self.historyIgnore:
            self.clear_play()
            #get item id clicked on
            clickedIID = self.history.focus()
            self.historySelection = clickedIID
            txt = self.history.set(clickedIID,'Word')
            board = self.history.set(clickedIID,'Board')
            #update colors on the board to match the board of the word suggested
            self.update_board_colors(board)
            self.history.focus_set()
            self.save_board_colors()
        else:
            self.historyIgnore = False

    def change_difficulty(self, d=''):
        if d != '':
            self.difficulty.set(d)
        if self.difficulty.get() == 'R':
            self.player.changedifficulty(['R', 5, 8, 'R'])
        elif self.difficulty.get() == 'E':
            self.player.changedifficulty(['R', 5, 5, 'S'])
        elif self.difficulty.get() == 'M':
            self.player.changedifficulty(['R', 5, 8, 'S'])
        elif self.difficulty.get() == 'H':
            self.player.changedifficulty(['R', 5, 25, 'S'])
        else:
            self.player.changedifficulty(['A', 5, 25, 'S'])

    def add_to_hist(self, word, score, board, letters, turn):
        #delete the history past the current selection
        txt = ''
        if self.historySelection != -1:
            txt = self.history.set(self.historySelection,'Word')
            toDelete = []
            if txt == self.initialHist:
                toDelete.append(self.historySelection)
            iid = self.history.next(self.historySelection)
            while iid != '':
                toDelete.append(iid)
                iid = self.history.next(iid)
            for iid in toDelete:
                self.history.delete(iid)
        #check if the history treeview is empty
        cnt = len(self.history.get_children())
        if cnt == 0:
            self.history.insert('','end',values=(self.initialHist, '', self.boardColors, self.letters))
        #copy the word, board, and score to the end of the history treeview
        if turn == 1:
            insertID = self.history.insert('','end',tag='blue',values=(word, score, board, letters))
        else:
            insertID = self.history.insert('','end',tag='red',values=(word, score, board, letters))
        self.update_board_colors(board)
        #select the inserted item in history
        self.historyIgnore=True
        self.history.selection_set(insertID)
        self.history.focus(insertID)
        self.historySelection = insertID
        self.history.see(insertID)
        #make the referee aware of which words are in the history
        words = list()
        for iid in self.history.get_children():
            txt = self.history.set(iid,'Word')
            if txt != self.initialHist:
                words.append(txt)
            if iid == self.historySelection:
                break
        self.refPlayer.resetplayed(self.letters, words)
        self.make_word_set()
        #add the "need save" marker
        if self.title()[-1] != '*' and self.file != '':
            self.title(self.title()+'*')

    def play_word(self):
        """tied to self.btnPlay"""
        #change all foreground colors to black
        self.set_text_black()
        #add word made to history with current colors of the board
        word = self.play.config()['text'][-1]
        board = ''.join(self.get_defended_color(row, col) for row in range(5) for col in range(5))
        letters = ''.join([self.board.itemcget(self.boardStuff[row][col][1], 'text') for row in range(5) for col in range(5)])
        blue, red, bluedef, reddef = self.refPlayer.convertboardscore(board.upper())
        score, bluedef, reddef = self.refPlayer.evaluatepos(letters, blue, red)
        self.add_to_hist(word, score, board, letters, 1)
        self.btnPlay.state(['disabled'])
        self.save_board_colors()
        self.clear_play()
        if '-' in board:
            self.do_search()

    def pass_turn(self):
        self.clear_play()
        self.do_search()
        self.save_board_colors()

    def do_search(self, event=None):
        self.busy()
        self.letters = ''.join([self.board.itemcget(self.boardStuff[row][col][1], 'text') for row in range(5) for col in range(5)])
        if not(all([x in ascii_uppercase for x in self.letters]) and len(self.letters) == 25):
            self.not_busy()
            messagebox.showwarning("Concentrate","The board must be completely filled with letters.")
            return
        boardColors = ''.join(self.get_color(row, col) for row in range(5) for col in range(5))
        if 'W' not in boardColors:
            self.not_busy()
            messagebox.showwarning("Concentrate","Game Over.")
            return
        #make the engine aware of which words are in the history
        words = list()
        for iid in self.history.get_children():
            txt = self.history.set(iid,'Word')
            if txt != self.initialHist:
                words.append(txt)
            if iid == self.historySelection:
                break
        self.player.possible(self.letters)
        self.player.resetplayed(self.letters, words)
        start = time()
        word, board, score = self.player.turn(self.letters, boardColors, -1)
        totalTime = round(time()-start,2)
        self.add_to_hist(word, score, board, self.letters, -1)
        self.not_busy()


if __name__ == '__main__':
    PlayGUI().mainloop()
