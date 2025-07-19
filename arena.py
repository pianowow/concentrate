#-------------------------------------------------------------------------------
# Name:        search
# Purpose:
#
# Author:      CHRISTOPHER_IRWIN
#
# Created:     24/03/2013

#TODO

import os
import sys
import inspect
import pickle
from player import player0, player1
from time import time,strftime
from random import choice, shuffle, sample

import logging

difficulty = ['A',5,25,'S']

logger = logging.getLogger('arena')
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('tests\\arena.log')
fh.setLevel(logging.INFO)
# define a Handler which writes INFO messages or higher to the sys.stderr
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
# set a format which is simpler for console use
cformatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
fformatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
# tell the handler to use this format
console.setFormatter(cformatter)
fh.setFormatter(fformatter)
# add the handler to the root logger
logger.addHandler(console)
logger.addHandler(fh)

#for the results table (csv file)
logtable = logging.getLogger('csv')
logtable.setLevel(logging.INFO)
th = logging.FileHandler('tests\\arena.csv')
th.setLevel(logging.INFO)
tformatter = logging.Formatter('%(asctime)s,%(message)s','%Y-%m-%d %H:%M:%S')
th.setFormatter(tformatter)
logtable.addHandler(th)
logtable.addHandler(console)

# Now, we can log to the root logger, or any other logger. First the root...
##logging.info('Jackdaws love my big sphinx of quartz.')

# Now, define a couple of other loggers which might represent areas in your
# application:

##logger1 = logging.getLogger('myapp.area1')
##logger2 = logging.getLogger('myapp.area2')
##

def find_data_file(filename):
    if getattr(sys, 'frozen', False):
        # The application is frozen
        datadir = os.path.dirname(sys.executable)
    else:
        # The application is not frozen
        # Change this bit to match where you store your data files:
        datadir = os.path.dirname(inspect.stack()[0][1])

    return os.path.join(datadir, filename)

listfile = open(find_data_file('en15.txt'))
letterlist = list()
for word in listfile:
    word = word.upper().strip()
    for letter in word:
        letterlist.append(letter)
listfile.close()

vowels = ('A','E','I','O','U')

letterhist = dict()
for letter in [x for x in letterlist if x not in vowels]:
    if letter in letterhist:
        letterhist[letter] += 1
    else:
        letterhist[letter] = 1

tot = len(letterlist)
minimum = .25 * letterhist['N'] / tot
newletterlist = []
for letter in letterhist:
    letterhist[letter] = int(max((letterhist[letter]/tot,minimum)) / minimum * 100)
    newletterlist += [letter]*letterhist[letter]

def genletters():
    while True:
        vowels = ('A','E','I','O','U')
        tot = 25
        vowelCount = choice(range(3, 9))
        tot -= vowelCount
        vowels = [choice(vowels) for x in range(vowelCount)]
        cons = sample(newletterlist, tot)
        if 'Q' in cons:
            if 'I' not in vowels:
                continue
        board = vowels+cons
        shuffle(board)
        break
    return ''.join(board)

