#-------------------------------------------------------------------------------
# Name:        search
# Purpose:
#
# Author:      CHRISTOPHER_IRWIN
#
# Created:     24/03/2013

#TODO

#simulate from the middle of the game, have score be an input

from player import player0,player1
from time import time
from random import choice

listfile = open('en14.txt','r')
letterlist = list()
for word in listfile:
    word = word.upper().strip()
    for letter in word:
        letterlist.append(letter)
listfile.close()

vowels = ('A','E','I','O','U')

def genletters():
    while True:
        board = ''.join([choice(letterlist) for x in range(25)])
        if 'Q' in board:
            if 'I' not in board:
                continue
        vowelcount = sum([board.count(v) for v in vowels])
        if vowelcount < 3 or vowelcount > 7:
            continue
        break
    return board

def reverseboard(board):
    out = ''
    for char in board:
        if char == 'r': out += 'b'
        elif char == 'R': out += 'B'
        elif char == 'b': out += 'r'
        elif char == 'B': out += 'R'
        else: out += char
    return out

def numscore(board):
    blue = 0
    red = 0
    blued = 0
    redd = 0
    for char in board:
        if char == 'B':
            blue += 1
            blued += 1
        elif char == 'b':
            blue += 1
        elif char == 'R':
            red += 1
            redd += 1
        elif char == 'r':
            red += 1
    return str(blue).zfill(2), str(blued).zfill(2), str(red).zfill(2), str(redd).zfill(2)

def game(allletters='',player0blue=False):
    if allletters == '':
        allletters = genletters()
    allletters = allletters.upper()
    if player0blue:
        b = player0()
        print('player0 plays blue')
        r = player1()
        print('player1 plays red')
    else:
        b = player1()
        print('player1 plays blue')
        r = player0()
        print('player0 plays red')

    b.cache = dict()
    r.cache = dict()
    b.possible(allletters)
    r.possible(allletters)
    turn = 'blue'
    board = '----- ----- ----- ----- -----'
    print(allletters,board)
    playedwords = list()
    while board.find('-') != -1:
        if turn == 'blue':
            word,board = b.turn(allletters,board)
            blue,blued,red,redd = numscore(board)
            playedwords.append(word)
            r.playword(allletters,word)
            print('blue plays',word.ljust(25),board,len(playedwords),'blue:',blue+'('+blued+')','red:',red+'('+redd+')')
            turn = 'red'
        else:
            board = reverseboard(board)
            word,board = r.turn(allletters,board)
            board = reverseboard(board)
            blue,blued,red,redd = numscore(board)
            playedwords.append(word)
            b.playword(allletters,word)
            print(' red plays',word.ljust(25),board,len(playedwords),'blue:',blue+'('+blued+')','red:',red+'('+redd+')')
            turn = 'blue'
    if int(blue) > int(red):
        print('Blue wins!')
        return ('blue',len(playedwords))
    else:
        print('Red wins!')
        return ('red',len(playedwords))

def both(allletters=''):
    if allletters == '':
        allletters = genletters()
    g1res,g1len = game(allletters,True)
    g2res,g2len = game(allletters,False)
    p0wins = 0
    p1wins = 0
    p0len = 0
    p1len = 0
    if g1res == 'blue':
        p0wins += 1
        p0len += g1len
    else:
        p1wins += 1
        p1len += g1len
    if g2res == 'blue':
        p1wins += 1
        p1len += g2len
    else:
        p0wins += 1
        p0len += g2len
    if p0wins > p1wins:
        print('player0 won both games')
        return (2,0,'player0')
    elif p1wins > p0wins:
        print('player1 won both games')
        return (0,2,'player1')
    else:
        print('players tied 1-1')
        if p0len < p1len:
            print('however player0 won faster')
            return (1,1,'player0')

        elif p1len < p0len:
            print('however player1 won faster')
            return (1,1,'player1')
        else:
            print('they both played the same amount of moves to win')
            return (1,1,'tie')

def tournament(matchcount):
    p0tot = 0
    p1tot = 0
    ties = 0
    equal = 0
    win0 = 0
    win1 = 0
    times = []
    for x in range(1,matchcount+1):
        print()
        print('***********************   GAME '+str(x).zfill(4)+'   ***********************')
        print('  score: player0:',p0tot,'player1:',p1tot)
        print()
        strt = time()
        w0,w1,res = both()
        times.append(time()-strt)
        p0tot += w0
        p1tot += w1
        if w0 > w1:
            win0 += 1
        elif w1 > w0:
            win1 += 1
        elif w0==w1:
            ties += 1
            if res == 'player0':
                p0tot += .5
            elif res == 'player1':
                p1tot += .5
            else:
                equal += 1
    print()
    print('***********************     RESULT     ***********************')


    if p0tot > p1tot:
        print('player0 wins',str(p0tot)+'-'+str(p1tot))
    elif p1tot > p0tot:
        print('player1 wins',str(p0tot)+'-'+str(p1tot))
    else:
        print('tie: ',str(p0tot)+'-'+str(p1tot))
    print('ties:',ties, ' equal games:',equal,'player0 wins:',win0,' player1 wins:',win1)
    print('average seconds per game:',round(sum(times)/len(times),2))


