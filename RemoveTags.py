import os
import re
import subprocess
import sys
import traceback
from datetime import timedelta
from time import time, strftime, localtime

DEBUG = False
null = 'null'
FFPROBE = '"C:\\Program Files\\MKVToolNix\\mkvinfo.exe"'
MKVMERGE = '"C:\\Program Files\\MKVToolNix\\mkvpropedit.exe"'
PREDIR = 'G:\\'
FOLDERS = 'D:\\TagRemovalList.txt'


def generate_next_file(rootdir):
    for path, dirlist, filelist in os.walk(rootdir):
        for fn in filelist:
            if '~' not in fn and (fn.endswith('.mkv')):
                yield (path, fn)


def seconds_to_str(elapsed=None):
    if elapsed == None:
        return strftime("%Y-%m-%d %H:%M:%S", localtime())
    else:
        return str(timedelta(seconds=elapsed))[:-4]


def get_dar(the_way):
    some_count = 0
    try:
        command = FFPROBE + ' "' + os.path.join(the_way[0], the_way[1]) + '"'
        if DEBUG:
            print(command)
        dar = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    except:
        return traceback.format_exc()
    split_dar = re.split('\\n', dar.stdout)
    if DEBUG:
        print(split_dar)
    firstWidth = None
    firstHeight = None
    for item in split_dar:
        more_split = re.split('\+', item)
        if len(more_split) > 1:
            if more_split[1] == ' Color matrix coefficients: 1':
                firstWidth = more_split[1]
            if more_split[1] == ' Color primaries: 1':
                firstHeight = more_split[1]
    if DEBUG:
        print(firstWidth)
        print(firstHeight)
    if firstWidth is not None and firstHeight is not None:
        editCommand = MKVMERGE + ' "' + os.path.join(the_way[0], the_way[1]) + ('" -e track:1 -d color-matrix-coeff'
                      'icients -d color-range -d color-transfer-characteristics -d color-primaries')
        if DEBUG:
            print(editCommand)
        try:
            some_count = some_count + 1
            subprocess.call(editCommand)
        except:
            return traceback.format_exc()
    return some_count



if __name__ == '__main__':
    if len(sys.argv) <= 1:
        start = time()
        some_other_count = 0
        print('Reading folders.')
        artistfile = open(FOLDERS, 'r', -1, 'utf-8')
        artistlist = artistfile.readlines()
        dirs = []
        for artist in artistlist:
            if DEBUG:
                print(artist.strip())
            dirs.append(PREDIR + artist.strip())
        qTheStack = []
        for currentPath in dirs:
            for wFile in generate_next_file(currentPath):
                qTheStack.append((wFile[0], wFile[1]))
        if DEBUG:
            for elem in qTheStack:
                print(elem)
        for dude in qTheStack:
            some_other_count = some_other_count + get_dar(dude)
        end = time()
        print('Total time: ' + seconds_to_str(end - start))
        if some_other_count > 1:
            print('Removed tags on ' + str(some_other_count) + ' movies.')
        if some_other_count == 0:
            print('Removed no tags from any movies.')
        if some_other_count == 1:
            print('Removed tags on ' + str(some_other_count) + ' movie.')
    else:
        print('Sorry, not going to work.')
