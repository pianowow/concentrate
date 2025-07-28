#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      CHRISTOPHER_IRWIN
#
# Created:     28/05/2014
# Copyright:   (c) CHRISTOPHER_IRWIN 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#!/usr/bin/env python

##import arena
##from player import player0
##
##p0 = player0(['R',5,25,'S'])
##
##lenhist = dict()
##lst = list()
##
##for x in range(50):
##    letters = arena.genletters()
##    words = p0.possible(letters)
##    mylenhist = dict()
##    for word in words:
##        length = len(word)
##        if length in mylenhist:
##            mylenhist[length] += 1
##        else:
##            mylenhist[length] = 1
##    print(letters,len(words),mylenhist)
##    lst.append((len(words),letters,mylenhist))


def grep(*matches):
    """Returns a generator function that operates on an iterable:
        filters items in the iterable that match any of the patterns.

    match: a callable returning a True value if it matches the item

    >>> import re
    >>> input = ["alpha\n", "beta\n", "gamma\n", "delta\n"]
    >>> list(grep(re.compile('b').match)(input))
    ['beta\n']
    """
    def _do_grep_wrapper(*matches):
        def _do_grep(lines):
            for line in lines:
                for match in matches:
                    if match(line):
                        yield line
                        break
        return _do_grep
    return _do_grep_wrapper(*matches)

f = open('tests/arena.log')
grepper = grep(lambda line: "longest" in line or "won both" in line or "tied" in line ) # a function
matched = grepper(f) # a generator object
out = ''
for line in matched:
    out+=line

print(out)