##def reverseboard(board):
##    out = ''
##    for char in board:
##        if char == 'r': out += 'b'
##        elif char == 'R': out += 'B'
##        elif char == 'b': out += 'r'
##        elif char == 'B': out += 'R'
##        else: out += char
##    return out

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
        logger.info(allletters)
    allletters = allletters.upper()

    filename = ''
    if player0blue:
        b = player0(difficulty)
        logger.debug('player0 plays blue')
        r = player1(difficulty)
        logger.debug('player1 plays red')
        filename = strftime('%Y_%m_%d_%H_%M_%S_b0r1.cgd')
    else:
        b = player1(difficulty)
        logger.debug('player1 plays blue')
        r = player0(difficulty)
        logger.debug('player0 plays red')
        filename = strftime('%Y_%m_%d_%H_%M_%S_b1r0.cgd')
    datadir = os.path.dirname(inspect.stack()[0][1]) +os.sep+'tests'
    fnwithpath = os.path.join(datadir, filename)
    logger.info(fnwithpath)
    saveList = list()
    saveDict = dict()
    b.cache = dict()
    r.cache = dict()
    b.possible(allletters)
    r.possible(allletters)
    turn = 'blue'
    board = '----- ----- ----- ----- -----'
    saveList.append(('I001','[Initial Position]','',board.replace(' ',''), allletters, ''))

    playedwords = list()
    bluePassed = redPassed = False
    btime = rtime = 0
    score = 0
    early = False
    while board.find('-') != -1:
        if turn == 'blue':
            start = time()
            oldscore = score
            word,board,score = b.turn(allletters,board,1)
            blue,blued,red,redd = numscore(board)
            playedwords.append(word)
            r.playword(allletters,word)
            t = round(time() - start,2)
            btime += t
            logger.debug(' '.join(('blue plays',word.ljust(25),board,str(len(playedwords)),'blue:',blue+'('+str(blued)+')','red:',red+'('+str(redd)+')','time:',str(t),'seconds',str(round(score,4)))))
            if word == '':
                bluePassed = True
            else:
                bluePassed = False
            num = len(playedwords)+1
            saveList.append(('I%03d' % num,word,round(score,4),board.replace(' ',''),allletters, turn))
            turn = 'red'
        else:
            start = time()
            oldscore = score
            word,board,score = r.turn(allletters,board,-1)
            blue,blued,red,redd = numscore(board)
            playedwords.append(word)
            b.playword(allletters,word)
            t = round(time() - start,2)
            rtime += t
            logger.debug(' '.join((' red plays',word.ljust(25),board,str(len(playedwords)),'blue:',blue+'('+str(blued)+')','red:',red+'('+str(redd)+')','time:',str(t),'seconds',str(round(score,4)))))
            if word == '':
                redPassed = True
            else:
                redPassed = False
            num = len(playedwords)+1
            saveList.append(('I%03d' % num,word,round(score,4),board.replace(' ',''),allletters, turn))
            turn = 'blue'
        if len(playedwords) > 100 and ((oldscore < 0 and score < 0) or (oldscore > 0 and score > 0)):
            early = True
            break
        if bluePassed and redPassed:
            break
    saveDict['history'] = saveList
    saveDict['letters'] = allletters
    saveDict['colors'] = '-'*25
    saveDict['selected'] = 'I001'
    f = open(fnwithpath,'wb')
    pickle.dump(saveDict,f)
    f.close()

    if not early:
        if blue > red:
            logger.debug('Blue wins!')
            return ('blue', len(playedwords), btime, rtime, fnwithpath)
        elif red > blue:
            logger.debug('Red wins!')
            return ('red', len(playedwords), btime, rtime, fnwithpath)
        else:
            logger.debug('Tie')
            return ('', len(playedwords), btime, rtime, fnwithpath)
    else:
        if score > 0:
            logger.debug('Blue wins!')
            return ('blue', len(playedwords), btime, rtime, fnwithpath)
        else:
            logger.debug('Red wins!')
            return ('red', len(playedwords), btime, rtime, fnwithpath)



