#-------------------------------------------------------------------------------
# Name:        search
# Purpose:
#
# Author:      CHRISTOPHER_IRWIN
#
# Created:     24/03/2013
#
# Purpose: to tune evaluation parameters with an evolutionary algorithm

import os
import sys
import inspect
import logging
import pickle
import multiprocessing
from player import player0
from time import time,strftime
from random import choice, shuffle, sample, random
from itertools import combinations


def find_data_file(filename):
    if getattr(sys, 'frozen', False):
        # The application is frozen
        datadir = os.path.dirname(sys.executable)
    else:
        # The application is not frozen
        # Change this bit to match where you store your data files:
        datadir = os.path.dirname(inspect.stack()[0][1])

    return os.path.join(datadir, filename)


def genletters(vowelCount = -1):
    while True:
        vowels = ('A','E','I','O','U')
        tot = 25
        if vowelCount == -1:
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

def game(allletters, player1, player2):
    if allletters == '':
        allletters = genletters()
        logger.info(allletters)
    allletters = allletters.upper()

    b = player1
    r = player2

    b.cache = dict()
    r.cache = dict()
    b.possible(allletters)
    r.possible(allletters)
    turn = 'blue'
    board = '----- ----- ----- ----- -----'

    playedwords = list()
    bluePassed = redPassed = False
    btime = rtime = 0
    score = 0
    early = False
    while board.find('-') != -1:
        if turn == 'blue':
            oldscore = score
            word,board,score = b.turn(allletters,board,1)
            blue,blued,red,redd = numscore(board)
            playedwords.append(word)
            r.playword(allletters,word)
            if word == '':
                bluePassed = True
            else:
                bluePassed = False
            num = len(playedwords)+1
            turn = 'red'
        else:
            oldscore = score
            word,board,score = r.turn(allletters,board,-1)
            blue,blued,red,redd = numscore(board)
            playedwords.append(word)
            b.playword(allletters,word)
            if word == '':
                redPassed = True
            else:
                redPassed = False
            num = len(playedwords)+1
            turn = 'blue'
        if len(playedwords) > 100 and ((oldscore < 0 and score < 0) or (oldscore > 0 and score > 0)):
            early = True
            break
        if bluePassed and redPassed:
            break

    if not early:
        if blue > red:
            return 2,0
        elif red > blue:
            return 0,2
        else:
            return 1,1
    else:
        if score > 0:
            return 2,0
        else:
            return 0,2

def both(allletters,player1,player2):
    if allletters == '':
        allletters = genletters()
    g1p1s,g1p2s = game(allletters,player1,player2)
    g2p2s,g2p1s = game(allletters,player2,player1)
    p1s = g1p1s + g2p1s
    p2s = g1p2s + g2p2s
    return p1s, p2s

def make_boards():
    vowel_count_list = [3,4,5,5,6,6,7,8] #8 boards with varying vowel counts
    board_list = []
    for x in vowel_count_list:
        gotit = False
        while not gotit:
            good = True
            board = genletters(x)
            for l in board:
                if board.count(l) > 2:
                    good = False #I don't want lots of the same letter (all that does is slow down the engine)
                    break
            if good:
                board_list.append(board)
                gotit = True
    return board_list

def mutate(parent):  #sliding window based on current values for parent +/- .5 above and below
    child = []
    mutation_probability = .6
    for value in parent:
        if random() <= mutation_probability:
            child.append(round(value - .5 + random(),2))
        else:
            child.append(value)
    return tuple(child)

def sex(parent1, parent2):
    child = []
    for i,value in enumerate(parent1):
        newval = round((value + parent2[i]) / 2, 2)
        child.append(newval)
    return tuple(child)

def have_kids(parent_scores): #parent_scores is a dict of {parent:score, parent:score, ..}
    parents = list(parent_scores.keys())
    parents.sort(key=lambda x:parent_scores[x], reverse=True)
    parents.pop()
    parents.pop()
    diff = round(sum([abs(x-y) for (x,y) in zip(parents[0],parents[1])]),2)
    logger.info('%s %s',parents, diff)
    if diff > .5:
        parents.append(sex(parents[0],parents[1])) #if they are different enough, sex makes sense
    else:
        parents.pop() #else, get rid of #2, because it's mostly a copy of #1
    while len(parents) < 4:
        newparent = mutate(parents[0])
        if newparent not in parents: #because the score dictionary will double the score of a duplicated entry here
            parents.append(newparent)
    return parents

