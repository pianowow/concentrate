#-------------------------------------------------------------------------------
# Name:        search
# Purpose:
#
# Author:      CHRISTOPHER_IRWIN
#
# Created:     24/03/2013

#is it possible to write arrange as a loop instead of recursion? might be better for performance

#eliminate the addition of uw and dw in evaluate pos (add in possible)
    #make player1 the same as player0 except possible and evaluatepos, make sure they score words the same.

#gotta be a way to program parity... choosing between a few words on the border between occupations (take the last word!)


from string import ascii_uppercase, digits
from random import choice
from itertools import combinations, count
from time import clock
from math import sqrt
import os
import sys
import logging


class player0:
    def __init__(self, difficulty=['A',5,25,'S'], weights = (5.15, -2.75, 3.09, 5.72)): #this represents maximum difficulty
        '''difficulty:#'A' for all words, 'R' for reduced.  numbers for span limit and word length limit'''
        self.difficulty = difficulty
        self.name = 'stable - player0'
        #load word lists
        listfile = open('en14.txt','r')
        reducedfile = open('reduced.txt','r')
        wordset = set()
        reducedset = set()
        for word in [word.upper().strip() for word in listfile]:
            wordset.add(word)
        for word in [word.upper().strip() for word in reducedfile]:
            reducedset.add(word)
        listfile.close()
        reducedfile.close()
        self.wordlist = list(wordset)
        self.reducedlist = list(reducedset)
        #initialize cache (memory of games, words available for each game, words played, values for tiles)
        self.cache = dict() #dict of {letters:(words,played,defendedscore,undefendedscore)}
        #save reference neighbor dictionary
        self.neighbors= dict() #dict of square:[map].  square is a number 0-24, map is a bitmap of all its neighbors
        def saveneighbor(square, nsquare):
            if nsquare in range(25):
                if square in self.neighbors:
                    self.neighbors[square] = self.neighbors[square] | (1 << nsquare)
                else:
                    self.neighbors[square] = (1 << nsquare)
        for square in range(25):
            saveneighbor(square,square)
            saveneighbor(square,square-5)
            if square % 5 != 4:
                saveneighbor(square,square+1)
            if square % 5 != 0:
                saveneighbor(square,square-1)
            saveneighbor(square,square+5)
        self.endgamearrangecount= 0
        self.weights= weights
        self.dw = weights[0]
        self.uw = 1
        self.dpw = weights[1]
        self.upw = weights[2]
        self.mw = weights[3]

    def changedifficulty(self, diff):
        self.difficulty = diff
        self.cache = dict() #cache saves the word list for the board, which can change if we are using one dictionary vs another

    def possible(self, letters):
        '''Returns words using only these letters.  Also saves constants used for position evaluation later'''
        letters = letters.upper()
        if letters in self.cache:
            return [x for x in self.cache[letters][0] if x not in self.cache[letters][1]] #so we don't suggest words that have already been played
        else:
            found = list()
            wordsizelimit = self.difficulty[2]
            if self.difficulty[0] == 'A':
                for word in [x for x in self.wordlist if len(x) <= wordsizelimit]:
                    good = True
                    for l in word:
                        if letters.count(l) < word.count(l):
                            good = False
                            break
                    if good:
                        found.append(word)
            else:
                for word in [x for x in self.reducedlist if len(x) <= wordsizelimit]:
                    good = True
                    for l in word:
                        if letters.count(l) < word.count(l):
                            good = False
                            break
                    if good:
                        found.append(word)
            #calculate the popularity of each letter
            letterdict = dict()
            for word in found:
                for letter in word:
                    if letter in letterdict:
                        letterdict[letter] += 1
                    else:
                        letterdict[letter] = 1
            letterlst = []
            cnt = []
            for letter in letterdict.keys():
                letterlst.append(letter)
                cnt.append(letterdict[letter])
            mincnt = min(cnt)
            for i,num in enumerate(cnt):
                cnt[i] = num/mincnt  #gets it into range 1-max/min
            maxcnt = max(cnt)
            for i,num in enumerate(cnt):
                cnt[i] = num/maxcnt  #gets it into range 0-1
            for i,letter in enumerate(letterlst):
                letterdict[letter] = round(cnt[i],2)
            for l in ascii_uppercase:
                if l not in letterdict:
                    letterdict[l] = 0
            #calculate defended scores (same as popularity)
            d = [0 for x in range(25)]
            for i,l in enumerate(letters):
                d[i] = letterdict[l]
            #calculate undefended scores (average of neighbor popularity and 1-popularity of square)
            u = [0 for x in range(25)]
            for row in range(5):
                for col in range(5):
                    neighborlist = []
                    if row-1 in range(5):
                        neighborlist.append(d[(row-1)*5+col])
                    if col+1 in range(5):
                        neighborlist.append(d[row*5+col+1])
                    if row+1 in range(5):
                        neighborlist.append(d[(row+1)*5+col])
                    if col-1 in range(5):
                        neighborlist.append(d[row*5+col-1])
                    size = len(neighborlist)
                    for x in range(size):
                        neighborlist.append(1-d[row*5+col])  #prefer non-usable undefended squares
                    u[row*5+col] = round(sum(neighborlist) / len(neighborlist),2)
            self.cache[letters] = [tuple(found),[],d,u] #valid words, played words, defended scores, undefended scores
            return found

    def concentrate(self, allletters, needletters='', notletters='', anyletters=''):
        '''filter possible(allletters) for those that use all needletters, not notletters, and any of anyletters.
        Also removes words that are prefixes of played words'''
        allletters = allletters.upper()
        needletters = needletters.upper()
        found = self.possible(allletters)
        allletterlist = list()
        if needletters != '':
            for word in found: #find words that use all needletters
                good = True
                for l in needletters:
                    if word.count(l) < needletters.count(l):
                        good = False
                        break
                if good:
                    allletterlist.append(word.strip())
        else:
            allletterlist = found
        notletterlist = list()
        if notletters != '': #remove words that use the notletters
            for word in allletterlist:
                good = True
                for l in notletters:
                    if word.count(l) > allletters.count(l) - notletters.count(l): #using 1 R when there are two Rs is fine
                        good = False
                        break
                if good:
                    notletterlist.append(word)
        else:
            notletterlist = allletterlist
        anyletterlist = list()
        if anyletters != '':  #remove words that don't use anyletters
            for word in notletterlist:
              good = False
              for l in anyletters:
                  if l in word:
                      good = True
                      break
              if good:
                  anyletterlist.append(word)
        else:
            anyletterlist = notletterlist
        anyletterlist.sort(key=len)
        goodlist = list()
        for i,word1 in enumerate(anyletterlist): #remove words that are prefixes of played words
            good = True
            lenword1 = len(word1)
            for word2 in self.cache[allletters][1]:
                if word2[:lenword1] == word1:
                    good = False
                    break
            if good:
                goodlist.append(word1)
        return tuple(sorted(goodlist,key=lambda x:(len(x),x)))

    def evaluatepos(self, allletters, blue, red, move):
        '''returns a number indicating who is winning, and by how much.  Positive, blue; negative, red.  Also returns bitmaps of blue defended and red defended squares'''
        bluedef = reddef = 0
        ending = (bin(blue|red).count('1') == 25)
        d = self.cache[allletters][2] #defended
        u = self.cache[allletters][3] #undefended
        bluescore = redscore = 0
        for i in range(25):
            if blue & (1<<i):
                if (blue & self.neighbors[i]) == self.neighbors[i]:
                    bluescore += (self.dw + self.dpw*d[i])
                    bluedef = bluedef | (1<<i)
                else:
                    bluescore += (self.uw + self.upw*u[i])
            if red & (1<<i):
                if (red & self.neighbors[i]) == self.neighbors[i]:
                    redscore += (self.dw + self.dpw*d[i])
                    reddef = reddef | (1<<i)
                else:
                    redscore += (self.uw + self.upw*u[i])
        if not ending:
            #bonus for being away from the zeroletters
            if move == 1:
                mycenter = self.centroid(blue)
                theircenter = self.centroid(red)
            else:
                mycenter = self.centroid(red)
                theircenter = self.centroid(blue)
            zerocenter = self.centroid(~(red|blue))
            mydiff = self.vectordiff(mycenter,zerocenter)
            theirdiff = self.vectordiff(theircenter,zerocenter)
            zerodiff = mydiff - theirdiff
            total = bluescore - redscore + self.mw*zerodiff*move
            return total,bluedef,reddef
        else: #game over
            total = bin(blue).count('1') - bin(red).count('1')
            return total * 1000,bluedef,reddef

    #TODO: is it possible to write arrange as a loop instead of recursion? might be better for performance
    def arrange(self,allletters,word,blue,red,origbluedef,origreddef,scores=dict(),used=[],move=1):
        '''recursive function to determine the best placement of word'''
        if len(word) == 0:
            score,bluedef,reddef = self.evaluatepos(allletters,blue,red,move)
            if (blue,red) not in scores:
                scores[(blue,red)] = (score,bluedef,reddef)
        else:
            l = word[0]
            listindex = list()
            i = allletters.find(l)
            oldred = red
            oldblue = blue
            while i >= 0:
                if i not in used:
                    used.append(i)
                    if move == 1 and (1<<i & origreddef == 0):
                        blue = blue | (1<<i) #set 1 to position i
                        red = red & ~(1<<i) #set 0 to position i
                    elif move == -1 and (1<<i & origbluedef == 0):
                        blue = blue & ~(1<<i) #set 0 to position i
                        red = red | (1<<i) #set 1 to position i
                    self.arrange(allletters,word[1:],blue,red,origbluedef,origreddef,scores,used,move)
                    red = oldred
                    blue = oldblue
                    used.pop()
                i = allletters.find(l, i + 1)

    def convertboardscore(self, rbscore):
        '''produces bitmaps from string of 25 characters representing the colors'''
        i = 0
        prevchar = 'W'
        blue = 0 #bitmap of blue's occupied tiles
        bluedef = 0 #bitmap of blue's defended tiles
        red = 0 #bitmap of red's occupied tiles
        reddef = 0 #bitmap of red's defended tiles
        for char in rbscore:
            if char == 'B':
                blue = blue | (1 << i) #assign 1 to that position in the bitmap
                prevchar = char
                i += 1
            elif char == 'R':
                red = red | (1 << i) #assign 1 to that position in the bitmap
                prevchar = char
                i += 1
            elif char in digits:
                num = int(char)
                for x in range(num-1):
                    if prevchar == 'R':
                        red = red | (1 << i)
                    elif prevchar == 'B':
                        blue = blue | (1 << i)
                    i+=1
            else:
                prevchar = 'W'
                i+=1
        for i in range(25): #check defended
            if (blue & self.neighbors[i]) == self.neighbors[i]:
                bluedef = bluedef | (1 << i) #assign 1 to that position in the bitmap
            if (red & self.neighbors[i]) == self.neighbors[i]:
                reddef = reddef | (1 << i) #assign 1 to that position in the bitmap
        return (blue,red,bluedef,reddef)

    def displayscore(self, blue, red, bluedef, reddef):
        '''produces string of bB-rR from numeric score'''
        s = ''
        for i in range(25):
            if (blue & self.neighbors[i]) == self.neighbors[i]:
                s += 'B'
            elif (red & self.neighbors[i]) == self.neighbors[i]:
                s += 'R'
            elif blue & (1<<i):
                s += 'b'
            elif red & (1<<i):
                s += 'r'
            else:
                s += '-'
            if i % 5 == 4:
                s += ' '
        return s

    def groupwords(self, words, anyl):
        '''groups words to limit the number of calls to arrange (optimization added after using cProfile.run)'''
        wordgroups = dict() #{'groupletters': [word1, word2, etc]}

        for word in words:
            group = ''.join(sorted([l for l in word if l in anyl]))
            if group in wordgroups:
                wordgroups[group].append(word)
            else:
                wordgroups[group]=[word]
        return wordgroups

    def endgamecheck(self, allletters, blue, red, bluedef, reddef, move):
        zeroletters = ''
        zeros = (~blue & ~red)
        anyl = ''
        if move == 1: #reversed here for opponent's reply
            targets = (blue & ~bluedef) | zeros
        else:
            targets = (red & ~reddef) | zeros
        for i in range(25):
            if (1<<i) & targets:
                anyl += allletters[i]
            if (1<<i) & zeros:
                zeroletters += allletters[i]
        gameendingwords = []
        losing = False
        endingsoon = False
        newscore = None
        if zeroletters != '':  #don't check if we've already finished the game
            if allletters+zeroletters in self.cache:
                gameendingwords = self.cache[allletters+zeroletters]
            else:
                gameendingwords = self.concentrate(allletters,needletters=zeroletters)
                self.cache[allletters+zeroletters] = gameendingwords
            wordgroups = tuple(self.groupwords(gameendingwords,anyl))
            for gameendingword in wordgroups:
                scores = dict()
                used = []
                self.arrange(allletters,gameendingword,blue,red,bluedef,reddef,scores,used,-move)
                self.endgamearrangecount += len(scores)
                if move == 1:
                    newscore = min(x[0] for x in scores.values())
                    if newscore < -999:
                        losing = True
                        break
                else:
                    newscore = max(x[0] for x in scores.values())
                    if newscore > 999:
                        losing = True
                        break
        if len(gameendingwords) > 0:
            endingsoon = True
        else:
            endingsoon = False
        return (zeroletters,endingsoon,losing,newscore)

    def ply2(self, allletters, blue, red, bluedef, reddef, move):
        rbscore = self.displayscore(blue,red,bluedef,reddef)
        newrbscore = rbscore.replace(' ','').upper()
        oppscores = self.decide(allletters, newrbscore, '','', -move)
        if move == 1:
            newscore = min(x[0] for x in oppscores)
        else:
            newscore = max(x[0] for x in oppscores)
        #print(rbscore,newscore)
        return newscore

    def decide(self, allletters,score,needletters,notletters,move):
        '''judges the merit of possible words for this board'''
        blue,red,bluedef,reddef = self.convertboardscore(score)
        #find goal for notletters
        maxwordsizepossible = max(len(x) for x in self.possible(allletters))
        #print('max word size',maxwordsizepossible)
        if maxwordsizepossible < 13: #based on testing goal vs flexible version
            goal = self.computegoal(allletters, blue, red, move)
        else:
            goal = 0
        #letters to focus on are undefended opponent and unclaimed
        if move == 1:
            targets = (red & ~reddef) | (~blue & ~red)
        else:
            targets = (blue & ~bluedef) | (~blue & ~red)
        anyl = ''
        dontuse = []
        notletters = ''
        for i,l in enumerate(allletters):
            if (1<<i) & targets:
                anyl += l
            if (1<<i) & goal:
                dontuse.append(i)
                notletters += l
        #if goal:
            #self.logger.debug('goal: '+notletters+' '+str(goal))
        words = self.concentrate(allletters,needletters,notletters,anyl)
        wordgroups = self.groupwords(words,anyl)
        #print(len(words),'words')
        #print(len(wordgroups),'groups')
        wordscores = list()
        for x,group in enumerate(wordgroups.keys()):
            scores = dict() #scores formed by different arrangements of the same group
                            #entries of the form (red,blue):(score,bluedef,reddef)
            self.arrange(allletters,group,blue,red,bluedef,reddef,scores,dontuse,move)
            for playblue,playred in scores:
                playscore, playbluedef, playreddef = scores[(playblue,playred)]
                groupsize = len(wordgroups[group])
                for word in wordgroups[group]:
                    wordscores.append((playscore,word,groupsize,playblue,playred,playbluedef,playreddef))
        #print(len(wordscores),'plays')
        return wordscores

    def playword(self, allletters, word):
        self.cache[allletters][1].append(word)

    def resetplayed(self, allletters, words):
        self.cache[allletters][1] = words

    def unplayword(self, allletters, word):
        if word in self.cache[allletters][1]:
            self.cache[allletters][1].remove(word)

    def turn(self, allletters, score='wwwwwwwwwwwwwwwwwwwwwwwww', move=1, logger=None):
        if logger:
            self.logger = logger
        else:
            self.logger = logging.getLogger()
        '''selects a result from decide'''
        allletters = allletters.upper()
        score = score.upper()
        score = score.replace(' ','')
        if len(allletters) != 25:
            raise ValueError('allletters must be 25 letters')

        wordscores = self.decide(allletters,score,'','',move)
        #wordscores is a list of tuples: (playscore,word,groupsize,playblue,playred,playbluedef,playreddef)
        #look at the highest scores, return first word that doesn't lose
        if self.difficulty[3] == 'S':  # not random difficulty
            if move == 1:
                wordscores.sort(reverse=True, key=lambda x: (x[0],len(x[1])))
            else:
                wordscores.sort(key=lambda x: (x[0],-len(x[1])))
            play = 0
            for wordnum,(numScore,word,groupsize,blue,red,bluedef,reddef) in enumerate(wordscores[:200]):
                zeroletters,endingsoon,losing,newscore = self.endgamecheck(allletters,blue,red,bluedef,reddef,move)
                if not losing:
                    if move == 1:
                        if numScore > -999:
                            play = wordnum
                            break
                        else:
                            break
                    else:
                        if numScore < 999:
                            play = wordnum
                            break
                        else:
                            break
        else:
            play = choice(range(len(wordscores))) #random difficulty
        if len(wordscores) > 0:
            word = wordscores[play][1]
            board = self.displayscore(wordscores[play][3],wordscores[play][4],wordscores[play][5],wordscores[play][6])
            numScore = wordscores[play][0]
            self.playword(allletters,word)
            return word,board,numScore
        else:
            blue, red, bluedef, reddef = self.convertboardscore(score)
            numScore, bluedef, reddef = self.evaluatepos(allletters, blue, red, move)
            return '', self.displayscore(blue, red, bluedef, reddef), numScore

    def computegoal(self, allletters, blue, red, move):
        '''return the favorite smallest group of letters that have no playable spanning words'''
        goodgoals = []
        unoccupiedmap= ~(blue|red)
        unoccupied = []
        for x in range(25):
            if 1<<x & unoccupiedmap == 1<<x:
                unoccupied.append(x)
        lst = self.possible(allletters)
        for r in range(2,len(unoccupied)):
            #print('r =',r)
            for goal in combinations(unoccupied,r):
                goalstr = ''.join(allletters[i] for i in goal)
                goodgoal = True
                for word in lst: #find one word that uses all the goal letters
                    goodword = True
                    for l in goalstr:
                        if word.count(l) < goalstr.count(l):
                            goodword = False
                            break
                    if goodword: #we found a word that uses all the goal letters
                        goodgoal = False
                        break
                if goodgoal:
                    goalmap = 0
                    for i in goal:
                        goalmap |= 1<<i
                    goodgoals.append(goalmap)
            if goodgoals!=[]:
                break
        #once we get here, we've got either an empty list, or a list of equally-sized goals
        #we choose the "best" goal by using the goalvalue function
        if goodgoals == []:
            return 0
        else:
            #self.logger.debug('goal count: '+str(len(goodgoals)))
            return max(goodgoals,key=lambda goal:self.goalvalue(goal, blue, red, move))

    def goalvalue(self, goal, blue, red, move):
        #strict letter popularity reduced the strength of the program
        #testing centroid analysis now
        val = 0
        if move == 1:
            #compute distance between blue centroid and goal centroid = goal value
            if blue:
                v1 = self.centroid(blue)
            else:
                v1 = (2,2)
            v2 = self.centroid(goal)
        else:
            #compute distance between red centroid and goal centroid = goal value
            if red:
                v1 = self.centroid(red)
            else:
                v1 = (2,2)
            v2 = self.centroid(goal)
        val = self.vectordiff(v1, v2)
        #print('blue:',str(self.centroid(blue)),'red:',str(self.centroid(red)),'goal:',str(self.centroid(goal)),'val:',val)
        #self.printmap(blue, red, goal)
        return val

    def vectordiff(self, v1, v2):
        return sqrt((v1[0]-v2[0])**2 + (v1[1]-v2[1])**2)

    def centroid(self, map):
        cnt = 0
        ysum = 0
        xsum = 0
        for i in range(25):
            if (1<<i & map):
                y = i//5
                x = i%5
                ysum+=y
                xsum+=x
                cnt += 1
        if cnt > 0:
            return (xsum/cnt, ysum/cnt)
        else:
            return (2,2)