def both(allletters=''):
    if allletters == '':
        allletters = genletters()
    ref = player0(difficulty)
    numwords = len(ref.possible(allletters))
    biggestlength = max(len(x) for x in ref.possible(allletters))
        #logger.info(allletters + ' - number of possible words: ' +str(numwords))
        #logger.info(allletters + ' - longest word length: ' +str(biggestlength))
    g1res,g1len,b1time,r1time,fnwithpath = game(allletters,True)
    logger.info('result: '+g1res+' '+str(g1len) +' words played')
    #datetime,whowentfirst,whowon,gamelength,allletters,biggestwordlength,possiblewords,
    if g1res == 'blue':
        winner = 'player0'
    elif g1res == 'red':
        winner = 'player1'
    else:
        winner = 'tie'
    logtable.info('%s,%s,%s,%d,%d,%d,%s','player0',winner,allletters,g1len,biggestlength,numwords,fnwithpath)
    g2res,g2len,b2time,r2time,fnwithpath = game(allletters,False)
    logger.info('result: '+g2res+' '+str(g2len) +' words played')
    if g2res == 'blue':
        winner = 'player1'
    elif g2res == 'red':
        winner = 'player0'
    else:
        winner = 'tie'
    logtable.info('%s,%s,%s,%d,%d,%d,%s','player1',winner,allletters,g2len,biggestlength,numwords,fnwithpath)

    p0time = b1time+r2time
    p1time = r1time+b2time
    p0wins = 0
    p1wins = 0
    p0len = 0
    p1len = 0
    if g1res == 'blue':
        p0wins += 1
        p0len += g1len
    elif g1res == 'red':
        p1wins += 1
        p1len += g1len
    else:
        p0len += g1len
        p1len += g1len
    if g2res == 'blue':
        p1wins += 1
        p1len += g2len
    elif g2res == 'red':
        p0wins += 1
        p0len += g2len
    else:
        p0len += g2len
        p1len += g2len
    if p0wins > p1wins:
        logger.info('player0 won both games')
        return (2,0,'player0',p0time,p1time)
    elif p1wins > p0wins:
        logger.info('player1 won both games')
        return (0,2,'player1',p0time,p1time)
    else:
        temp = 'players tied 1-1. '
        if p0len < p1len:
            logger.info(temp+'however player0 won faster')
            return (1,1,'player0',p0time,p1time)

        elif p1len < p0len:
            logger.info(temp+'however player1 won faster')
            return (1,1,'player1',p0time,p1time)
        else:
            logger.info(temp+'they both played the same amount of moves to win')
            return (1,1,'tie',p0time,p1time)

def match(matchcount):
    p0tot = 0
    p1tot = 0
    ties = 0
    equal = 0
    win0 = 0
    win1 = 0
    times = []
    p0tottime = p1tottime = 0
    logger.info('')
    logger.info('')
    logger.info('MATCH BEGINS - difficulty: '+str(difficulty))
    logger.info('')
    for x in range(1,matchcount+1):
        logger.info('')
        logger.info('***********************   GAME '+str(x).zfill(4)+'   ***********************')
        logger.info('  score: player0: '+str(round(p0tot,1))+' player1: '+str(round(p1tot,1)))
        logger.debug('')
        strt = time()
        w0,w1,res,p0time,p1time = both()
        times.append(time()-strt)
        p0tottime += p0time
        p1tottime += p1time
        p0tot = round(w0+p0tot,1)
        p1tot = round(w1+p1tot,1)
        if w0 > w1:
            win0 += 1
        elif w1 > w0:
            win1 += 1
        elif w0==w1:
            ties += 1
            if res == 'player0':
                p0tot += .1
            elif res == 'player1':
                p1tot += .1
            else:
                equal += 1
    logger.info('')
    logger.info('***********************     RESULT     ***********************')

    if p0tot > p1tot:
        logger.info('player0 wins '+str(round(p0tot,1))+'-'+str(round(p1tot,1)))
    elif p1tot > p0tot:
        logger.info('player1 wins '+str(round(p0tot,1))+'-'+str(round(p1tot,1)))
    else:
        logger.info('tie: '+str(p0tot)+'-'+str(p1tot))
    logger.info('ties: '+str(ties)+ ' equal games: '+str(equal)+' player0 wins: '+str(win0)+' player1 wins: '+str(win1))
    logger.info('player0 time used: '+str(round(p0tottime,2))+' player1 time used: '+str(round(p1tottime,2)))
    if p0tottime > p1tottime:
        logger.info('player0 was '+str(round((p0tottime-p1tottime)/p1tottime*100))+' percent slower')
    elif p0tottime < p1tottime:
        logger.info('player1 was '+str(round((p1tottime-p0tottime)/p0tottime*100))+' percent slower')
    logger.info('average seconds per game: '+str(round(sum(times)/len(times),2)))