def run_both(args):
    board = args[0]
    p1 = args[1][0]
    p2 = args[1][1]
    p1s,p2s = both(board, p1, p2)
    return p1.weights, p1s, p2.weights, p2s

def do_generation(competitors, boards):
    comp_scores = dict()
    comp_objs = dict()
    for p in competitors:
        comp_scores[p] = 0
        comp_objs[p] = player0(difficulty=d, weights=p)
    pairs = list(combinations(competitors,2))
    pairs_obj = [(comp_objs[x], comp_objs[y]) for (x,y) in pairs]
    for board in boards:
        boardzip = [board]*len(pairs)
        args = list(zip(boardzip, pairs_obj))
        outlst = pool.map(run_both,args)
        for out in outlst:
            p1 = out[0]
            p1s = out[1]
            p2 = out[2]
            p2s = out[3]
            comp_scores[p1] += p1s
            comp_scores[p2] += p2s
        logger.info(comp_scores)
    return comp_scores

def evolve(num_generations):
    logger.info('===== Begin Evolution =====')
    boards = make_boards()
    competitors = []
    #start with best weight known, and three mutations
    #best_so_far = (2,.8,1,1,1)  #original values for concentrate
    #best_so_far = (2.09, 0.38, 1.39, 0.54, 1.33) #after 2 generations:
    #best_so_far = (2.22, 0.13, 1.05, 0.43, 0.95) #after 10 more generations
    #best_so_far = (2.1, 0.38, 0.9, 0.43, 1.82) #after 10 more generations
    #best_so_far = (1.75, 0.72, 1.12, 0.85, 1.99) #after 10 more generations
    #best_so_far = (2.14, 0.7, 1.54, 0.71, 1.67) #after 10 more generations
    #best_so_far = (2.14, 0.41, 1.06, 0.71, 1.58) #after 4 more generations
    #best_so_far = (2.39, 0.41, 0.85, 0.71, 1.58) #after 4 more generations
    #best_so_far = (2.46, 0.27, 0.79, 0.87, 2.15) #after 10 more generations
    #best_so_far = (1.64, 0.15, -0.13, 1.47, 1.54) #after 20 more generations
    #best_so_far = (2.06, 0.32, -1.07, 0.8, 1.18) #after 120 more generations
    #to avoid "drifting" along a line of solutions (perhaps increasing or decreasing all weights by a % does not change the strength) I will fix one paramter, uw
    #best_so_far = (1.34, 0.27, -0.42, 0.92, 1.53) after 35 more generations
    #multiply this to get 1 instead of .27, then leave that out
    #best_so_far = (4.95, -3.4, 3.4, 5.6) #hopefully this is equivalent... but I'll do a bunch more generations to be sure
    f = open('evolve_memory.pkl','rb')
    best_dict = pickle.load(f)
    f.close()
    best_so_far = list(best_dict.keys())[0]
    prior_generations = best_dict[best_so_far]
    competitors.append(best_so_far)
    logger.info('starting with %s',best_so_far)
    logger.info('this is the result of %s prior generations',prior_generations)
    logger.info('boards used for this run:')
    for board in boards:
        logger.info('    %s',board)
    while len(competitors) < 4:
        competitors.append(mutate(best_so_far))
    start = time()
    for i in range(num_generations):
        logger.info('Generation %s: %s',i,competitors)
        scores = do_generation(competitors, boards)
        competitors = have_kids(scores)
        best_so_far = max(scores,key=lambda x:scores[x])
        prior_generations += 1
        f = open('evolve_memory.pkl','wb')
        pickle.dump({best_so_far:prior_generations},f)
        f.close()
    score_lst = list(sorted(scores.keys(),key=lambda x:scores[x],reverse=True))
    score_pairs = [(scores[x],x) for x in score_lst]
    logger.info('final score: %s' % score_pairs)
    for (x,y) in score_pairs:
        logger.info('    %s %s' % (x,y))
    end = time()
    avg = round((end-start)/num_generations,2)
    logger.info('%s seconds per generation',avg)
    logger.info('%s seconds total'%round(end-start,2))

if __name__ == '__main__':
    d = ['R',5,25,'S']

    logger = logging.getLogger('evolve')
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler('tests\\evolve.log')
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

    listfile = open(find_data_file('en14.txt'),'r')
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

    pool = multiprocessing.Pool(3)

    evolve(30)

    pool.terminate()