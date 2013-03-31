#-------------------------------------------------------------------------------
# Name:        search
# Purpose:
#
# Author:      CHRISTOPHER_IRWIN
#
# Created:     11/02/2013

from time import time
from player import player0,player1

class search(player0):
    def turn(self, allletters, score='wwwwwwwwwwwwwwwwwwwwwwwww',move=1):
        '''displays results of decide'''
        allletters = allletters.upper()
        score = score.upper()
        if len(allletters) != 25:
            raise ValueError('allletters must be 25 letters')
        print('searching...')
        start = time()
        wordscores = self.decide(allletters,score,move)
        end = time()
        print(round(end-start,2),'seconds to determe the best plays',)
        print(len(wordscores),'words found')
        showhidden = False
        #look at the highest scores, print each word list associated

        print('')
        print('best scoring words:')
        #words = sorted(list(worddict.keys()),key=lambda x:worddict[x][0],reverse=True)
        wordscores.sort(reverse=True)  #turn bias here
        showhidden = False
        wordnum = 0
        amounttodisplay = 5
        lastdisplayed = -1
        previouslastdisplayed = -1
        while True:
            displayed = 0
            previouslastdisplayed = lastdisplayed
            for wordnum,(score,word,groupsize,board) in enumerate(wordscores): #print score and check if opponent can win on next turn
                if wordnum > lastdisplayed and displayed < amounttodisplay:
                    zeroletters,endingsoon,losing = self.endgamecheck(allletters,board,move)
                    if losing:
                        if showhidden:
                            print(wordnum,word.ljust(25),score,groupsize,self.displayscore(board),zeroletters,'loses')
                            displayed += 1                            
                    elif endingsoon:
                        print(wordnum,word.ljust(25),score,groupsize,self.displayscore(board),zeroletters,'ending soon')
                        lastdisplayed = wordnum
                        displayed += 1
                    else:
                        print(wordnum,word.ljust(25),score,groupsize,self.displayscore(board),zeroletters)
                        lastdisplayed = wordnum
                        displayed += 1
                elif displayed >= amounttodisplay:
                    break
            txt = input('Type a number to remove, M for more, H to toggle hidden: ')
            #txt = ''
            if txt == '':
                break
            elif txt.upper() == 'M':
                print()
            elif txt.upper() == 'H':
                showhidden = not showhidden
                lastdisplayed = -1
                print()
                print('showing hidden words that can lose the game on the opponent''s move')
                print()
            else: #remove word from wordscores and add to cached played words
                num = int(txt)
                word = wordscores[num][1]
                print()
                print('removing',txt,word)
                print()
                wordscores.pop(num)
                lastdisplayed = previouslastdisplayed
                self.cache[allletters][1].append(word)

class easysearch(search):
    listfile = open('easy.txt','r')
    wordset = set()
    for word in [word.upper().strip() for word in listfile]:
        if len(word) <= 25:
            wordset.add(word)
    listfile.close()
    wordlist = list(wordset)
    


h = search()
def turn(alll,score='wwwwwwwwwwwwwwwwwwwwwwwww',m=1):
    h.turn(alll,score,m)

e = easysearch()
def easy(alll,score='wwwwwwwwwwwwwwwwwwwwwwwww',m=1):
    e.turn(alll,score,m)
