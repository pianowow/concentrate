#-------------------------------------------------------------------------------
# Name:        search
# Purpose:
#
# Author:      CHRISTOPHER_IRWIN
#
# Created:     24/03/2013

#idea to improve:
#limited minimax... pick 10 words that pass endgame check and run search on those

from string import ascii_uppercase, digits
from random import choice
import os
import sys

def find_data_file(filename):
    if getattr(sys, 'frozen', False):
        # The application is frozen
        datadir = os.path.dirname(sys.executable)
    else:
        # The application is not frozen
        datadir = os.path.dirname(__file__)

    return os.path.join(datadir, filename)

class player0:
    def __init__(self, difficulty=['A',5,25,'S']): #this represents maximum difficulty
        '''difficulty:#'A' for all words, 'R' for reduced.  numbers for span limit and word length limit'''
        self.difficulty = difficulty
        listfile = open(find_data_file('en14.txt'),'r')
        reducedfile = open(find_data_file('reduced.txt'),'r')
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
        self.cache = dict() #dict of {letters:(words,played,usability,defendability)}
        self.neighbors= dict() #dict of (row,col):[(nrow1,ncol1),(nrow2,ncol2),...] for all neighboring squares
        self.makeneighbordict()

    def makeneighbordict(self):
        for square in range(25):
            self.saveneighbor(square,square)
            self.saveneighbor(square,square-5)
            if square % 5 != 4:
                self.saveneighbor(square,square+1)
            if square % 5 != 0:
                self.saveneighbor(square,square-1)
            self.saveneighbor(square,square+5)

    def saveneighbor(self, square, nsquare):
        if nsquare in range(25):
            if square in self.neighbors:
                self.neighbors[square] = self.neighbors[square] | (1 << nsquare)
            else:
                self.neighbors[square] = (1 << nsquare)

    def changedifficulty(self, diff):
        self.difficulty = diff
        self.cache = dict() #cache saves the word list for the board, which can change if we are using one dictionary vs another

    def letterpopularity(self, words):
        '''returns a histogram (values 0-1) of the letters in words'''
        letterdict = dict()
        for word in words:
            for letter in word:
                if letter in letterdict:
                    letterdict[letter] += 1
                else:
                    letterdict[letter] = 1
        letters = []
        cnt = []
        for letter in letterdict.keys():
            letters.append(letter)
            cnt.append(letterdict[letter])
        mincnt = min(cnt)
        for i,num in enumerate(cnt):
            cnt[i] = num/mincnt  #gets it into range 1-max/min
        maxcnt = max(cnt)
        for i,num in enumerate(cnt):
            cnt[i] = num/maxcnt  #gets it into range 0-1
        for i,letter in enumerate(letters):
            letterdict[letter] = round(cnt[i],2)
        for l in ascii_uppercase:
            if l not in letterdict:
                letterdict[l] = 0
        return letterdict

    def defended_score(self, allletters,lp):
        m = [0 for x in range(25)]
        for i,l in enumerate(allletters):
            m[i] = lp[l]
        return m

    def undefended_score(self, d):
        m = [0 for x in range(25)]
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
                m[row*5+col] = round(sum(neighborlist) / len(neighborlist),2)
        return m

    def possible(self, letters):
        '''Returns words using only these letters'''
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
            lp = self.letterpopularity(found)
            d = self.defended_score(letters,lp)
            u = self.undefended_score(d)
            self.cache[letters] = [tuple(found),[],d,u]
            return found

    def concentrate(self, allletters,needletters='',anyletters=''):
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
        anyletterlist = list()
        if anyletters != '':  #remove words that don't use anyletters
            for word in allletterlist:
              good = False
              for l in anyletters:
                  if l in word:
                      good = True
                      break
              if good:
                  anyletterlist.append(word)
        else:
            anyletterlist = allletterlist
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

    def evaluatepos(self, allletters, blue, red):
        '''returns a number indicating who is winning, and by how much.  Positive, blue; negative, red.  Also returns bitmaps of blue defended and red defended squares'''
        bluedef = reddef = 0
        ending = (bin(blue|red).count('1') == 25)
        dw = 2
        uw = 1
        d = self.cache[allletters][2] #defended
        u = self.cache[allletters][3] #undefended
        bluescore = redscore = 0
        vulnerableRed = 0
        vulnerableBlue = 0
        for i in range(25): #check defended
            if blue & (1<<i):
                if (blue & self.neighbors[i]) == self.neighbors[i]:
                    bluescore += (dw + d[i])
                    bluedef = bluedef | (1<<i)
                else:
                    bluescore += (uw + u[i])
                    vulnerableBlue |= (self.neighbors[i] & ~blue)
            if red & (1<<i):
                if (red & self.neighbors[i]) == self.neighbors[i]:
                    redscore += (dw + d[i])
                    reddef = reddef | (1<<i)
                else:
                    redscore += (uw + u[i])
                    vulnerableRed |= (self.neighbors[i] & ~red)
        vulnerableBlue = bin(vulnerableBlue).count('1')
        vulnerableRed = bin(vulnerableRed).count('1')
        total = bluescore - redscore - vulnerableBlue/5 + vulnerableRed/5
        if not ending:
            return round(total,2),bluedef,reddef
        else: #game over
            total = bin(blue).count('1') - bin(red).count('1')
            return total * 1000,bluedef,reddef

    def arrange(self,allletters,word,blue,red,targets,scores=[],used=[],move=1):
        '''recursive function to determine the best placement of word'''
        if len(word) == 0:
            score,bluedef,reddef = self.evaluatepos(allletters,blue,red)
            if (blue,red) not in ((x[1],x[2]) for x in scores):
                scores.append((score,blue,red,bluedef,reddef))
        else:
            l = word[0]
            listindex = list()
            i = allletters.find(l)
            oldred = red
            oldblue = blue
            while i >= 0:
                if i not in used and ((1<<i) & targets): #only care about tiles that change the score
                    used.append(i)
                    if move == 1:
                        blue = blue | (1<<i) #set 1 to position i
                        red = red & ~(1<<i) #set 0 to position i
                    else:
                        blue = blue & ~(1<<i) #set 0 to position i
                        red = red | (1<<i) #set 1 to position i
                    self.arrange(allletters,word[1:],blue,red,targets,scores,used,move)
                    red = oldred
                    blue = oldblue
                    used.pop()
                i = allletters.find(l, i + 1)

    def convertscore(self, letter):
        if letter == 'R': return -1
        elif letter == 'B': return 1
        else: return 0

    def convertboardscore(self, rbscore):
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
        wordgroups = dict() #
        for word in words:
            group = [l for l in word if l in anyl]
            newgroup = group[:]
            for letter in group:  #remove letters that are duplicated by defended or occupied tiles
                while newgroup.count(letter) > anyl.count(letter):
                    newgroup.remove(letter)
            group = tuple(sorted(newgroup))
            if group in wordgroups:
                wordgroups[group].append(word)
            else:
                wordgroups[group]=[word]
        return wordgroups

    def endgamecheck(self, allletters, blue, red, bluedef, reddef, move):
        zeroletters = ''
        anyl = ''
        zeros = (~blue & ~red)
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
                scores = []
                used = []
                self.arrange(allletters,gameendingword,blue,red,targets,scores,used,-move)
                if move == 1:
                    newscore = min(scores)[0]
                    if newscore < -999:
                        losing = True
                        break
                else:
                    newscore = max(scores)[0]
                    if newscore > 999:
                        losing = True
                        break
        if len(gameendingwords) > 0:
            endingsoon = True
        else:
            endingsoon = False
        return (zeroletters,endingsoon,losing,newscore)

    def decide(self, allletters,score,needletters,move):
        '''judges the merit of possible words for this board'''
        #board = self.convertboardscore(score)
        blue,red,bluedef,reddef = self.convertboardscore(score)
        #letters to focus on are undefended opponent and unclaimed
        if move == 1:
            targets = (red & ~reddef) | (~blue & ~red)
        else:
            targets = (blue & ~bluedef) | (~blue & ~red)
        anyl = ''
        for i in range(25):
            if (1 << i) & targets:
                anyl += allletters[i]
        words = self.concentrate(allletters,needletters,anyletters=anyl)
        wordgroups = self.groupwords(words,anyl)
        wordscores = list()
        for x,group in enumerate(wordgroups.keys()):
            #wordscore = [row[:] for row in board] #much faster than deepcopy!
            scores = list() #scores formed by different arrangements of the same group  #TODO make this a set
            self.arrange(allletters,group,blue,red,targets,scores,[],move)
            for play in scores:
                playscore = play[0]
                playblue = play[1]
                playred = play[2]
                playbluedef = play[3]
                playreddef = play[4]
                groupsize = len(wordgroups[group])
                for word in wordgroups[group]:
                    wordscores.append((playscore,word,groupsize,playblue,playred,playbluedef,playreddef))
        return wordscores

    def playword(self, allletters, word):
        self.cache[allletters][1].append(word)

    def resetplayed(self, allletters, words):
        self.cache[allletters][1] = words

    def turn(self, allletters, score='wwwwwwwwwwwwwwwwwwwwwwwww', move=1):
        '''displays results of decide'''
        allletters = allletters.upper()
        score = score.upper()
        score = score.replace(' ','')
        if len(allletters) != 25:
            raise ValueError('allletters must be 25 letters')

        wordscores = self.decide(allletters,score,'',move)

        #look at the highest scores, return first word that doesn't lose
        if self.difficulty[3] == 'S':  # this is how random difficulty is implemented
            if move == 1:
                wordscores.sort(reverse=True, key=lambda x: (x[0],len(x[1])))
            else:
                wordscores.sort(key=lambda x: (x[0],-len(x[1])))
            play = 0
            for wordnum,(numScore,word,groupsize,blue,red,bluedef,reddef) in enumerate(wordscores):
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
            play = choice(range(len(wordscores)))
        if len(wordscores) > 0:
            word = wordscores[play][1]
            board = self.displayscore(wordscores[play][3],wordscores[play][4],wordscores[play][5],wordscores[play][6])
            numScore = wordscores[play][0]
            self.playword(allletters,word)
            return word,board,numScore
        else:
            blue, red, bluedef, reddef = self.convertboardscore(score)
            numScore, bluedef, reddef = self.evaluatepos(allletters, blue, red)
            return '', self.displayscore(blue, red, bluedef, reddef), numScore


