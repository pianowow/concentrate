#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      CHRISTOPHER_IRWIN
#
# Created:     08/03/2013
# Copyright:   (c) CHRISTOPHER_IRWIN 2013
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#!/usr/bin/env python

listfile = open('en14.txt')
wordset1 = set()
for line in listfile:
    wordset1.add(line.upper().strip())
listfile.close()
wordlist1 = list(wordset1)

for word in wordlist1:
    if len(word) > 20:
        print(word, len(word))

##listfile = open('easy2.txt','r')
##wordset2 = set()
##for line in listfile:
##    wordset2.add(line.upper().strip())
##listfile.close()
##wordlist2 = list(wordset2)
##
##print([x for x in wordlist1 if x not in wordset2])
##print(sorted([x for x in wordlist2 if x not in wordset1]))
