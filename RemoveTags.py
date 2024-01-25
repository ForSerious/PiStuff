import os
import re
import subprocess
import sys
import traceback
from datetime import timedelta
from time import time, strftime, localtime

DEBUG = True
null = 'null'
FFPROBE = '"G:\\Program Files (x86)\\SVP 4\\utils\\ffprobe.exe"'
MKVMERGE = '"G:\\Program Files\\MKVToolNix\\mkvpropedit.exe"'
PREDIR = 'E:\\'
FOLDERS = 'E:\\Dump\\The Bourne Supremacy\\theList.txt'


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
    try:
        command = FFPROBE + (' -v error -show_entries stream=color_range,color_space,color_transfer,color_primaries'
                             ' -select_streams v:0 -of default=noprint_wrappers=1 "') + \
                  os.path.join(the_way[0], the_way[1]) + '"'
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
        more_split = re.split('=', item)
        if more_split[0] == 'color_range':
            firstWidth = more_split[1]
        if more_split[0] == 'color_primaries':
            firstHeight = more_split[1]
    if DEBUG:
        print(firstWidth)
        print(firstHeight)
    if firstWidth != 'unknown' and firstHeight != 'unknown':
        editCommand = MKVMERGE + ' "' + os.path.join(the_way[0], the_way[1]) + ('" -e track:1 -d color-matrix-coefficients'
                      ' -d color-range -d color-transfer-characteristics -d color-primaries')
        if DEBUG:
            print(editCommand)
        try:
            print(editCommand)
            subprocess.call(editCommand)
        except:
            return traceback.format_exc()



if __name__ == '__main__':
    if len(sys.argv) <= 1:
        start = time()
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
            get_dar(dude)
        end = time()
        print('Total time: ' + seconds_to_str(end - start))
    else:
        print('Sorry, not going to work.')
