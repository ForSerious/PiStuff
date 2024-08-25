import os
import sys
import globals as g
import StreamLine as sl


if __name__ == '__main__':
    if len(sys.argv) <= 1:
        print('Reading artists.')
        artistfile = open(g.FOLDERLISTPATH, 'r', -1, 'utf-8')
        artistlist = artistfile.readlines()
        dirs = []
        for artist in artistlist:
            if g.DEBUG:
                print(artist.strip())
            dirs.append(g.PREDIR + artist.strip())
        qTheStack = []
        for currentPath in dirs:
            print(repr(currentPath))
            for wFile in sl.generate_next_file(currentPath):
                print(repr(wFile))
                #print(convert_song(wFile))
                qTheStack.append(wFile)
        qTheStack = sorted(qTheStack, key=lambda x: sl.duration_compare(x), reverse=True)
        if g.DEBUG:
            for elem in qTheStack:
                print(elem)
        print('List loaded.')
        for thing in qTheStack:
            #print(repr(thing))
            print(sl.convert_song(thing))
        if os.path.exists(g.LOGPATH):
            os.startfile(g.LOGPATH)
    else:
        sl.convert_song(os.path.join(sys.argv[1]))
