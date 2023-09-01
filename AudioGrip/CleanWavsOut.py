import os
import struct
import sys

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
    for fFile in generateFile(generateNextFile('G:\\Clip\\CDN-48kHz')):
        os.remove(fFile)
        iNum = iNum + 1
    for fFile in generateFile(generateNextFile('C:\\Users\\Peasant\\Desktop\\Process\\Batch')):
        os.remove(fFile)
        iNum = iNum + 1
    for fFile in generateFile(generateNextFile('C:\\Users\\Peasant\\Desktop\\Process\\ReComp')):
        os.remove(fFile)
        iNum = iNum + 1
    logPath = 'C:\\Users\\Peasant\\Desktop\\Process\\Controls\\Recomp.log'
    if os.path.exists(logPath):
        os.remove(logPath)
    print(iNum)
