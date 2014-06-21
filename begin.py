#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      CHRISTOPHER_IRWIN
#
# Created:     11/06/2014
# Copyright:   (c) CHRISTOPHER_IRWIN 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#!/usr/bin/env python
import pickle

f = open('recent.ccd','wb')
pickle.dump([],f)
f.close()