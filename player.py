#-------------------------------------------------------------------------------
# Name:        search
# Purpose:
#
# Author:      CHRISTOPHER_IRWIN
#
# Created:     24/03/2013

#idea to improve:
#consider re-working the evaluation to take advantage of bitmap representation of tiles.
#implement and test vulnerability in player1
#define span for each word (average distance between each successive letter) ... could be useful for eliminating non-human words on an easy level
#limited minimax... pick 10 words that pass endgame check and run search on those
#combine groupwords and concentrate functions (group words as they are found)

from string import ascii_uppercase

class player0:
    def __init__(self, difficulty=['A',5,25]): #this represents maximum difficulty
        '''difficulty:#'A' for all words, 'R' for reduced.  numbers for span limit and word length limit'''
        self.difficulty = difficulty
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
        self.cache = dict() #dict of {letters:(words,played,usability,defendability)}

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

    #usablility is a bonus for defended tiles based on letterpopularity
    def usability(self, allletters,lp):
        '''returns a 2D list based on how usable each letter is'''
        m = [[0 for x in range(5)] for y in range(5)]
        for i,l in enumerate(allletters):
            row = i//5
            col = i%5
            m[row][col] = lp[l]
        return m

    #defendability is the average usability of surrounding squares
    def defendability(self, u):
        '''returns a 2D list based on how defendable each letter is'''
        m = [[0 for x in range(5)] for y in range(5)]
        for row in range(5):
            for col in range(5):
                neighborlist = []
                if row-1 in range(5):
                    neighborlist.append(u[row-1][col])
                if col+1 in range(5):
                    neighborlist.append(u[row][col+1])
                if row+1 in range(5):
                   neighborlist.append(u[row+1][col])
                if col-1 in range(5):
                    neighborlist.append(u[row][col-1])
                m[row][col] = round(sum(neighborlist) / len(neighborlist),2)
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
            u = self.usability(letters,lp)
            d = self.defendability(u)
            self.cache[letters] = (tuple(found),[],u,d)
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

