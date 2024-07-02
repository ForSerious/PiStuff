import os
import globals as g

'''Yields all files in the folder rootdir'''
def generateNextFile(rootdir):
  for path, dirlist, filelist in os.walk(rootdir):
      for fileName in filelist:
          yield os.path.join(path, fileName)

'''Yields the next wave object'''
def generateFile(genNext):
    for fn in genNext:
      if fn.endswith('.wav') or fn.endswith('.txt'):
          yield fn

if __name__ == '__main__':
    iNum = 0
    for fFile in generateFile(generateNextFile(g.FINALOUT)):
        os.remove(fFile)
        iNum = iNum + 1
    for fFile in generateFile(generateNextFile(g.DBOUTPATH)):
        os.remove(fFile)
        iNum = iNum + 1
    for fFile in generateFile(generateNextFile(g.RECOMPPATH)):
        os.remove(fFile)
        iNum = iNum + 1
    if os.path.exists(g.LOGPATH):
        os.remove(g.LOGPATH)
        iNum = iNum + 1
    print(iNum)
