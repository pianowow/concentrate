#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      CHRISTOPHER_IRWIN
#
# Created:     12/08/2014
# Copyright:   (c) CHRISTOPHER_IRWIN 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------


from player import player0
from time import time
#import multiprocessing
#import pickle

def centroid(map):
    cnt = 0
    ysum = 0
    xsum = 0
    for i in range(25):
        if (1<<i & map):
            y = i//5
            x = i%5
            ysum+=y
            xsum+=x
            cnt +=1
    if cnt > 0:
        return (xsum/cnt, ysum/cnt)
    else:
        return (2,2)


##def centroid(map):
##    cnt = bin(map).count('1')
##    ysum = 0
##    xsum = 0
##    if cnt > 0:
##
##        for i in range(25):
##            if (1<<i & map):
##                y = i//5
##                x = i%5
##                ysum+=y
##                xsum+=x
##        return (xsum/cnt, ysum/cnt)
##
##    else:
##        return (2,2)

##def centroid(map):
##    d = [(i//5,i%5) for i in range(25) if 1<<i & map]
##    cnt = len(d)
##    if cnt:
##        xsum, ysum = [sum(x) for x in zip(*d)]
##        return (xsum/cnt, ysum/cnt)
##    else:
##        return (2,2)


##def centroid(map):
##    if map == 0:
##        return (2,2)
##    b = '{0:025b}'.format(map)
##    cnt = b.count('1')
##    #cnt = sum([1<<i & map > 0 for i in range(25)])  #slower than counting the ones in the string representation
##    #x = sum([i*c for i,c in enumerate([b[row:row+5].count('1') for row in range(0,25,5)])]) / cnt
##    #y = sum([i*c for i,c in enumerate([b[col:col+21:5].count('1') for col in range(0,5)])]) / cnt
##    return (x,y)




if __name__ == '__main__':
    #pool = multiprocessing.Pool(3)

    centroidmemory = dict()

    beg = time()
    p = player0()
    for x in range(2**20):
        y = centroid(x)

    print(time()-beg,'seconds')

    #outlst = pool.map(centroid,inputlst)
    #print(time()-beg,'seconds to get outlst')

##    beg = time()
##    for x,y in zip(inputlst,outlst):
##        centroidmemory[x] = y
##    print(time()-beg,'seconds to get centroidmemory')
##    print(len(centroidmemory))
##
##    beg = time()
##    f = open('centroidmemory.pkl','wb')
##    pickle.dump(centroidmemory,f)
##    f.close()
##    print(time()-beg,'seconds to write the file')