##    def normalize(self, board):

    def evaluatepos(self, allletters,board):
        '''board is a 2D array of numbers. modifies board to show weighted score (from dw) of defended tiles'''
        #defended weights
        total = 0
        ending = True
        dw = 2
        ndw = -dw
        u = self.cache[allletters][2] #usability
        d = self.cache[allletters][3] #defendability
        #nested loop testing if neighbors were in range(5) was slower than this hardcoding... so I kept it
        #also the overhead of writing my own sign function was too slow (to make this more readable)
        #corners
        if board[0][0] > 0 and board[1][0] > 0 and board[0][1] > 0:
            board[0][0] = dw + u[0][0]
        elif board[0][0] < 0 and board[1][0] < 0 and board[0][1] < 0:
            board[0][0] = ndw - u[0][0]
        else:
            if board[0][0] > 0:
                board[0][0] = d[0][0]
            elif board[0][0] < 0:
                board[0][0] = -d[0][0]
            else:
                board[0][0] = 0
                ending = False
        total += board[0][0]
        if board[0][4] > 0 and board[1][4] > 0 and board[0][3] > 0:
            board[0][4] = dw + u[0][4]
        elif board[0][4] < 0 and board[1][4] < 0 and board[0][3] < 0:
            board[0][4] = ndw - u[0][4]
        else:
            if board[0][4] > 0:
                board[0][4] = d[0][4]
            elif  board[0][4] < 0:
                board[0][4] = -d[0][4]
            else:
                board[0][4] = 0
                ending = False
        total += board[0][4]
        if board[4][0] > 0 and board[3][0] > 0 and board[4][1] > 0:
            board[4][0] = dw + u[4][0]
        elif board[4][0] < 0 and board[3][0] < 0 and board[4][1] < 0:
            board[4][0] = ndw - u[4][0]
        else:
            if board[4][0] > 0:
                board[4][0] = d[4][0]
            elif board[4][0] < 0:
                board[4][0] = -d[4][0]
            else:
                board[4][0] = 0
                ending = False
        total += board[0][0]
        if board[4][4] > 0 and board[3][4] > 0 and board[4][3] > 0:
            board[4][4] = dw + u[4][4]
        elif board[4][4] < 0 and board[3][4] < 0 and board[4][3] < 0:
            board[4][4] = ndw - u[4][4]
        else:
            if board[4][4] > 0:
                board[4][4] = d[4][4]
            elif board[4][4] < 0:
                board[4][4] = -d[4][4]
            else:
                board[4][4] = 0
                ending = False
        total += board[4][4]
        #edges
        for col in (1,2,3):
            if board[0][col] > 0 and board[0][col-1] > 0 and board[0][col+1] > 0 and board[1][col] > 0:
                board[0][col] = dw + u[0][col]
            elif board[0][col] < 0 and board[0][col-1] < 0 and board[0][col+1] < 0 and board[1][col] < 0:
                board[0][col] = ndw - u[0][col]
            else:
                if board[0][col] > 0:
                    board[0][col] = d[0][col]
                elif board[0][col] < 0:
                    board[0][col] = -d[0][col]
                else:
                    board[0][col] = 0
                    ending = False
            total += board[0][col]
            if board[4][col] > 0 and board[4][col-1] > 0 and board[4][col+1] > 0 and board[3][col] > 0:
                board[4][col] = dw + u[4][col]
            elif board[4][col] < 0 and board[4][col-1] < 0 and board[4][col+1] < 0 and board[3][col] < 0:
                board[4][col] = ndw - u[4][col]
            else:
                if board[4][col] > 0:
                    board[4][col] = d[4][col]
                elif board[4][col] < 0:
                    board[4][col] = -d[4][col]
                else:
                    board[4][col] = 0
                    ending = False
            total += board[4][col]
        for row in (1,2,3):
            if board[row][0] > 0 and board[row-1][0] > 0 and board[row+1][0] > 0 and board[row][1] > 0:
                board[row][0] = dw + u[row][0]
            elif board[row][0] < 0 and board[row-1][0] < 0 and board[row+1][0] < 0 and board[row][1] < 0:
                board[row][0] = ndw - u[row][0]
            else:
                if board[row][0] > 0:
                    board[row][0] = d[row][0]
                elif board[row][0] < 0:
                    board[row][0] = -d[row][0]
                else:
                    board[row][0] = 0
                    ending = False
            total += board[row][0]
            if board[row][4] > 0 and board[row-1][4] > 0 and board[row+1][4] > 0 and board[row][3] > 0:
                board[row][4] = dw + u[row][4]
            elif board[row][4] < 0 and board[row-1][4] < 0 and board[row+1][4] < 0 and board[row][3] < 0:
                board[row][4] = ndw - u[row][4]
            else:
                if board[row][4] > 0:
                    board[row][4] = d[row][4]
                elif board[row][4] < 0:
                    board[row][4] = -d[row][4]
                else:
                    board[row][4] = 0
                    ending = False
            total += board[row][4]
        #others
        for row in (1,2,3):
            for col in (1,2,3):
                if board[row][col] > 0 and board[row][col-1] > 0 and board[row][col+1] > 0 and board[row+1][col] > 0 and board[row-1][col] > 0:
                    board[row][col] = dw + u[row][col]
                elif board[row][col] < 0 and board[row][col-1] < 0 and board[row][col+1] < 0 and board[row+1][col] < 0 and board[row-1][col] < 0:
                    board[row][col] = ndw - u[row][col]
                else:
                    if board[row][col] > 0:
                        board[row][col] = d[row][col]
                    elif board[row][col] < 0:
                        board[row][col] = -d[row][col]
                    else:
                        board[row][col] = 0
                        ending = False
                total += board[row][col]
        #TODO I could eliminate these two list comprehensions by adding the logic in the hard-coded mess above
        #total = sum([num for row in board for num in row])
        #if 0 in [num for row in board for num in row]: #game not over
        if not ending:
            return total
        else: #game over
            #total = sum([1 for row in board for num in row if num > 0])
            #total += sum([-1 for row in board for num in row if num < 0])
            total = sum([num/abs(num) for row in board for num in row])
            return total * 1000

    def arrange(self, allletters,word,wordscore=[[0 for x in range(5)] for y in range(5)],scores=[],used=[],move=1):
        '''recursive function to determine the best placement of word'''
        if len(word) == 0:
            newboard = [row[:] for row in wordscore] #faster than deepcopy
            score = round(self.evaluatepos(allletters,newboard),2)
            if scores != []:
                if move > 0:
                    if score > max(x[0] for x in scores):
                        scores.append((score,newboard))
                else:
                    if score < min(x[0] for x in scores):
                        scores.append((score,newboard))
            else:
                scores.append((score,newboard))
        else:
            l = word[0]
            listindex = list()
            i = allletters.find(l)
            while i >= 0:
                row = i//5
                col = i%5
                score = wordscore[row][col]
                if move == 1:
                    if i not in used and -1 <= score <= 0:  #only care about tiles that change the score
                        listindex.append(i)
                else:
                    if i not in used and 0 <= score <= 1:
                        listindex.append(i)
                i = allletters.find(l, i + 1)
            for i in listindex:
                used.append(i)
                row = i//5
                col = i%5
                oldscore = wordscore[row][col]
                if abs(oldscore) < 2:
                    wordscore[row][col] = move
                self.arrange(allletters, word[1:], wordscore, scores, used, move)
                wordscore[row][col] = oldscore
                used.pop()

    def convertscore(self, letter):
        if letter == 'R': return -1
        elif letter == 'B': return 1
        else: return 0

    def convertboardscore(self, rbscore):
        board = [[0 for x in range(5)] for y in range(5)]
        i = 0
        prevchar = 'x'
        for char in rbscore:
            if char in ('R','B','-','W',' '):
                row = i // 5
                col = i % 5
                board[row][col] = self.convertscore(char)
                i += 1
                prevchar = char
            else:
                num = int(char)
                for x in range(num-1):
                    row = i // 5
                    col = i % 5
                    board[row][col] = self.convertscore(prevchar)
                    i+=1
        return board

    def displayscore(self, board):
        '''produces string of bB-rR from numeric score'''
        s = ''
        for row in board:
            for num in row:
                if num > 1: s += 'B'
                elif 0 < num <= 1: s += 'b'
                elif num == 0: s += '-'
                elif -1 <= num < 0: s += 'r'
                else: s += 'R'
            s+=' '
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

    def endgamecheck(self, allletters, board, move):
        zeroletters = ''
        anyl = ''
        for i,row in enumerate(board):
            for j,s in enumerate(row):
                if s == 0:
                    zeroletters += allletters[i*5+j]
                if move == 1:  #group on red's reply
                    if 0 <= s <= 1:
                        anyl += allletters[5*i+j]
                else:  #group on blue's reply
                    if -1 <= s <= 0:
                        anyl += allletters[5*i+j]
        gameendingwords = []
        losing = False
        endingsoon = False
        newscore = None
        if zeroletters != '':  #don't check if we've already finished the game
            if allletters+zeroletters in self.cache:
                gameendingwords = self.cache[allletters+zeroletters]
            else:
                gameendingwords = tuple(self.concentrate(allletters,needletters=zeroletters))
                self.cache[allletters+zeroletters] = gameendingwords
            wordgroups = tuple(self.groupwords(gameendingwords,anyl))
            for gameendingword in wordgroups:
                scores = []
                used = []
                arrboard = [row[:] for row in board]
                self.arrange(allletters,gameendingword,arrboard,scores,used,-move)
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

    def decide(self, allletters,score,move):
        '''judges the merit of possible words for this board'''
        board = self.convertboardscore(score)
        self.possible(allletters) #saves word list and board stats to cache
        self.evaluatepos(allletters,board) #uses board stats to determine score
        #letters to focus on are undefended opponent and unclaimed
        anyl = ''
        for i,row in enumerate(board):
            for j,score in enumerate(row):
                if move == 1:
                    if -1 <= score <= 0:
                        anyl += allletters[5*i+j]
                else:
                    if 0 <= score <= 1:
                        anyl += allletters[5*i+j]
        words = self.concentrate(allletters,anyletters=anyl)
        num = round(self.evaluatepos(allletters,board),2)
        wordgroups = self.groupwords(words,anyl)
        wordscores = list()
        for x,group in enumerate(wordgroups.keys()):
            wordscore = [row[:] for row in board] #much faster than deepcopy!
            scores = list() #scores formed by different arrangements of the same group
            self.arrange(allletters,group,wordscore,scores,[],move)
            for play in scores:
                playscore = play[0]
                playboard = play[1]
                groupsize = len(wordgroups[group])
                for word in wordgroups[group]:
                    wordscores.append((playscore,word,groupsize,playboard))
        return wordscores

    def playword(self, allletters, word):
        self.cache[allletters][1].append(word)

    def turn(self, allletters, score='wwwwwwwwwwwwwwwwwwwwwwwww',move=1):
        '''displays results of decide'''
        allletters = allletters.upper()
        score = score.upper()
        score = score.replace(' ','')
        if len(allletters) != 25:
            raise ValueError('allletters must be 25 letters')

        wordscores = self.decide(allletters,score,move)

        #look at the highest scores, return first word that doesn't lose
        if move == 1:
            wordscores.sort(reverse=True)
        else:
            wordscores.sort()
        play = 0
        for wordnum,(score,word,groupsize,board) in enumerate(wordscores):
            zeroletters,endingsoon,losing,newscore = self.endgamecheck(allletters,board,move)
            if not losing:
                if move == 1:
                    if score > -999:
                        play = wordnum
                        break
                    else:
                        break
                else:
                    if score < 999:
                        play = wordnum
                        break
                    else:
                        break
        word = wordscores[play][1]
        board = self.displayscore(wordscores[play][3])
        self.playword(allletters,word)

        return word,board

class player1(player0):
    pass
