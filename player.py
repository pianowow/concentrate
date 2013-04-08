#-------------------------------------------------------------------------------
# Name:        search
# Purpose:
#
# Author:      CHRISTOPHER_IRWIN
#
# Created:     24/03/2013

#idea to improve:
#define span for each word (average distance between each successive letter) ... could be useful for eliminating non-human words on an easy level
#limited minimax... pick 10 words that pass endgame check and run search on those
#combine groupwords and concentrate functions (group words as they are found)


class player0:
    def __init__(self):
        #self.listfile = open('reduced.txt','r')
        self.listfile = open('en14.txt','r')
        self.wordset = set()
        for word in [word.upper().strip() for word in self.listfile]:
            if len(word) <= 25:
                self.wordset.add(word)
        self.listfile.close()
        self.wordlist = list(self.wordset)
        self.cache = dict() #dict of {letters:(words,played,usability,defendability)}

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
            for word in self.wordlist:
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
            self.cache[letters] = (found,[],u,d)
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
        return sorted(goodlist,key=lambda x:(len(x),x))

    def normalize(self, board):
        '''board is a 2D array of numbers. modifies board to show weighted score (from dw) of defended tiles'''
        #defended weights
        dw = 2
        ndw = -dw
        #nested loop testing if neighbors were in range(5) was slower than this hardcoding... so I kept it
        #also the overhead of writing my own sign function was too slow (to make this more readable)
        #corners
        if board[0][0] > 0 and board[1][0] > 0 and board[0][1] > 0:
            board[0][0] = dw
        elif board[0][0] < 0 and board[1][0] < 0 and board[0][1] < 0:
            board[0][0] = ndw
        else:
            if board[0][0] > 0:
                board[0][0] = 1
            elif board[0][0] < 0:
                board[0][0] = -1
            else:
                board[0][0] = 0
        if board[0][4] > 0 and board[1][4] > 0 and board[0][3] > 0:
            board[0][4] = dw
        elif board[0][4] < 0 and board[1][4] < 0 and board[0][3] < 0:
            board[0][4] = ndw
        else:
            if board[0][4] > 0:
                board[0][4] = 1
            elif  board[0][4] < 0:
                board[0][4] = -1
            else:
                board[0][4] = 0
        if board[4][0] > 0 and board[3][0] > 0 and board[4][1] > 0:
            board[4][0] = dw
        elif board[4][0] < 0 and board[3][0] < 0 and board[4][1] < 0:
            board[4][0] = ndw
        else:
            if board[4][0] > 0:
                board[4][0] = 1
            elif board[4][0] < 0:
                board[4][0] = -1
            else:
                board[4][0] = 0
        if board[4][4] > 0 and board[3][4] > 0 and board[4][3] > 0:
            board[4][4] = dw
        elif board[4][4] < 0 and board[3][4] < 0 and board[4][3] < 0:
            board[4][4] = ndw
        else:
            if board[4][4] > 0:
                board[4][4] = 1
            elif board[4][4] < 0:
                board[4][4] = -1
            else:
                board[4][4] = 0
        #edges
        for col in (1,2,3):
            if board[0][col] > 0 and board[0][col-1] > 0 and board[0][col+1] > 0 and board[1][col] > 0:
                board[0][col] = dw
            elif board[0][col] < 0 and board[0][col-1] < 0 and board[0][col+1] < 0 and board[1][col] < 0:
                board[0][col] = ndw
            else:
                if board[0][col] > 0:
                    board[0][col] = 1
                elif board[0][col] < 0:
                    board[0][col] = -1
                else:
                    board[0][col] = 0
            if board[4][col] > 0 and board[4][col-1] > 0 and board[4][col+1] > 0 and board[3][col] > 0:
                board[4][col] = dw
            elif board[4][col] < 0 and board[4][col-1] < 0 and board[4][col+1] < 0 and board[3][col] < 0:
                board[4][col] = ndw
            else:
                if board[4][col] > 0:
                    board[4][col] = 1
                elif board[4][col] < 0:
                    board[4][col] = -1
                else:
                    board[4][col] = 0
        for row in (1,2,3):
            if board[row][0] > 0 and board[row-1][0] > 0 and board[row+1][0] > 0 and board[row][1] > 0:
                board[row][0] = dw
            elif board[row][0] < 0 and board[row-1][0] < 0 and board[row+1][0] < 0 and board[row][1] < 0:
                board[row][0] = ndw
            else:
                if board[row][0] > 0:
                    board[row][0] = 1
                elif board[row][0] < 0:
                    board[row][0] = -1
                else:
                    board[row][0] = 0
            if board[row][4] > 0 and board[row-1][4] > 0 and board[row+1][4] > 0 and board[row][3] > 0:
                board[row][4] = dw
            elif board[row][4] < 0 and board[row-1][4] < 0 and board[row+1][4] < 0 and board[row][3] < 0:
                board[row][4] = ndw
            else:
                if board[row][4] > 0:
                    board[row][4] = 1
                elif board[row][4] < 0:
                    board[row][4] = -1
                else:
                    board[row][4] = 0
        #others
        for row in (1,2,3):
            for col in (1,2,3):
                if board[row][col] > 0 and board[row][col-1] > 0 and board[row][col+1] > 0 and board[row+1][col] > 0 and board[row-1][col] > 0:
                    board[row][col] = dw
                elif board[row][col] < 0 and board[row][col-1] < 0 and board[row][col+1] < 0 and board[row+1][col] < 0 and board[row-1][col] < 0:
                    board[row][col] = ndw
                else:
                    if board[row][col] > 0:
                        board[row][col] = 1
                    elif board[row][col] < 0:
                        board[row][col] = -1
                    else:
                        board[row][col] = 0

    def evaluatepos(self, allletters,board):
        self.normalize(board)
        u = self.cache[allletters][2] #usability
        d = self.cache[allletters][3] #defendability
        for row in range(5):
            for col in range(5):
                if board[row][col] > 1: #defended
                    board[row][col] = board[row][col] + u[row][col]
                elif board[row][col] < -1: #defended
                    board[row][col] = board[row][col] - u[row][col]
                elif board[row][col] == 1: #not defended, used
                    board[row][col] = d[row][col]
                elif board[row][col] == -1: #not defended, used
                    board[row][col] = - d[row][col]
        total = sum([num for row in board for num in row])
        if 0 in [num for row in board for num in row]: #game not over
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
        '''produces string of bBrRw from numeric score'''
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
                gameendingwords = self.concentrate(allletters,needletters=zeroletters)
                self.cache[allletters+zeroletters] = gameendingwords
            wordgroups = self.groupwords(gameendingwords,anyl)
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
                    newscore = max(scores)
                    if newscore > 999:
                        losing = True
                        break
        if len(gameendingwords) > 0:
            endingsoon = True
        else:
            endingsoon = False
        return (zeroletters,endingsoon,losing,newscore)

    def decide(self, allletters,score,move): #move is 1 for
        '''judges the merit of possible words for this board'''
        board = self.convertboardscore(score)
        self.normalize(board)
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
