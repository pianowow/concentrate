#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      CHRISTOPHER_IRWIN
#
# Created:     24/09/2014
# Copyright:   (c) CHRISTOPHER_IRWIN 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------

f = open('en15.txt')
for line in f:
    if len(line) == 26:
        print(line)