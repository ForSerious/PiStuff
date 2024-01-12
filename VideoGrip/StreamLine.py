import os
import sys
import subprocess
import traceback
from multiprocessing import Process, JoinableQueue
from time import time, strftime, localtime
from datetime import timedelta

DEBUG = False
PROCESSES = 12
VIEW64 = '"C:\\Users\\Acolyte\\Desktop\\Graphs\\IrfanView\\i_view64.exe"'
LISTPATH = 'G:\\Vid\\FolderList.txt'

'''So, this should generate every file in the rootdir and return them one by one.'''
def generate_next_file(rootdir):
    for path, dirlist, filelist in os.walk(rootdir):
        for fn in filelist:
            if '~' not in fn and (fn.endswith('.jpg') or fn.endswith('.png')):
                yield os.path.join(path, fn)


'''Create the command to run ReComp'''
def reco_file(filepath):
    try:
        command = VIEW64 + ' "' + filepath + '" /resize=(1920,1080) /resample /convert="' + filepath + '"'
        if DEBUG:
            print('The Command: ')
            print(command)
        subprocess.call(command)
    except:
        return (False, traceback.format_exc())
    return (True, "done")


'''Create the command to run ReComp'''
def crop_file(filepath):
    try:
        command = VIEW64 + ' "' + filepath + '" /crop=(21,44,599,377,0) /convert="' + filepath + '"'
        if DEBUG:
            print('The Command: ')
            print(command)
        subprocess.call(command)
    except:
        return (False, traceback.format_exc())
    return (True, "done")


## Pull all the needed tags from the song to create the commands needed to convert.
def convert_song(file_path):
    if DEBUG:
        print(file_path)
    # output = reco_file(file_path)
    output = crop_file(file_path)
    if DEBUG:
        print('reco done: ' + output[1])
        # print(tags[0])
    return output


def runCity(q, out):
    while True:
        if q.empty():
            break
        out.put(convert_song(q.get()))
        q.task_done()
    return out


def secondsToStr(elapsed=None):
    if elapsed is None:
        return strftime("%Y-%m-%d %H:%M:%S", localtime())
    else:
        return str(timedelta(seconds=elapsed))


if __name__ == '__main__':
    if len(sys.argv) <= 1:
        start = time()
        print('Reading folders.')
        predir = 'D:\\'
        artistfile = open(LISTPATH, 'r', -1, 'utf-8')
        artistlist = artistfile.readlines()
        dirs = []
        for artist in artistlist:
            if DEBUG:
                print(artist.strip())
            dirs.append(predir + artist.strip())
        qTheStack = []
        for currentPath in dirs:
            for wFile in generate_next_file(currentPath):
                # print(repr(wFile))
                # print(convert_song(wFile))
                qTheStack.append(wFile)
        if DEBUG:
            for elem in qTheStack:
                print(elem)
        qInput = JoinableQueue()
        for path in qTheStack:
            qInput.put(path)
        print(str(len(qTheStack)) + ' Images loaded.')
        qOutput = JoinableQueue()
        for i in range(PROCESSES):
            worker = Process(target=runCity, args=(qInput, qOutput))
            worker.daemon = True
            worker.start()
        itemcount = 0
        printcount = 1001
        bstart = time()
        for blh in qTheStack:
            smite = str(itemcount)
            if len(smite) < 2:
                smite = '0' + smite
            deets = qOutput.get(True, 1200)
            if deets[0] != True:
                print(smite + ': ' + deets[1])
            printcount = printcount - 1
            if printcount == 0:
                bend = time()
                print(smite + ': ' + secondsToStr(bend - bstart))
                bstart = bend
                printcount = 1000
            itemcount = itemcount + 1
        qInput.join()
        end = time()
        print('Total time: ' + secondsToStr(end - start))
    else:
        convert_song(os.path.join(sys.argv[1]))
