#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      CHRISTOPHER_IRWIN
#
# Created:     27/03/2013
# Copyright:   (c) CHRISTOPHER_IRWIN 2013
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#!/usr/bin/env python

#intersect en14.txt with 3esl.txt

endings = ('ing','ly','ed','d','er','r','s','es','ings','ers','rs','y','ey','')
prefixes = ('dis','in','im','il','ir','re','un','')

listfile = open('en14.txt','r')
en14set = set()
for line in listfile:
    en14set.add(line.upper().strip())
listfile.close()

listfile = open('3esl.txt','r')
eslset = set()
for line in listfile:
    eslset.add(line.upper().strip())
listfile.close()

goodeslset = set()
for eslword in eslset:
    if eslword in en14set:
        goodeslset.add(eslword)
        for variant in [x for x in [p.upper()+eslword+e.upper() for e in endings for p in prefixes] if x in en14set]:
            goodeslset.add(variant)
        if eslword[-1] == 'E':
            withoute = eslword [:-1]
            for variant in [x for x in [p.upper()+withoute+e.upper() for e in endings for p in prefixes] if x in en14set]:
                goodeslset.add(variant) 

esllist = sorted([w+'\n' for w in goodeslset])

easydict = open('reduced.txt','w')
easydict.writelines(esllist)
easydict.close()
