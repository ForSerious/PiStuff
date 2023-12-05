import errno
import os
import re
import subprocess
import sys
import traceback
import json
from datetime import timedelta
from multiprocessing import Process, JoinableQueue
from time import time, strftime, localtime
from collections import deque


DEBUG = False
CRF = '22'
null = 'null'
FFMPEG = '"G:\\Program Files (x86)\\SVP 4\\utils\\ffmpeg.exe"'
TVAI = '"G:\\Program Files\\Topaz Labs LLC\\Topaz Video AI\\ffmpeg.exe"'
FFPROBE = '"G:\\Program Files (x86)\\SVP 4\\utils\\ffprobe.exe"'
MKVMERGE = '"G:\\Program Files\\MKVToolNix\\mkvmerge.exe"'
PREDIR = 'E:\\'
FOLDERS = 'E:\\Dump\\Directory list.txt'


def generate_next_file(rootdir):
    for path, dirlist, filelist in os.walk(rootdir):
        for fn in filelist:
            if '~' not in fn and (fn.endswith('.mkv') or fn.endswith('.mov') or fn.endswith('.mpg')):
                yield (path, fn)


def seconds_to_str(elapsed=None):
    if elapsed == None:
        return strftime("%Y-%m-%d %H:%M:%S", localtime())
    else:
        return str(timedelta(seconds=elapsed))[:-4]


def get_dar(the_way, ext):
    try:
        command = FFPROBE + ' -v error -show_entries stream=width,height,sa' \
                            'mple_aspect_ratio,display_aspect_ratio -select_streams v:0 -of default=noprint_wrappers=1 "' + \
                  os.path.join(the_way['-path'], the_way['-file'] + '.' + ext)
        dar = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    except:
        return traceback.format_exc()
    firstHeight = None
    firstWidth = None
    sar1 = None
    sar2 = None
    dar1 = None
    dar2 = None
    split_dar = re.split('\\n', dar.stdout)
    if DEBUG:
        print(split_dar)
    for item in split_dar:
        more_split = re.split('=', item)
        if more_split[0] == 'width':
            firstWidth = int(more_split[1])
        if more_split[0] == 'height':
            firstHeight = int(more_split[1])
        if more_split[0] == 'sample_aspect_ratio':
            moremore_split = re.split(':', more_split[1])
            sar1 = int(moremore_split[0])
            sar2 = int(moremore_split[1])
        if more_split[0] == 'display_aspect_ratio':
            moremore_split = re.split(':', more_split[1])
            dar1 = int(moremore_split[0])
            dar2 = int(moremore_split[1])
    width = int(firstWidth * sar1 / sar2)
    height = int(width / dar1 * dar2)
    return str(width), str(height)


def populate_options(file_path):
    ext = file_path[1][-3:]
    newpath = file_path[1][:-4]
    the_way = {}
    the_way['-path'] = file_path[0]
    the_way['-file'] = newpath
    the_way['-out'] = newpath
    dar = get_dar(the_way, ext)
    if DEBUG:
        print(dar)
    the_way['-w'] = dar[0]
    the_way['-h'] = dar[1]
    the_way['-ext'] = ext
    return the_way


def run_all_models(the_way):
    # Fill it out.
    return True


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
        itemcount = 0
        printcount = 1001
        bstart = time()
        OptionsStack = []
        AmountLoop = []
        for dude in qTheStack:
            option = populate_options(dude)
            if option is not None:
                option['-r'] = '23.976'
                run_all_models(option)
        end = time()
        print('Total time: ' + seconds_to_str(end - start))
    else:
        print('Sorry, not going to work.')
