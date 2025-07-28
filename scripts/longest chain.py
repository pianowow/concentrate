#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      CHRISTOPHER_IRWIN
#
# Created:     07/08/2014
# Copyright:   (c) CHRISTOPHER_IRWIN 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------

listfile = open('en15.txt')
wordlist = list()
for word in listfile:
    word = word.upper().strip()
    wordlist.append(word)
listfile.close()

wordset = set(wordlist)

wordlist.sort(key=lambda x:(len(x),x))

suffixwords= list()

maxprefixcnt = 0

for word in wordlist:
    prefixcnt = 0
    for i in range(2,len(word)):
        if word[:i] in wordset:
            prefixcnt += 1
    if prefixcnt == maxprefixcnt:
        suffixwords.append(word)
    elif prefixcnt > maxprefixcnt:
        maxprefixcnt = prefixcnt
        suffixwords = [word]

print(suffixwords, maxprefixcnt)

for word in suffixwords:
    print(word)
    for i in range(2,len(word)):
        if word[:i] in wordset:
            print(word[:i])
