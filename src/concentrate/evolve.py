#-------------------------------------------------------------------------------
# Name:        search
# Purpose:
#
# Author:      CHRISTOPHER_IRWIN
#
# Created:     23/06/2014
#
# Purpose: to tune evaluation parameters with an evolutionary algorithm

import os
import sys
import inspect
import logging
import pickle
import multiprocessing
#from player import player0,player1
from pathlib import Path
from player import player1
from time import time
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
    for char in board:
        if char == 'B':
            blue += 1
        elif char == 'b':
            blue += 1
        elif char == 'R':
            red += 1
        elif char == 'r':
            red += 1
    return blue,red

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
    score = 0
    early = False
    while board.find('-') != -1:
        if turn == 'blue':
            oldscore = score
            word,board,score = b.turn(allletters,board,1)
            blue,red = numscore(board)
            playedwords.append(word)
            r.playword(allletters,word)
            if word == '':
                bluePassed = True
            else:
                bluePassed = False
            turn = 'red'
        else:
            oldscore = score
            word,board,score = r.turn(allletters,board,-1)
            blue,red = numscore(board)
            playedwords.append(word)
            b.playword(allletters,word)
            if word == '':
                redPassed = True
            else:
                redPassed = False
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
            for letter in board:
                if board.count(letter) > 2:
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
    for x,y in zip(parent1,parent2):
        newval = round((x + y) / 2, 2)
        child.append(newval)
    return tuple(child)

def have_kids(parent_scores):  # parent_scores is a dict of {parent:score, parent:score, ..}
    parents = list(parent_scores.keys())
    parents.sort(key=lambda x:parent_scores[x], reverse=True)
    while len(parents) > 2:
        parents.pop()
    diff = round(sum([abs(x-y) for (x,y) in zip(parents[0],parents[1])]),2)
    logger.info(f'{parents} {diff}')
    if diff > .5:
        parents.append(sex(parents[0],parents[1]))  # if they are different enough, sex makes sense
    else:
        parents.pop()  # else, get rid of #2, because it's mostly a copy of #1
    while len(parents) < 4:
        newparent = mutate(parents[0])
        if newparent not in parents:  # because the score dictionary will double the score of a duplicated entry here
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
        comp_objs[p] = player1(difficulty=d, weights=p)
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

def read_file():
    with open(Path(__file__).parent.parent.parent / 'data' / 'evolve_memory.pkl','rb') as f:
        best_dict = pickle.load(f)
    return best_dict

def new_file(begin_weights, generations=0):
    dct = {begin_weights: generations}
    with open(Path(__file__).parent.parent.parent / 'data' / 'evolve_memory.pkl','wb') as f:
        pickle.dump(dct,f)

def evolve(num_generations):
    logger.info('===== Begin Evolution =====')
    boards = make_boards()
    competitors = []
    #start with best weight known, and three mutations
    #best_so_far = (2.5, 1.25, 1.25, 1.25)  #original values for concentrate (shifted so uw = 1, instead of .8)
    #best_so_far = (4.75, -1.55, 2.6, 6.95) #after 400 generations from original values
    #best_so_far = (4.38, -1.28, 2.29, 7.78) #after 450 generation

    #second run, started with four random values between (-5 and +5) and continued
    #best_so_far =(3.32, 0.35, 2.56, 4.56) #second run after 300 generations (weaker than first run)

    best_dict = read_file()
    best_so_far = list(best_dict.keys())[0]
    prior_generations = best_dict[best_so_far]
    competitors.append(best_so_far)
    logger.info(f'starting with {best_so_far}')
    logger.info(f'this is the result of {prior_generations} prior generations')
    logger.info('boards used for this run:')
    for board in boards:
        logger.info(f'    {board}')
    while len(competitors) < 4:
        newguy = mutate(best_so_far)
        if newguy not in competitors:
            competitors.append(newguy)
    start = time()
    for i in range(num_generations):
        logger.info(f'Generation {i}: {competitors}')
        scores = do_generation(competitors, boards)
        competitors = have_kids(scores)
        best_so_far = max(scores,key=lambda x:scores[x])
        prior_generations += 1
        f = open(Path(__file__).parent.parent.parent / 'data' / 'evolve_memory.pkl','wb')
        pickle.dump({best_so_far:prior_generations},f)
        f.close()
    score_lst = list(sorted(scores.keys(),key=lambda x:scores[x],reverse=True))
    score_pairs = [(scores[x],x) for x in score_lst]
    logger.info(f'final score: {score_pairs}')
    for (x,y) in score_pairs:
        logger.info(f'    {x} {y}')
    end = time()
    avg = round((end-start)/num_generations,2)
    logger.info(f'{avg} seconds per generation')
    logger.info(f'{round(end-start,2)} seconds total')

if __name__ == '__main__':
    d = ['R',5,25,'S']

    project_dir = Path(__file__).parent.parent.parent
    os.makedirs(project_dir / 'log', exist_ok=True)
    logger = logging.getLogger('evolve')
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler(project_dir / 'log' / 'evolve.log')
    fh.setLevel(logging.INFO)
    # define a Handler which writes INFO messages or higher to the sys.stderr
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    # set a format
    myformatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
    # tell the handlers to use this format
    console.setFormatter(myformatter)
    fh.setFormatter(myformatter)
    # add the handler to the root logger
    logger.addHandler(console)
    logger.addHandler(fh)

    listfile = open(Path(__file__).parent.parent.parent / 'data' / 'word_lists' / 'en15.txt')
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
    pool = multiprocessing.Pool(7)

    print(read_file())

    evolve(100)

def begin(num_gens):
    evolve(num_gens)

def multiple(round_size, round_count):
    for x in range(round_count):
        begin(round_size)
