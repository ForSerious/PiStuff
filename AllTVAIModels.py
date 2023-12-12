import errno
import os
import re
import subprocess
import sys
import traceback
from datetime import timedelta
from time import time, strftime, localtime


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


def populate_options(file_path, out_path):
    ext = file_path[1][-3:]
    newpath = file_path[1][:-4]
    the_way = {}
    the_way['-path'] = file_path[0]
    the_way['-file'] = newpath
    the_way['-out'] = out_path
    dar = get_dar(the_way, ext)
    if DEBUG:
        print(dar)
    the_way['-w'] = dar[0]
    the_way['-h'] = dar[1]
    the_way['-ext'] = ext
    return the_way


def get_ext(ext):
    if ext == 'png':
        return '\\%6d.png'
    else:
        return '.' + ext


def run_all_models(the_way):
    the_models = ['aaa-10', 'aaa-9', 'ahq-10', 'ahq-11', 'ahq-12', 'alq-10', 'alq-12', 'alq-13', 'alqs-1', 'alqs-2',
                  'amq-10', 'amq-12', 'amq-13', 'amqs-1', 'amqs-2', 'ddv-1', 'ddv-2', 'ddv-3', 'dtd-1', 'dtd-3',
                  'dtd-4', 'dtds-1', 'dtds-2', 'dtv-1', 'dtv-3', 'dtv-4', 'dtvs-1', 'dtvs-2', 'gcg-5', 'ghq-5',
                  'prap-2', 'prob-2', 'thd-3', 'thf-4']
    the_models = ['amq-13', 'ahq-12']
    for model in the_models:
        try:
            if not os.path.exists(os.path.join(the_way['-out'], the_way['-file'] + model)):
                os.mkdir(os.path.join(the_way['-out'], the_way['-file'] + model))
            if DEBUG:
                print('Making folder: ')
                print('"' + os.path.join(the_way['-file'] + model) + '"')
        except OSError as exc:
            if exc.errno != errno.EEXIST:
                raise
            pass
    for model in the_models:
        command = TVAI + ' -hide_banner -stats_period 2.0 -nostdin -y -i "'
        if model == 'prap-2' or model == 'prob-2' or model == 'thd-3' or model == 'thf-4':
            command = ''
        else:
            command = (command + os.path.join(the_way['-path'], the_way['-file'] + get_ext(the_way['-ext']))
            + '" -sws_flags spline+accurate_rnd+full_chroma_int -color_trc 1 -colorspace 1 -color_primaries 1 -r ' +
            the_way['-r'] + ' -ss ' + the_way['-ss'] + ' -filter_complex scale=w=' + the_way['-w'] + ':h=' + the_way['-h'] + ',setsar=1,tvai_up'
            '=model=' + model + ':scale=' + the_way['-scale'] + ':w=' + the_way['-w2'] + ':h=' + the_way['-h2'] + ':ble'
            'nd=' + the_way['-blend'] + ':device=0:vram=1:instances=1 -c:v png -pix_fmt rgb24 -frames:v 1 "' +
            os.path.join(the_way['-out'], the_way['-file'] + model) + '\\%6d.png"')
        if DEBUG:
            print('The Command: ')
            print(command)
        subprocess.call(command)
    return True


def set_scale(the_way):
    scale = float(the_way['-scale'])
    width = int(the_way['-w']) * scale
    height = int(the_way['-h']) * scale
    the_way['-w2'] = str(int((width + width) % 2))
    the_way['-h2'] = str(int((height + height) % 2))
    return the_way


if __name__ == '__main__':
    input_file_path = null
    output_file_path = null
    input_time_stamp = null
    input_scale = null
    input_rate = null
    if len(sys.argv) >= 1:
        sys.argv.reverse()
        while sys.argv.__len__() > 0:
            argument = sys.argv.pop()
            if argument == '-input':
                input_file_path = sys.argv.pop()
            if argument == '-output':
                output_file_path = sys.argv.pop()
            if argument == '-time':
                input_time_stamp = sys.argv.pop()
            if argument == '-scale':
                input_scale = sys.argv.pop()
            if argument == '-rate':
                input_rate = sys.argv.pop()
        print('input_file_path: ' + input_file_path)
        print('output_file_path: ' + output_file_path)
        print('input_time_stamp: ' + input_time_stamp)
        if input_file_path == null:
            print('-input needs a path to a video file')
            sys.exit(2)
        if output_file_path == null:
            print('-output needs a path')
            sys.exit(2)
        if input_time_stamp == null:
            print('-time was not set. Defaulting to time of 00:00:30.333')
            input_time_stamp = '00:00:30.333'
        if input_scale == null:
            print('-scale was not set. Defaulting to 2')
            input_scale = '2'
        if input_rate == null:
            print('-rate was not set. Defaulting to 23.976')
            input_rate = '23.976'
        start = time()
        if os.path.exists(input_file_path):
            dude = os.path.split(input_file_path)
            option = populate_options(dude, output_file_path)
            if option is not None:
                option['-r'] = input_rate
                option['-scale'] = input_scale
                option['-blend'] = '0.0'
                option['-ss'] = input_time_stamp
                option['-t'] = '0.0'
                option = set_scale(option)
                run_all_models(option)
            end = time()
            print('Total time: ' + seconds_to_str(end - start))
        else:
            print('File does not exist.')
    else:
        print('No input path.')