class player1(player0):
    def evaluatepos(self, allletters, blue, red):
        '''returns a number indicating who is winning, and by how much.  Positive, blue; negative, red.  Also returns bitmaps of blue defended and red defended squares'''
        bluedef = reddef = 0
        ending = (bin(blue|red).count('1') == 25)
        dw = 2
        uw = 1
        d = self.cache[allletters][2] #defended
        u = self.cache[allletters][3] #undefended
        bluescore = redscore = 0
        vulnerableRed = 0
        vulnerableBlue = 0
        for i in range(25): #check defended
            if blue & (1<<i):
                if (blue & self.neighbors[i]) == self.neighbors[i]:
                    bluescore += (dw + d[i])
                    bluedef = bluedef | (1<<i)
                else:
                    bluescore += (uw + u[i])
                    vulnerableBlue |= (self.neighbors[i] & ~blue)
            if red & (1<<i):
                if (red & self.neighbors[i]) == self.neighbors[i]:
                    redscore += (dw + d[i])
                    reddef = reddef | (1<<i)
                else:
                    redscore += (uw + u[i])
                    vulnerableRed |= (self.neighbors[i] & ~red)
        vulnerableBlue = bin(vulnerableBlue).count('1')
        vulnerableRed = bin(vulnerableRed).count('1')
        total = bluescore - redscore - vulnerableBlue/2 + vulnerableRed/2
        if not ending:
            return round(total,2),bluedef,reddef
        else: #game over
            total = bin(blue).count('1') - bin(red).count('1')
            return total * 1000,bluedef,reddef