class player1(player0):
    def __init__(self, difficulty=['A',5,25,'S'], weights = (5.15, -2.75, 3.09, 5.72)): #this represents maximum difficulty
        self.name = 'stable - player0'
        super().__init__(difficulty, weights)

    def possible(self, letters):
        '''Returns words using only these letters.  Also saves constants used for position evaluation later'''
        letters = letters.upper()
        if letters in self.cache:
            return [x for x in self.cache[letters][0] if x not in self.cache[letters][1]] #so we don't suggest words that have already been played
        else:
            found = list()
            wordsizelimit = self.difficulty[2]
            if self.difficulty[0] == 'A':
                for word in [x for x in self.wordlist if len(x) <= wordsizelimit]:
                    good = True
                    for l in word:
                        if letters.count(l) < word.count(l):
                            good = False
                            break
                    if good:
                        found.append(word)
            else:
                for word in [x for x in self.reducedlist if len(x) <= wordsizelimit]:
                    good = True
                    for l in word:
                        if letters.count(l) < word.count(l):
                            good = False
                            break
                    if good:
                        found.append(word)
            #calculate the popularity of each letter
            letterdict = dict()
            for word in found:
                for letter in word:
                    if letter in letterdict:
                        letterdict[letter] += 1
                    else:
                        letterdict[letter] = 1
            letterlst = []
            cnt = []
            for letter in letterdict.keys():
                letterlst.append(letter)
                cnt.append(letterdict[letter])
            mincnt = min(cnt)
            for i,num in enumerate(cnt):
                cnt[i] = num/mincnt  #gets it into range 1-max/min
            maxcnt = max(cnt)
            for i,num in enumerate(cnt):
                cnt[i] = num/maxcnt  #gets it into range 0-1
            for i,letter in enumerate(letterlst):
                letterdict[letter] = round(cnt[i],2)
            for l in ascii_uppercase:
                if l not in letterdict:
                    letterdict[l] = 0
            #calculate defended scores (same as popularity), plus the weights introduced for evolution
            d = [0 for x in range(25)]
            for i,l in enumerate(letters):
                d[i] = self.dw + self.dwp*letterdict[l]
            #calculate undefended scores (average of neighbor popularity and 1-popularity of square)
            u = [0 for x in range(25)]
            for row in range(5):
                for col in range(5):
                    neighborlist = []
                    if row-1 in range(5):
                        neighborlist.append(letterdict[letters[(row-1)*5+col]])
                    if col+1 in range(5):
                        neighborlist.append(letterdict[letters[row*5+col+1]])
                    if row+1 in range(5):
                        neighborlist.append(letterdict[letters[(row+1)*5+col]])
                    if col-1 in range(5):
                        neighborlist.append(letterdict[letters[row*5+col-1]])
                    size = len(neighborlist)
                    for x in range(size):
                        neighborlist.append(1-letterdict[letters[row*5+col]])  #prefer non-usable undefended squares
                    u[row*5+col] = round(sum(neighborlist) / len(neighborlist),2)
            self.cache[letters] = [tuple(found),[],d,u] #valid words, played words, defended scores, undefended scores
            return found

    def evaluatepos(self, allletters, blue, red, move):
        '''returns a number indicating who is winning, and by how much.  Positive, blue; negative, red.  Also returns bitmaps of blue defended and red defended squares'''
        bluedef = reddef = 0
        ending = (bin(blue|red).count('1') == 25)
        d = self.cache[allletters][2] #defended
        u = self.cache[allletters][3] #undefended
        bluescore = redscore = 0
        for i in range(25):
            if blue & (1<<i):
                if (blue & self.neighbors[i]) == self.neighbors[i]:
                    bluescore += d[i]
                    bluedef = bluedef | (1<<i)
                else:
                    bluescore += (self.uw + self.upw*u[i])
            if red & (1<<i):
                if (red & self.neighbors[i]) == self.neighbors[i]:
                    redscore += d[i]
                    reddef = reddef | (1<<i)
                else:
                    redscore += (self.uw + self.upw*u[i])
        if not ending:
            #bonus for being away from the zeroletters
            if move == 1:
                mycenter = self.centroid(blue)
                theircenter = self.centroid(red)
            else:
                mycenter = self.centroid(red)
                theircenter = self.centroid(blue)
            zerocenter = self.centroid(~(red|blue))
            mydiff = self.vectordiff(mycenter,zerocenter)
            theirdiff = self.vectordiff(theircenter,zerocenter)
            zerodiff = mydiff - theirdiff
            total = bluescore - redscore + self.mw*zerodiff*move
            return total,bluedef,reddef
        else: #game over
            total = bin(blue).count('1') - bin(red).count('1')
            return total * 1000,bluedef,reddef