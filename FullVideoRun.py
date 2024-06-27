import errno
import os
import re
import subprocess
import traceback
import json
from datetime import timedelta
from multiprocessing import Process, JoinableQueue
from time import time, strftime, localtime
from collections import deque
from clrprint import clrprint

DEBUG = False
BETA = False
ALPHA = False
REMOVETAGS = True
CRF = '21'
null = 'null'
FFMPEG = '"C:\\Program Files (x86)\\SVP 4\\utils\\ffmpeg.exe"'
TVAI = '"G:\\Program Files\\Topaz Labs LLC\\Topaz Video AI\\ffmpeg.exe"'
if BETA:
    TVAI = '"H:\\Program Files\\Topaz Labs LLC\\Topaz Video AI BETA\\ffmpeg.exe"'
if ALPHA:
    TVAI = '"H:\\Program Files\\Topaz Labs LLC\\Topaz Video AI ALPHA\\ffmpeg.exe"'
FFPROBE = '"C:\\Program Files (x86)\\SVP 4\\utils\\ffprobe.exe"'
MKVMERGE = '"C:\\Program Files\\MKVToolNix\\mkvmerge.exe"'
MKVEDIT = '"C:\\Program Files\\MKVToolNix\\mkvpropedit.exe"'
# Cut and frame rate correction processes
FFNUM = 3
# How many TVAI instances
TVAINUM = 1
# How many TVAI APO instances
APONUM = 1
PREDIR = 'D:\\'
FOLDERS = 'C:\\PiStuff\\FullRunList.txt'
OTHER_DRIVE = 'S:\\'
LINEAR = True
SORT = False


def generate_next_file(rootdir):
    for path, dirlist, filelist in os.walk(rootdir):
        for fn in filelist:
            if '~' not in fn and (fn.endswith('.mkv') or fn.endswith('.mov') or fn.endswith('.mpg')):
                yield (path, fn)


def generate_next_image(rootdir):
    for path, dirlist, filelist in os.walk(rootdir):
        for fn in filelist:
            if fn.endswith('.jpg') or fn.endswith('.tif') or fn.endswith('.png'):
                yield os.path.join(path, fn)


def seconds_to_str(elapsed=None):
    if elapsed is None:
        return strftime("%Y-%m-%d %H:%M:%S", localtime())
    else:
        return str(timedelta(seconds=elapsed))[:-4]


def get_ext(ext):
    if ext == 'tif':
        return '\\%6d.tif'
    else:
        return '.' + ext


def ff_pass(filepath):
    ff_start = time()
    ss = ''
    t = ''
    r = ''
    part = ' ff'
    dering = ''
    decimate_tmp = ''
    if filepath.get('-decimate', null) != null:
        decimate_tmp = filepath['-decimate']
    if filepath.get('-ss', null) != null or filepath.get('-ss2', null) != null:
        if filepath.get('-pass2', null) and filepath.get('-ss2', null) != null:
            ss = '-ss ' + filepath['-ss2'] + ' '
            part = ' pt2 ff'
            if filepath.get('-decimate2', null) != null:
                decimate_tmp = filepath['-decimate2']
        else:
            if filepath.get('-ss', null) != null:
                ss = '-ss ' + filepath['-ss'] + ' '
            if filepath.get('-pt2', null) != null:
                part = ' pt1 ff'
    if filepath.get('-t', null) != null:
        if filepath.get('-pass2', null) and filepath.get('-t2', null) != null:
            t = '-t ' + filepath['-t2'] + ' '
            part = ' pt2 ff'
            if filepath.get('-decimate2', null) != null:
                decimate_tmp = filepath['-decimate2']
        else:
            t = '-t ' + filepath['-t'] + ' '
            if filepath.get('-pt2', null) != null:
                part = ' pt1 ff'
    if filepath.get('-r', null) != null:
        r = '-r ' + filepath['-r'] + ' '
    out_path = (get_drive_path(filepath['-path'], filepath, False), filepath['-file'] + part)
    filepath['-out'] = out_path[1]
    try:
        run_three = False
        now_tif = False
        decimate = ''
        if filepath.get('-decimate', null) != null:
            # WWWW WWWW WWWW WWWW WWWW WXWWW WWWW WXWWW WWWXW WWWW WWWWX WXWWW
            decimate = '-vf "decimate=cycle=5" '
        if filepath.get('-vpy', null) != null and filepath.get('-deinterlace', null) != null:
            decimate = '-r ' + filepath['-r'] + ' ' + decimate
            if filepath.get('-nnedi3', null) != null or filepath.get('-nnedi3cl', null) != null:
                generate_nnedi3_vpy(filepath, filepath['-file'])
            else:
                generate_vpy(filepath, filepath['-file'])
            command = (FFMPEG + ' -hide_banner -stats_period 2.0 -nostdin -f vapoursynth -i "' +
                str(os.path.join(get_drive_path(filepath['-path'], filepath, True), filepath['-file'] + '.vpy')) +
                '" -y ' + ss + t + '-map 0:v:0 ' + decimate + '-c:v libx265 -crf'
                ' 12 -preset veryfast "' + str(os.path.join(get_drive_path(out_path[0], filepath, False), out_path[1] +
                '.mkv')) + '"')
        if filepath.get('-vpy', null) == null and filepath.get('-deinterlace', null) != null:
            if filepath.get('-bob', null) == null and filepath.get('-decimate', null) != null:
                decimate = ',decimate=cycle=2' + decimate_tmp + ' '
            else:
                decimate = decimate_tmp + ' '
            command = (FFMPEG + ' -hide_banner -stats_period 2.0 -nostdin -y -i "' + str(os.path.join(get_drive_path(
                filepath['-path'], filepath, True), filepath['-file'] + '.' + filepath['-ext'])) + '" ' + ss + t +
                '-r ' + filepath['-r'] + ' -map 0:v:0 -filter_complex setsar=1,bwdif=mode=1:parity=-1:deint=0' + decimate +
                '-c:v libx265 -crf 12 -preset veryfast "' + str(os.path.join(get_drive_path(out_path[0], filepath,
                False), out_path[1] + '.mkv')) + '"')
        if filepath.get('-deinterlace', null) == null:
            command = (FFMPEG + ' -hide_banner -stats_period 2.0 -nostdin -i "' + str(os.path.join(get_drive_path(
                filepath['-path'], filepath, True), filepath['-file'] + '.' + filepath['-ext'])) + '" -y ' + ss +
                t + '-map 0:v:0 ' + r + dering + '-c:v libx265 -crf 12'
                ' -preset veryfast -c:a copy -c:s copy -max_muxing_queue_size 4096 "' + str(os.path.join(get_drive_path(
                out_path[0], filepath, False), out_path[1] + '.mkv') + '"'))
            if filepath.get('-vpy', null) != null or filepath.get('-dfttest', null) != null or filepath.get('-neovd', null) != null:
                generate_vpy(filepath, out_path[1])
                run_three = True
                command3 = (FFMPEG + ' -hide_banner -stats_period 2.0 -nostdin -f vapoursynth -i "' + str(os.path.join(
                    get_drive_path(filepath['-path'], filepath, True), out_path[1] + '.vpy')) + '" -y -map 0:v:0 '
                    + r + decimate + '-c:v libx265 -crf 12 -preset veryfast "' + str(os.path.join(
                    get_drive_path(out_path[0], filepath, False), out_path[1] + 'vpy' + '.mkv') + '"'))
                out_path = (filepath['-path'], out_path[1] + 'vpy')
                filepath['-out'] = out_path[1]
        if filepath.get('-name', null) != null:
            if filepath.get('-pt2', null) != null:
                name = filepath['-name'] + part[:-3]
            else:
                name = filepath['-name']
        else:
            name = out_path[1]
        command2 = (FFMPEG + ' -hide_banner -stats_period 2.0 -nostdin -i "' + filepath['-originpath'] + '" -y ' +
            ss + t + '-map 0:v:0 -map 0:a? -map 0:s? -map 0:d? -map 0:t? ' + r + '-vn -c:a copy -c:s copy -c:d copy "' +
            str(os.path.join(get_drive_path(out_path[0], filepath, False), name + '.mka')) + '"')
        filepath['-mkapath'] = os.path.join(get_drive_path(out_path[0], filepath, False), name + '.mka')
        filepath['-mkaname'] = name
        if DEBUG:
            print('The Command: ')
            print(command)
            print('The Command2: ')
            print(command2)
        if get_json_state(filepath).get('mka', null) == null:
            subprocess.call(command2)
            save_json_state(filepath, 'mka')
        if get_json_state(filepath).get('ff1', null) == null:
            subprocess.call(command)
            save_json_state(filepath, 'ff1')
            if filepath.get('-vpy', null) != null:
                filepath = swap_drive_path(filepath)
        if run_three and get_json_state(filepath).get('ff2', null) == null:
            if DEBUG:
                print('The Command3: ')
                print(command3)
            subprocess.call(command3)
            save_json_state(filepath, 'ff2')
        filepath['-ext'] = 'mkv'
        if now_tif:
            filepath['-ext'] = 'tif'
            filepath['-folders'].append(os.path.join(get_drive_path(out_path[0], filepath, False), out_path[1]))
    except:
        return None
    ff_end = time()
    the_name = filepath['-out']
    if filepath.get('-name', null) != null:
        the_name = filepath['-name']
    filepath['-took'] = the_name + 'time:' + seconds_to_str(ff_end - ff_start)
    filepath['-sort'] = ff_end - ff_start
    filepath['-runtot'] = filepath['-sort']
    if filepath.get('-vpy', null) != null:
        filepath = swap_drive_path(filepath)
    return swap_drive_path(filepath)


def amq_pass(filepath, filename):
    ff_start = time()
    debuglog = ''
    if DEBUG:
        debuglog = ' -report'
    out_path = (filepath['-path'], filename + 'amq')
    filepath['-out'] = out_path[1]
    filepath['-folders'].append(os.path.join(get_drive_path(filepath['-path'], filepath, False), out_path[1]))
    try:
        if not os.path.exists(os.path.join(get_drive_path(filepath['-path'], filepath, False), filepath['-out'])):
            os.mkdir(os.path.join(get_drive_path(filepath['-path'], filepath, False), filepath['-out']))
        if DEBUG:
            print('The Make Folder: ')
            print('"' + os.path.join(get_drive_path(filepath['-path'], filepath, False), filepath['-out']) + '"')
    except OSError as exc:
        if exc.errno != errno.EEXIST:
            raise
        pass
    sar = get_sar_things(filepath)
    blend = '0'
    if filepath.get('-blend', 'null') != null:
        blend = filepath['-blend']
    if filepath.get('-theia', null) != null:
        t_noise = filepath.get('-tnoise', '-0.39')
        t_blur = filepath.get('-tblur', '0.0')
        t_comp = filepath.get('-tcomp', '0.33')
        command = (TVAI + ' -hide_banner -stats_period 2.0 -nostdin -y -i "' +
                  os.path.join(get_drive_path(filepath['-path'], filepath, True), filename +
                  get_ext(filepath['-ext'])) + '" -r ' + filepath['-r'] + debuglog + ' -filter_complex ' + sar[1] +
                  'tvai_up=model=thf-4:scale=1.0:w=' + filepath['-w'] + ':h=' + filepath['-h'] +
                  ':noise=' + t_noise + ':blur=' + t_blur + ':compression=' + t_comp + ':device=0:vram=1:instances=1'
                  ' -c:v tiff -compression_algo deflate "' +
                  os.path.join(get_drive_path(out_path[0], filepath, False), out_path[1]) + '\\%6d.tif"')
    elif filepath.get('-nyx', null) != null:
        n_version = filepath.get('-nyxver', '1')
        if n_version == '2':
            n_version = 'nyx-2'
        if n_version == '1':
            n_version = 'nyx-1'
        if n_version == '3':
            n_version = 'nxf-1'
        if n_version == '4':
            n_version = 'nyx-3'
        n_comp = filepath.get('-nyxcomp', '0')
        n_details = filepath.get('-nyxdetails', '0')
        n_blur = filepath.get('-nyxblur', '0')
        n_noise = filepath.get('-nyxnoise', '0.1')
        n_halo = filepath.get('-nyxhalo', '0')
        n_preblur = filepath.get('-nyxpreblur', '0')
        n_blend = filepath.get('-nyxblend', '0')
        n_auto = ''
        if filepath.get('-nyxauto', null) != null:
            n_auto = ':estimate=8'
        command = (TVAI + ' -hide_banner -stats_period 2.0 -nostdin -y -i "' +
                  os.path.join(get_drive_path(filepath['-path'], filepath, True), filename +
                  get_ext(filepath['-ext'])) + '" -r ' + filepath['-r'] + debuglog + ' -filter_complex ' + sar[1] +
                  'tvai_up=model=' + n_version + ':scale=1:preblur=' + n_preblur + ':noise=' + n_noise +
                  ':details=' + n_details + ':halo=' + n_halo + ':blur=' + n_blur + ':compression=' + n_comp +
                  ':blend=' + n_blend + n_auto + ':device=0:vram=1:instances=1 -c:v tiff -compression_algo deflate "' +
                  os.path.join(get_drive_path(out_path[0], filepath, False), out_path[1]) + '\\%6d.tif"')
    else:
        am = 'amq-13'
        if filepath.get('-high', null) != null:
            am = 'ahq-12'
        command = (TVAI + ' -hide_banner -stats_period 2.0 -nostdin -y -i "' +
                  os.path.join(get_drive_path(filepath['-path'], filepath, True), filename +
                  get_ext(filepath['-ext'])) + '" -r ' + filepath['-r'] + debuglog + ' -filter_complex ' + sar[1] +
                  'tvai_up=model=' + am + ':scale=1.0:w=' + filepath['-w'] + ':h=' + filepath['-h'] + ':blend=' +
                  blend + ':device=0:vram=1:instances=1 -c:v tiff -compression_algo deflate "' +
                  os.path.join(get_drive_path(out_path[0], filepath, False), out_path[1]) + '\\%6d.tif"')
    try:
        if DEBUG:
            print('The Command: ')
            print(command)
        if get_json_state(filepath).get('amq', null) == null:
            env_run_command(filepath, command, out_path[1])
            save_json_state(filepath, 'amq')
        filepath['-ext'] = 'tif'
        if filepath.get('-clean', null) != null:
            clean_images(filepath)
            remove_some_file(filepath, filename)
    except:
        filepath['-took'] = traceback.format_exc()
        return filepath
    ff_end = time()
    the_name = filepath['-out']
    if filepath.get('-name', null) != null:
        the_name = filepath['-name']
    filepath['-took'] = the_name + 'time:' + seconds_to_str(ff_end - ff_start)
    filepath['-sort'] = ff_end - ff_start
    if filepath.get('-runtot', None) is not None:
        filepath['-runtot'] = filepath['-runtot'] + filepath['-sort']
    else:
        filepath['-runtot'] = filepath['-sort']
    return swap_drive_path(filepath)


def apo_pass(filepath, filename):
    ff_start = time()
    out_path = (filepath['-path'], filename + 'apo')
    filepath['-out'] = out_path[1]
    filepath['-folders'].append(os.path.join(get_drive_path(filepath['-path'], filepath, False), out_path[1]))
    try:
        if not os.path.exists(os.path.join(get_drive_path(filepath['-path'], filepath, False), filepath['-out'])):
            os.mkdir(os.path.join(get_drive_path(filepath['-path'], filepath, False), filepath['-out']))
        if DEBUG:
            print('The Make Folder: ')
            print('"' + os.path.join(get_drive_path(filepath['-path'], filepath, False), filepath['-out']) + '"')
    except OSError as exc:
        if exc.errno != errno.EEXIST:
            raise
        pass
    frame = ''
    if filepath['-ext'] == 'tif':
        frame = ' -framerate ' + filepath['-r']
    model = 'apo-8'
    if filepath.get('-chr', null) != null:
        model = 'chr-2'
    if filepath.get('-chf', null) != null:
        model = 'chf-3'
    if filepath.get('-apf', null) != null:
        model = 'apf-1'
    if filepath.get('-aion', null) != null:
        model = 'aion-1'
    debuglog = ''
    if DEBUG:
        debuglog = ' -report'
    try:
        command = (TVAI + ' -hide_banner -stats_period 2.0 -nostdin'
                 + debuglog + frame + ' -y -i "' + os.path.join(get_drive_path(filepath['-path'], filepath, True),
                 filename + get_ext(filepath['-ext'])) + '" -filter_complex tvai_fi=model=' + model + ':slowmo=2.5:'
                 'rdt=0.000001:device=0:vram=1:instances=0 -c:v tiff -compression_algo deflate "' +
                   os.path.join(get_drive_path(out_path[0], filepath, False), out_path[1]) + '\\%6d.tif"')
        if DEBUG:
            print('The Command: ')
            print(command)
        if get_json_state(filepath).get('apo', null) == null:
            env_run_command(filepath, command, out_path[1])
            save_json_state(filepath, 'apo')
        filepath['-ext'] = 'tif'
        if filepath.get('-clean', null) != null:
            clean_images(filepath)
            remove_some_file(filepath, filename)
    except:
        filepath['-took'] = traceback.format_exc()
        return filepath
    ff_end = time()
    the_name = filepath['-out']
    if filepath.get('-name', null) != null:
        the_name = filepath['-name']
    filepath['-took'] = the_name + 'time:' + seconds_to_str(ff_end - ff_start)
    filepath['-sort'] = ff_end - ff_start
    if filepath.get('-runtot', None) is not None:
        filepath['-runtot'] = filepath['-runtot'] + filepath['-sort']
    else:
        filepath['-runtot'] = filepath['-sort']
    return swap_drive_path(filepath)


def get_r(filepath):
    if (filepath.get('-apo', null) != null or filepath.get('-apf', null) != null or filepath.get('-chr', null) != null
            or filepath.get('-chf', null) != null or filepath.get('-aion', null) != null):
        if filepath['-r'] == '23.976' or filepath['-r'] == '24':
            val = (float(filepath['-r']) * 2.5)
        else:
            val = (float(filepath['-r']) * 2)
    else:
        val = filepath['-r']
    return ' -r ' + str(val)


def ahq_pass(filepath, filename):
    ff_start = time()
    debuglog = ''
    if DEBUG:
        debuglog = ' -report'
    out_path = (filepath['-path'], filename + 'ahq')
    filepath['-out'] = out_path[1]
    filepath['-folders'].append(os.path.join(get_drive_path(filepath['-path'], filepath, False), filepath['-out']))
    try:
        if not os.path.exists(os.path.join(get_drive_path(filepath['-path'], filepath, False), filepath['-out'])):
            os.mkdir(os.path.join(get_drive_path(filepath['-path'], filepath, False), filepath['-out']))
        if DEBUG:
            print('The Make Folder: ')
            print('"' + os.path.join(get_drive_path(filepath['-path'], filepath, False), filepath['-out']) + '"')
    except OSError as exc:
        if exc.errno != errno.EEXIST:
            raise
        pass
    model = 'ahq-12'
    if filepath.get('-med', 'null') != null:
        model = 'amq-13'
    sar = get_sar_things(filepath)
    scale = sar[2]
    if filepath.get('-gaia', 'null') != null:
        scale = '0'
        model = 'ghq-5'
    blend = '0'
    if filepath.get('-blend', 'null') != null:
        blend = filepath['-blend']
    command = (TVAI + ' -hide_banner -stats_period 2.0 -nostdin -y -i "'
              + os.path.join(get_drive_path(filepath['-path'], filepath, True), filename +
              get_ext(filepath['-ext'])) + '"' + debuglog + ' -filter_complex ' + sar[1] + 'tvai_up=model=' + model +
              ':scale=' + scale + ':w=1920:h=1080:blend=' + blend + ':device=0:vram=1:instances=1' + sar[0] + ',scal'
              'e=w=1920:h=1080:flags=lanczos:threads=0:force_original_aspect_ratio=decrease,pad=1920:1080:-1:-1:color'
              '=black -c:v tiff -compression_algo deflate "' + os.path.join(get_drive_path(out_path[0],
              filepath, False), out_path[1]) + '\\%6d.tif"')
    try:
        if DEBUG:
            print('The Command: ')
            print(command)
        if get_json_state(filepath).get('ahq', null) == null:
            env_run_command(filepath, command, out_path[1])
            save_json_state(filepath, 'ahq')
        filepath['-ext'] = 'tif'
        if filepath.get('-clean', null) != null:
            clean_images(filepath)
            remove_some_file(filepath, filename)
    except:
        filepath['-took'] = traceback.format_exc()
        return filepath
    ff_end = time()
    the_name = filepath['-out']
    if filepath.get('-name', null) != null:
        the_name = filepath['-name']
    filepath['-took'] = the_name + 'time:' + seconds_to_str(ff_end - ff_start)
    if filepath.get('-runtot', None) is not None:
        filepath['-runtot'] = filepath['-runtot'] + (ff_end - ff_start)
    else:
        filepath['-runtot'] = (ff_end - ff_start)
    return swap_drive_path(filepath)


def prot_pass(filepath, filename):
    ff_start = time()
    debuglog = ''
    if DEBUG:
        debuglog = ' -report'
    fext = get_ext(filepath['-ext'])
    filt = ''
    if filepath['-ext'] != 'tif':
        filt = ' -sws_flags spline+accurate_rnd+full_chroma_int'
        filt = ''
    out_path = (filepath['-path'], filename + 'prot')
    filepath['-out'] = out_path[1]
    filepath['-folders'].append(os.path.join(get_drive_path(filepath['-path'], filepath, False), out_path[1]))
    try:
        if not os.path.exists(os.path.join(get_drive_path(filepath['-path'], filepath, False), out_path[1])):
            os.mkdir(os.path.join(get_drive_path(filepath['-path'], filepath, False), out_path[1]))
        if DEBUG:
            print('Prot Make Folder: ')
            print(os.path.join(get_drive_path(filepath['-path'], filepath, False), out_path[1]))
    except OSError as exc:
        if exc.errno != errno.EEXIST:
            raise
        pass
    sarparams = get_sar_things(filepath)
    sarscale = sarparams[0]
    squareratio = sarparams[1]
    scale = sarparams[2]
    theModel = 'prob-3'
    if filepath.get('-iris', 'null') != null:
        theModel = 'iris-1'
    if filepath.get('-protver', 'null') == '4':
        theModel = 'prob-4'
    blend = '0.0'
    if filepath.get('-blend', 'null') != null:
        blend = filepath['-blend']
    if filepath.get('-scale', 'null') != null:
        scale = filepath['-scale']
    if filepath.get('-auto', 'null') != null:
        command = (TVAI + ' -hide_banner -stats_period 2.0 -nostdin -y -thread_queue_size 4096 -i "'
                  + os.path.join(get_drive_path(filepath['-path'], filepath, True), filename + fext) + '"' +
                   filt + debuglog + ' -filter_complex ' + squareratio + 'tvai_up=model=' + theModel + ':scale=' + scale + ':w=0:h=0:preblur='
                  '0:noise=0:details=0:halo=0:blur=0:compression=0:estimate=8:blend=' + blend + ':device=0:vram=1:instances=1' + sarscale + ',scale=w=1920:h=1'
                  '080:flags=lanczos:threads=0:force_original_aspect_ratio=decrease,pad=1920:1080:-1:-1:color'
                  '=black -c:v tiff -compression_algo deflate "' + os.path.join(get_drive_path(out_path[0], filepath, False), out_path[1]) + '\\%6d.tif"')
    else:
        prot_preblur = '-0.06'
        prot_noise = '0'
        prot_details = '0.09'
        prot_halo = '0.06'
        prot_blur = '0.10'
        prot_compression = '0.5'
        prot_r_t_a = ''
        if filepath.get('-protcompression', 'null') != null:
            prot_compression = filepath['-protcompression']
        if filepath.get('-protdetails', 'null') != null:
            prot_details = filepath['-protdetails']
        if filepath.get('-protblur', 'null') != null:
            prot_blur = filepath['-protblur']
        if filepath.get('-protnoise', 'null') != null:
            prot_noise = filepath['-protnoise']
        if filepath.get('-prothalo', 'null') != null:
            prot_halo = filepath['-prothalo']
        if filepath.get('-protpreblur', 'null') != null:
            prot_preblur = filepath['-protpreblur']
        if filepath.get('-protrta', 'null') != null or filepath.get('-protauto', 'null') != null:
            prot_r_t_a = ':estimate=8'
        command = (TVAI + ' -hide_banner -stats_period 2.0 -nostdin -y -i "'
                  + os.path.join(get_drive_path(filepath['-path'], filepath, True), filename + fext) + '"' +
                   filt + ' -filter_complex ' + squareratio + 'tvai_up=model=' + theModel + ':scale=' + scale + ':w=1920:h=1080:prebl'
                  'ur=' + prot_preblur + ':noise=' + prot_noise + ':details=' + prot_details + ':halo=' + prot_halo + ':blur=' +
                  prot_blur + ':compression=' + prot_compression + prot_r_t_a + ':blend=' + blend + ':device=0:vram=1:instances=1' + sarscale + ',scale='
                  'w=1920:h=1080:flags=lanczos:threads=0:force_original_aspect_ratio=decrease,pad=1920:1080:-1:-1:color'
                  '=black -c:v tiff -compression_algo deflate "' + os.path.join(get_drive_path(out_path[0], filepath, False), out_path[1]) + '\\%6d.tif"')
    try:
        if DEBUG:
            print('The Command: ')
            print(command)
        if get_json_state(filepath).get('prot', null) == null:
            env_run_command(filepath, command, out_path[1])
            save_json_state(filepath, 'prot')
        filepath['-ext'] = 'tif'
        if filepath.get('-clean', null) != null:
            clean_images(filepath)
            remove_some_file(filepath, filename)
    except:
        filepath['-took'] = traceback.format_exc()
        return filepath
    ff_end = time()
    the_name = filepath['-out']
    if filepath.get('-name', null) != null:
        the_name = filepath['-name']
    filepath['-took'] = the_name + 'time:' + seconds_to_str(ff_end - ff_start)
    if filepath.get('-runtot', None) is not None:
        filepath['-runtot'] = filepath['-runtot'] + (ff_end - ff_start)
    else:
        filepath['-runtot'] = (ff_end - ff_start)
    return swap_drive_path(filepath)


def final_pass(filepath, filename):
    part = ' AI'
    if filepath.get('-ss', null) != null and filepath.get('-pt2', null) != null:
        if filepath.get('-pass2', null) and filepath['-ss2'] != null:
            part = ' pt2 AI'
        else:
            part = ' pt1 AI'
    if filepath.get('-t', null) != null and filepath.get('-pt2', null) != null:
        if filepath.get('-pass2', null) and filepath.get('-t2', null) != null:
            part = ' pt2 AI'
        else:
            part = ' pt1 AI'
    name = filepath['-file']
    if filepath.get('-name', null) != null:
        name = filepath['-name']
    out_path = (filepath['-path'], name + part)
    color_specs = 'p=709:t=601:m=709:r=tv:c=left'
    if filepath.get('-hd', null) != null or filepath.get('-bluray', null) != null:
        color_specs = 'p=709:t=601:m=470bg:r=tv:c=left'
    try:
        command = (FFMPEG + ' -hide_banner -stats_period 2.0 -nostdin -framerate ' + (get_r(filepath)[4:]) + ' -y -i "' +
             os.path.join(get_drive_path(filepath['-path'], filepath, True), filename + get_ext(filepath['-ext'])) +
             '" -c:v libx265 -crf ' + CRF + ' -pix_fmt yuv420p -preset slow -x265-params aq-mode=3 -sws_flags spline'
             '+accurate_rnd+full_chroma_int -vf "zscale=pin=bt709:min=gbr:tin=bt709:rin=pc:agamma=false:d=error_diffu'
             'sion:' + color_specs + ',format=yuv420p" -color_range tv "' + os.path.join(get_drive_path(out_path[0],
             filepath, False), out_path[1] + '.mkv') + '"')
        if filepath['-ext'] != 'tif':
            command = FFMPEG + ' -hide_banner -stats_period 2.0 -nostdin -y -i "' + \
                      os.path.join(filepath['-path'], filename + get_ext(filepath['-ext'])) + '" -an -sn -map_chapters -1 -c:v libx265 -crf ' \
                      + CRF + ' -preset slow -x265-params aq-mode=3 "' + os.path.join(out_path[0], out_path[1] + '.mkv') + '"'
        if DEBUG:
            print('The Command: ')
            print(command)
        if get_json_state(filepath).get('final', null) == null:
            subprocess.call(command)
            save_json_state(filepath, 'final')
        if filepath.get('-mergecommand', null) != null:
            merge_command = make_merge_command(filepath, out_path[1])
            if DEBUG:
                print('Merge command: ')
                print(merge_command)
            if get_json_state(filepath).get('merge', null) == null:
                subprocess.call(merge_command)
                save_json_state(filepath, 'merge')
            if filepath.get('-name', null) != null:
                name = filepath['-name']
            else:
                name = filepath['-file']
            if filepath.get('-cleanmerge', null) != null:
                if os.path.exists(os.path.join(get_drive_path(out_path[0], filepath, False), out_path[1] +
                '.mkv')) and filepath['-originpath'] != os.path.join(get_drive_path(out_path[0], filepath, False),
                out_path[1]) + '.mkv':
                    os.remove(os.path.join(get_drive_path(out_path[0], filepath, False), out_path[1] + '.mkv'))
                if (filepath.get('-pt2', null) != null and os.path.exists(filepath['-mkapath']) and
                filepath['-originpath'] != filepath['-mkapath']):
                    os.remove(filepath['-mkapath'])
                elif os.path.exists(filepath['-mkapath']) and filepath['-originpath'] != filepath['-mkapath']:
                    os.remove(filepath['-mkapath'])
            if filepath.get('-appendcommand', null) != null:
                if os.path.exists(os.path.join(get_drive_path(out_path[0], filepath, False), name +
                ' pt1 AI1.mkv')) and os.path.exists(os.path.join(get_drive_path(out_path[0], filepath, False),
                name + ' pt2 AI1.mkv')):
                    append_command = make_append_command(filepath)
                    if DEBUG:
                        print('Append command: ')
                        print(append_command)
                    if get_json_state(filepath).get('append', null) == null:
                        subprocess.call(append_command)
                        save_json_state(filepath, 'append')
                    if filepath.get('-cleanmerge', null) != null:
                        os.remove(os.path.join(get_drive_path(out_path[0], filepath, False), name + ' pt1 AI1.mkv'))
                        os.remove(os.path.join(get_drive_path(out_path[0], filepath, False), name + ' pt2 AI1.mkv'))
        if REMOVETAGS:
            editCommand = MKVEDIT + ' "' + os.path.join(out_path[0], filepath['-name'] + '.mkv') + ('" -e track:1 -d color-ma'
                          'trix-coefficients -d color-range -d color-transfer-characteristics -d color-primaries')
            subprocess.call(editCommand)
    except:
        return (False, traceback.format_exc())
    if filepath.get('-clean', null) != null:
        pt2 = ''
        if filepath['-pass2']:
            pt2 = 'pt2'
        if os.path.exists(os.path.join(filepath['-path'], filepath['-file'] + pt2 + '_run.json')):
            if not LINEAR:
                os.remove(os.path.join(filepath['-path'], filepath['-file'] + pt2 + '_run.json'))
            else:
                filepath['jsonRun'] = os.path.join(filepath['-path'], filepath['-file'] + pt2 + '_run.json')
        remove_some_file(filepath, filepath['-file'] + pt2 + 'ff')
    return (True, out_path[1])


def get_sar_things(filepath):
    scale = '2.25'
    sarscale = ',scale=w=' + filepath['-wx2'] + ':h=' + filepath['-hx2'] + ',setsar=1'
    squareratio = ''
    dosquare = False
    if not filepath['square']:
        squareratio = 'scale=w=' + filepath['-w'] + ':h=' + filepath['-h'] + ',setsar=1,'
        sarscale = ''
        dosquare = True
    if filepath.get('-hd', 'null') != null:
        scale = '1'
        sarscale = ''
    if filepath.get('squareDone', False):
        squareratio = ''
    if dosquare:
        filepath['squareDone'] = True
    return sarscale, squareratio, scale


def clean_images(file_path, final=False):
    if file_path.get('-clean', null) != null and (len(file_path['-folders']) > 1 or final is True):
        if len(file_path['-folders']) >= 1:
            del_start = time()
            i_num = 0
            the_dir = file_path['-folders'].popleft()
            for fFile in generate_next_image(the_dir):
                os.remove(fFile)
                i_num = i_num + 1
            os.rmdir(the_dir)
            del_end = time()
            clrprint('Removed', str(i_num), 'images.', clr='d,b,d')
            the_name = get_name(file_path)
            clrprint(the_name, 'del time:', seconds_to_str(del_end - del_start), clr='y,d,b')
            if len(file_path['-folders']) > 0 and final is True:
                clean_images(file_path, True)


def read_options(optionslist):
    options = {}
    for option in optionslist:
        halves = option.split(' ')
        options[halves[0]] = halves[1].strip()
    return options


def get_name(file_path):
    the_name = file_path['-file']
    if file_path.get('-name', null) != null:
        the_name = file_path['-name']
    return the_name


def convert_song(file_path):
    if DEBUG:
        print(file_path)
    totstart = time()
    output = (True, file_path['-out'])
    the_name = get_name(file_path)
    if file_path.get('-fin', null) != null:
        finstart = time()
        output = final_pass(file_path, output[1])
        finend = time()
        clrprint(the_name, 'fin time:', seconds_to_str(finend - finstart), clr='y,d,b')
    if DEBUG:
        print('Fin output: ' + output[1])
    clean_images(file_path, True)
    totend = time()
    clrprint('Total', the_name, 'time:', seconds_to_str(file_path.get('-runtot', 0.0) + (totend - totstart)) + '\n', clr='g,y,g,b')
    return output


def populate_options(file_path):
    ext = file_path[1][-3:]
    newpath = file_path[1][:-4]
    if os.path.exists(os.path.join(file_path[0], newpath + '.json')):
        clrprint('Populating:', newpath, clr='d,y')
        run_file = open(os.path.join(file_path[0], newpath + '.json'), 'r')
        the_way = json.load(run_file)
    elif os.path.exists(os.path.join(file_path[0], newpath + '.txt')):
        clrprint('Populating:', newpath, clr='d,y')
        optionsFile = open(os.path.join(file_path[0], newpath + '.txt'), 'r', -1, 'utf-8')
        optionslist = optionsFile.readlines()
        the_way = read_options(optionslist)
        outfile = open(os.path.join(file_path[0], newpath + '.json'), 'w')
        json.dump(the_way, outfile, indent=2)
    else:
        return None
    the_way['-path'] = file_path[0]
    the_way['-file'] = newpath
    the_way['-pass2'] = False
    the_way['-out'] = newpath
    the_way['-folders'] = deque()
    the_way['toDrive'] = OTHER_DRIVE
    the_way['fromDrive'] = PREDIR
    the_way = get_dar(the_way, ext)
    the_way['-ext'] = ext
    if the_way.get('-name', null) != null:
        the_way['-name'] = the_way['-name'].replace('_', ' ')
    else:
        the_way['-name'] = the_way['-file'] + ' AI'
    if the_way.get('-crf', null) != null:
        global CRF
        CRF = the_way['-crf']
    the_way['-originpath'] = os.path.join(file_path[0], file_path[1])
    the_way['-mkapath'] = os.path.join(file_path[0], file_path[1])
    if the_way.get('-r', null) == null:
        clrprint('You forgot -r!', clr='r')
        return None
    return the_way


def run_ff(q, out, repo):
    while True:
        if q.empty():
            break
        king = q.get()
        check_make_dirs(king)
        if king.get('-ff', null) != null:
            out.put(ff_pass(king))
        else:
            out.put(king)
        repo.put((king.get('-took', '00:00:00'), king.get('-runtot', 0.0)))
        q.task_done()
    return out


def run_amq(q, out, repo):
    while True:
        if q.empty():
            break
        the_way = q.get()
        if the_way.get('-amq', null) != null or the_way.get('-nyx', null) != null or the_way.get('-theia', null) != null:
            out.put(amq_pass(the_way, the_way['-out']))
        else:
            out.put(the_way)
        if the_way.get('-clean', null) != null:
            if os.path.exists(os.path.join(the_way['-path'], the_way['-out'][:-3] + '.vpy')):
                os.remove(os.path.join(the_way['-path'], the_way['-out'][:-3] + '.vpy'))
            if os.path.exists(os.path.join(the_way['-path'], the_way['-file'] + '.vpy')):
                os.remove(os.path.join(the_way['-path'], the_way['-file'] + '.vpy'))
        repo.put((the_way.get('-took', '00:00:00'), the_way.get('-runtot', 0.0)))
        q.task_done()
    return out


def run_apo(q, out, repo):
    while True:
        if q.empty():
            break
        the_way = q.get()
        if (the_way.get('-apo', null) != null or the_way.get('-apf', null) != null or the_way.get('-chr', null) != null
                or the_way.get('-chf', null) != null or the_way.get('-aion', null) != null):
            out.put(apo_pass(the_way, the_way['-out']))
        else:
            out.put(the_way)
        repo.put((the_way.get('-took', '00:00:00'), the_way.get('-runtot', 0.0)))
        q.task_done()
    return out


def run_prot(q, out, repo):
    while True:
        if q.empty():
            break
        the_way = q.get()
        if the_way.get('-ahq', null) != null or the_way.get('-gaia', null) != null:
            out.put(ahq_pass(the_way, the_way['-out']))
        elif the_way.get('-prot', null) != null or the_way.get('-iris', null) != null:
            out.put(prot_pass(the_way, the_way['-out']))
        else:
            out.put(the_way)
        repo.put((the_way.get('-took', '00:00:00'), the_way.get('-runtot', 0.0)))
        q.task_done()
    return out


def get_sort_num(q):
    new = q.replace(':', '')
    return float(new)


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
    if dar1 == 4 and dar2 == 3:
        the_way['square'] = True
    else:
        the_way['square'] = False
    the_way['-w'] = str(width)
    the_way['-h'] = str(height)
    the_way['-wx2'] = str(width * 2)
    the_way['-hx2'] = str(height * 2)
    the_way['-wx4'] = str(width * 4)
    the_way['-hx4'] = str(height * 4)
    if DEBUG:
        print('-w ' + the_way['-w'])
        print('-h ' + the_way['-h'])
        print('-wx2 ' + the_way['-wx2'])
        print('-hx2 ' + the_way['-hx2'])
    return the_way


def get_duration(the_way, ext):
    try:
        command = FFPROBE + ' -v error -show_entries format=duration -sexa' \
                            'gesimal -select_streams v:0 -of default=noprint_wrappers=1 "' + \
                  os.path.join(the_way['-path'], the_way['-file'] + '.' + ext)
        dar = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    except:
        return traceback.format_exc()
    duration = None
    split_dar = re.split('\\n', dar.stdout)
    if DEBUG:
        print(split_dar)
    for item in split_dar:
        more_split = re.split('=', item)
        if more_split[0] == 'duration':
            duration = more_split[1]
    return duration


def generate_vpy(the_way, the_file):
    deinterlace = ''
    TFF = 'True'
    if the_way.get('-deinterlace', null) != null:
        field = '0'
        if the_way.get('-bottomfield', null) != null:
            field = '1'
            TFF = 'False'
        bob = 'clip = clip[::2]\n'
        if the_way.get('-bob', null) != null:
            bob = ''
            field = '2'
        deinterlace = 'clip = core.std.SetFrameProp(clip=clip, prop="_FieldBased", intval=' + field + ')\n' \
        'clip = havsfunc.QTGMC(Input=clip, Preset="Placebo", TFF=' + TFF + ')\n'
        deinterlace = deinterlace + bob
    ifps = '30000'
    ofps = '30000'
    fpsden = '1001'
    if the_way.get('-ifps', null) != null:
        if the_way['-ifps'] == '24':
            ifps = '24'
            ofps = '24'
            fpsden = '1'
        if the_way['-ifps'] == '23':
            ifps = '24000'
            ofps = '24000'
        if the_way['-ifps'] == '60' or the_way['-ifps'] == '59':
            ifps = '30000'
            ofps = '60000'
    sigma = '2.0'
    if the_way.get('-denoiselevel', null) != null:
        sigma = the_way['-denoiselevel']
    if the_way.get('-noisesigma', null) != null:
        sigma = the_way['-noisesigma']
    denoiser = ''
    if the_way.get('-ezdenoise', null) != null:
        denoiser = 'clip = havsfunc.QTGMC(Input=clip, TFF=' + TFF + ', Preset="Placebo", NoiseProcess=1, ChromaNoise=True,' \
               ' Denoiser="KNLMeansCL", DenoiseMC=True, NoiseTR=2, Sigma=' + sigma + ')\nclip = clip[::2]\n'
    if the_way.get('-minideen', null) != null:
        rad = '1,1,1'
        if the_way.get('-rad', null) != null:
            rad = the_way['-rad']
        denoiser = denoiser + 'clip = core.neo_minideen.MiniDeen(clip, radius=[' + rad + '], threshold=[10,12,12])\n'
    if the_way.get('-fft3d', null) != null:
        # can be -1 to 5
        rad = '3'
        if the_way.get('-rad', null) != null:
            rad = the_way['-rad']
        denoiser = denoiser + 'clip = core.neo_fft3d.FFT3D(clip, sigma=' + sigma + ', bt=' + rad + ', ncpu=8)\n'
    if the_way.get('-neovd', null) != null:
        # I liked this one most.
        rad = '6'
        percent = '85.0'
        if the_way.get('-rad', null) != null:
            rad = the_way['-rad']
        if the_way.get('-percent', null) != null:
            percent = the_way['-percent']
        denoiser = denoiser + ('clip = core.neo_vd.VagueDenoiser(clip, threshold=' + sigma + ', nsteps=' + rad + ', percent=' +
                    percent + ')\n')
    if the_way.get('-dfttest', null) != null:
        # There are soooo many more parameters I could add.
        # This one is like neovd
        sigma = '8.0'
        if the_way.get('-denoiselevel', null) != null:
            sigma = the_way['-denoiselevel']
        rad = '0'
        if the_way.get('-dfttestType', null) != null:
            rad = the_way['-dfttestType']
        denoiser = denoiser + 'clip = core.neo_dfttest.DFTTest(clip, ftype=' + rad + ', sigma=' + sigma + ')\n'
    the_script = 'import vapoursynth as vs\ncore = vs.core\nimport havsfunc\n' \
                 'clip = core.lsmas.LWLibavSource(source="' + get_drive_path(the_way['-path'], the_way, False).replace('\\', '/') + '/' + the_file + '.' \
                 + the_way['-ext'] + '", format="YUV420P8", stream_index=0, cache=0, prefer_hw=0)\n' \
                 'clip = core.std.SetFrameProps(clip, _Matrix=5)\n' \
                 'clip = clip if not core.text.FrameProps(clip,"_Transfer") else core.std.SetFrameProps(clip, _Transfer=5)\n' \
                 'clip = clip if not core.text.FrameProps(clip,"_Primaries") else core.std.SetFrameProps(clip, _Primaries=5)\n' \
                 'clip = core.std.SetFrameProp(clip=clip, prop="_ColorRange", intval=1)\n' \
                 'clip = core.std.AssumeFPS(clip=clip, fpsnum=' + ifps + ', fpsden=' + fpsden + ')\n' \
                 + deinterlace + denoiser + \
                 'clip = core.std.AssumeFPS(clip=clip, fpsnum=' + ofps + ', fpsden=' + fpsden + ')\nclip.set_output()\n'
    f_out_put = open(os.path.join(the_way['-path'], the_file + '.vpy'), 'w')
    f_out_put.write(the_script)
    f_out_put.close()


def generate_nnedi3_vpy(the_way, the_file):
    field = '1'
    if the_way.get('-bottomfield', null) != null:
        field = '0'
    if the_way.get('-bob', null) != null:
        field = '2'
    if the_way.get('-bob2', null) != null:
        field = '3'
    nnedi3_size = '6'
    if the_way.get('-nnedi3size', null) != null:
        nnedi3_size = the_way['-nnedi3size']
    deinterlace = 'clip = core.std.SetFrameProp(clip=clip, prop="_FieldBased", intval=' + field + ')\n' \
         'clip = core.nnedi3.nnedi3(clip=clip, field=' + field + ', nsize=' + nnedi3_size + ', nns=4, qual=2, pscrn=4, exp=2)\n'
    if the_way.get('-nnedi3cl', null) != null:
        deinterlace = 'clip = core.std.SetFrameProp(clip=clip, prop="_FieldBased", intval=' + field + ')\n' \
             'clip = core.nnedi3cl.NNEDI3CL(clip=clip, field=' + field + ', nsize=' + nnedi3_size + ', nns=4, qual=2, pscrn=2)\n'
    ifps = '30000'
    ofps = '30000'
    fpsden = '1001'
    if the_way.get('-ifps', null) != null:
        if the_way['-ifps'] == '24':
            ifps = '24'
            ofps = '24'
            fpsden = '1'
        if the_way['-ifps'] == '23':
            ifps = '24000'
            ofps = '24000'
        if the_way['-ifps'] == '60' or the_way['-ifps'] == '59':
            ifps = '30000'
            ofps = '60000'
    the_script = 'import vapoursynth as vs\ncore = vs.core\n' \
                 'clip = core.lsmas.LWLibavSource(source="' + the_way['-path'].replace('\\', '/') + '/' + the_file + '.' \
                 + the_way['-ext'] + '", format="YUV420P8", stream_index=0, cache=0, prefer_hw=0)\n' \
                 'clip = core.std.SetFrameProps(clip, _Matrix=5)\n' \
                 'clip = clip if not core.text.FrameProps(clip,"_Transfer") else core.std.SetFrameProps(clip, _Transfer=5)\n' \
                 'clip = clip if not core.text.FrameProps(clip,"_Primaries") else core.std.SetFrameProps(clip, _Primaries=5)\n' \
                 'clip = core.std.SetFrameProp(clip=clip, prop="_ColorRange", intval=1)\n' \
                 'clip = core.std.AssumeFPS(clip=clip, fpsnum=' + ifps + ', fpsden=' + fpsden + ')\n' \
                 + deinterlace + \
                 'clip = core.std.AssumeFPS(clip=clip, fpsnum=' + ofps + ', fpsden=' + fpsden + ')\nclip.set_output()\n'
    f_out_put = open(os.path.join(the_way['-path'], the_file + '.vpy'), 'w')
    f_out_put.write(the_script)
    f_out_put.close()


def make_merge_command(the_way, filename):
    the_command = MKVMERGE + ' ' + the_way['-mergecommand'].replace('~', ' ')
    if os.path.exists(os.path.join(get_drive_path(the_way['-path'], the_way, True), filename + '.mkv')):
        the_command = the_command.replace('rxx1', os.path.join(get_drive_path(the_way['-path'], the_way, True), filename + '.mkv'))
        the_command = the_command.replace('rxxPt1', os.path.join(get_drive_path(the_way['-path'], the_way, True), filename + '.mkv'))
    else:
        the_command = the_command.replace('rxx1', os.path.join(get_drive_path(the_way['-path'], the_way, False), filename + '.mkv'))
        the_command = the_command.replace('rxxPt1', os.path.join(get_drive_path(the_way['-path'], the_way, False), filename + '.mkv'))
    the_command = the_command.replace('rxxOrigin', os.path.join(the_way['-path'], the_way['-file'] + '.mkv'))
    the_command = the_command.replace('rxx2', the_way['-mkapath'])
    the_command = the_command.replace('rxxMka', the_way['-mkapath'])
    if the_way.get('-pt2', null) != null:
        if os.path.exists(os.path.join(get_drive_path(the_way['-path'], the_way, True), filename + '1.mkv')):
            the_command = the_command.replace('rxx3', os.path.join(get_drive_path(the_way['-path'], the_way, True), filename + '1.mkv'))
            the_command = the_command.replace('rxxOut', os.path.join(get_drive_path(the_way['-path'], the_way, True), filename + '1.mkv'))
        else:
            the_command = the_command.replace('rxx3', os.path.join(get_drive_path(the_way['-path'], the_way, False), filename + '1.mkv'))
            the_command = the_command.replace('rxxOut', os.path.join(get_drive_path(the_way['-path'], the_way, False), filename + '1.mkv'))
    else:
        file_name = get_name(the_way)
        the_command = the_command.replace('rxx3', str(os.path.join(the_way['-path'], file_name + '.mkv')))
        the_command = the_command.replace('rxxOut', str(os.path.join(the_way['-path'], file_name + '.mkv')))
        the_command = the_command.replace('rxx4', file_name)
        the_command = the_command.replace('rxxTitle', file_name)
    return the_command


def make_append_command(the_way):
    the_command = MKVMERGE + ' ' + the_way['-appendcommand'].replace('~', ' ')
    name = get_name(the_way)
    the_command = the_command.replace('rxx3', os.path.join(the_way['-path'], name + '.mkv'))
    if os.path.exists(os.path.join(get_drive_path(the_way['-path'], the_way, True), name + ' pt1 AI1.mkv')):
        the_command = the_command.replace('rxx1', os.path.join(get_drive_path(the_way['-path'], the_way, True), name + ' pt1 AI1.mkv'))
        the_command = the_command.replace('rxxPt1', os.path.join(get_drive_path(the_way['-path'], the_way, True), name + ' pt1 AI1.mkv'))
    else:
        the_command = the_command.replace('rxx1', os.path.join(get_drive_path(the_way['-path'], the_way, False), name + ' pt1 AI1.mkv'))
        the_command = the_command.replace('rxxPt1', os.path.join(get_drive_path(the_way['-path'], the_way, False), name + ' pt1 AI1.mkv'))
    if os.path.exists(os.path.join(get_drive_path(the_way['-path'], the_way, True), name + ' pt2 AI1.mkv')):
        the_command = the_command.replace('rxx2', os.path.join(get_drive_path(the_way['-path'], the_way, True), name + ' pt2 AI1.mkv'))
        the_command = the_command.replace('rxxPt2', os.path.join(get_drive_path(the_way['-path'], the_way, True), name + ' pt2 AI1.mkv'))
    else:
        the_command = the_command.replace('rxx2', os.path.join(get_drive_path(the_way['-path'], the_way, False), name + ' pt2 AI1.mkv'))
        the_command = the_command.replace('rxxPt2', os.path.join(get_drive_path(the_way['-path'], the_way, False), name + ' pt2 AI1.mkv'))
    the_command = the_command.replace('rxx4', name)
    the_command = the_command.replace('rxxOut', os.path.join(the_way['-path'], name + '.mkv'))
    the_command = the_command.replace('rxxTitle', name)
    return the_command


def remove_some_file(filepath, filename):
    if filename[-2:] == 'ff' or filename[-3:] == 'vpy':
        if os.path.exists(os.path.join(get_drive_path(filepath['-path'], filepath, True), filename[:-5] + 'ff.mkv')):
            os.remove(os.path.join(get_drive_path(filepath['-path'], filepath, True), filename[:-5] + 'ff.mkv'))
        if os.path.exists(os.path.join(get_drive_path(filepath['-path'], filepath, True), filename[:-3] + 'vpy.mkv')):
            os.remove(os.path.join(get_drive_path(filepath['-path'], filepath, True), filename[:-3] + 'vpy.mkv'))
        if os.path.exists(os.path.join(get_drive_path(filepath['-path'], filepath, True), filename[:-2] + 'ff.mkv')):
            os.remove(os.path.join(get_drive_path(filepath['-path'], filepath, True), filename[:-2] + 'ff.mkv'))
        if os.path.exists(os.path.join(get_drive_path(filepath['-path'], filepath, True), filename[:-2] + ' ff.mkv')):
            os.remove(os.path.join(get_drive_path(filepath['-path'], filepath, True), filename[:-2] + ' ff.mkv'))
        if os.path.exists(os.path.join(get_drive_path(filepath['-path'], filepath, False), filename[:-5] + 'ff.mkv')):
            os.remove(os.path.join(get_drive_path(filepath['-path'], filepath, False), filename[:-5] + 'ff.mkv'))
        if os.path.exists(os.path.join(get_drive_path(filepath['-path'], filepath, False), filename[:-3] + 'vpy.mkv')):
            os.remove(os.path.join(get_drive_path(filepath['-path'], filepath, False), filename[:-3] + 'vpy.mkv'))
        if os.path.exists(os.path.join(get_drive_path(filepath['-path'], filepath, False), filename[:-2] + 'ff.mkv')):
            os.remove(os.path.join(get_drive_path(filepath['-path'], filepath, False), filename[:-2] + 'ff.mkv'))
        if os.path.exists(os.path.join(get_drive_path(filepath['-path'], filepath, False), filename[:-2] + ' ff.mkv')):
            os.remove(os.path.join(get_drive_path(filepath['-path'], filepath, False), filename[:-2] + ' ff.mkv'))


def get_json_state(filepath):
    pt2 = ''
    if filepath['-pass2']:
        pt2 = 'pt2'
    state = {}
    if os.path.exists(os.path.join(filepath['-path'], filepath['-file'] + pt2 + '_run.json')):
        state_file = open(os.path.join(filepath['-path'], filepath['-file'] + pt2 + '_run.json'), 'r')
        state = json.load(state_file)
        state_file.close()
    return state


def save_json_state(filepath, what_pass):
    pt2 = ''
    if filepath['-pass2']:
        pt2 = 'pt2'
    state = get_json_state(filepath)
    if os.path.exists(os.path.join(filepath['-path'], filepath['-file'] + pt2 + '_run.json')):
        os.remove(os.path.join(filepath['-path'], filepath['-file'] + pt2 + '_run.json'))
    state[what_pass] = 'done'
    outfile = open(os.path.join(filepath['-path'], filepath['-file'] + pt2 + '_run.json'), 'w')
    json.dump(state, outfile)
    outfile.close()


def make_beta_environment_variable(beta_env=None):
    if beta_env is None:
        beta_env = os.environ.copy()
    if ALPHA:
        beta_env["TVAI_MODEL_DIR"] = 'C:\\ProgramData\\Topaz Labs LLC\\Topaz Video AI ALPHA\\models'
    else:
        beta_env["TVAI_MODEL_DIR"] = 'C:\\ProgramData\\Topaz Labs LLC\\Topaz Video AI Beta\\models'
    return beta_env


def make_debug_environment_variable(theFileName):
    debug_env = os.environ.copy()
    debug_env["FFREPORT"] = 'file=' + theFileName.replace('\\', '\\\\').replace(':', '\\:') + ':level=32'
    return debug_env


def env_run_command(theWay, command, output):
    debugenv = None
    if DEBUG:
        debugenv = make_debug_environment_variable(os.path.join(theWay['-path'], output + '.log'))
    if BETA or ALPHA:
        beta_env = make_beta_environment_variable(debugenv)
        subprocess.call(command, env=beta_env)
    else:
        if DEBUG:
            subprocess.call(command, env=debugenv)
        else:
            subprocess.call(command)


def get_drive_path(thepath, theway, isfrom):
    oldpath = thepath[3:]
    if isfrom:
        return theway['fromDrive'] + oldpath
    return theway['toDrive'] + oldpath


def swap_drive_path(theway):
    temppath = theway['toDrive']
    theway['toDrive'] = theway['fromDrive']
    theway['fromDrive'] = temppath
    return theway


def check_make_dirs(theway):
    finalpath = get_drive_path(theway['-path'], theway, False)
    if not os.path.exists(finalpath):
        os.makedirs(finalpath, exist_ok=True)


def get_details_for_printing(took_string):
    found_index = took_string.find('time:')
    if found_index >= 0:
        found_name = took_string[:found_index]
        found_time = took_string[(found_index + 5):]
    else:
        found_name = ''
        found_time = took_string
    return [found_name, 'time:', found_time]


def run_linearly(lVideos, fStart):
    lJsonRuns = []
    for oVideoSpec in lVideos:
        clrprint('Starting:', oVideoSpec['-name'] + '\n', clr='d,y')
        check_make_dirs(oVideoSpec)
        if oVideoSpec.get('-ff', null) != null:
            clrprint('Starting ffmpeg pass.', clr='m')
            oVideoSpec = ff_pass(oVideoSpec)
            clrprint('ff pass took:', get_details_for_printing(oVideoSpec.get('-took', '00:00:00'))[2], clr='d,b')
            clrprint('Running total:', seconds_to_str(oVideoSpec.get('-runtot', 0.0)) + '\n', clr='d,b')
        if oVideoSpec.get('-amq', null) != null or oVideoSpec.get('-nyx', null) != null or oVideoSpec.get('-theia', null) != null:
            clrprint('Starting denoise pass.', clr='m')
            oVideoSpec = amq_pass(oVideoSpec, oVideoSpec['-out'])
            clrprint('Denoise pass took:', get_details_for_printing(oVideoSpec.get('-took', '00:00:00'))[2], clr='d,b')
            clrprint('Running total:', seconds_to_str(oVideoSpec.get('-runtot', 0.0)) + '\n', clr='d,b')
        if oVideoSpec.get('-clean', null) != null:
            if os.path.exists(os.path.join(oVideoSpec['-path'], oVideoSpec['-out'][:-3] + '.vpy')):
                os.remove(os.path.join(oVideoSpec['-path'], oVideoSpec['-out'][:-3] + '.vpy'))
            if os.path.exists(os.path.join(oVideoSpec['-path'], oVideoSpec['-file'] + '.vpy')):
                os.remove(os.path.join(oVideoSpec['-path'], oVideoSpec['-file'] + '.vpy'))
        if oVideoSpec.get('-ahq', null) != null or oVideoSpec.get('-gaia', null) != null:
            clrprint('Starting enhancement pass.', clr='m')
            oVideoSpec = ahq_pass(oVideoSpec, oVideoSpec['-out'])
            clrprint('Enhancement pass took:', get_details_for_printing(oVideoSpec.get('-took', '00:00:00'))[2], clr='d,b')
            clrprint('Running total:', seconds_to_str(oVideoSpec.get('-runtot', 0.0)) + '\n', clr='d,b')
        elif oVideoSpec.get('-prot', null) != null or oVideoSpec.get('-iris', null) != null:
            clrprint('Starting enhancement pass.', clr='m')
            oVideoSpec = prot_pass(oVideoSpec, oVideoSpec['-out'])
            clrprint('Enhancement pass took:', get_details_for_printing(oVideoSpec.get('-took', '00:00:00'))[2], clr='d,b')
            clrprint('Running total:', seconds_to_str(oVideoSpec.get('-runtot', 0.0)) + '\n', clr='d,b')
        if (oVideoSpec.get('-apo', null) != null or oVideoSpec.get('-apf', null) != null or oVideoSpec.get('-chr', null) != null
                or oVideoSpec.get('-chf', null) != null or oVideoSpec.get('-aion', null) != null):
            clrprint('Starting interpolation pass.', clr='m')
            oVideoSpec = apo_pass(oVideoSpec, oVideoSpec['-out'])
            clrprint('Interpolation pass took:', get_details_for_printing(oVideoSpec.get('-took', '00:00:00'))[2], clr='d,b')
            clrprint('Running total:', seconds_to_str(oVideoSpec.get('-runtot', 0.0)) + '\n', clr='d,b')
        clrprint('Starting final pass.', clr='m')
        convert_song(oVideoSpec)
        if oVideoSpec.get('jsonRun', null) != null:
            lJsonRuns.append(oVideoSpec['jsonRun'])
    if len(lJsonRuns) > 0:
        for sRun in lJsonRuns:
            os.remove(sRun)
    fEnd = time()
    clrprint('Total time:', seconds_to_str(fEnd - fStart), clr='g,b')


if __name__ == '__main__':
    start = time()
    clrprint('Reading folders.', clr='d')
    artistfile = open(FOLDERS, 'r', -1, 'utf-8')
    artistlist = artistfile.readlines()
    dirs = []
    for artist in artistlist:
        if DEBUG:
            clrprint(artist.strip(), clr='r')
        dirs.append(PREDIR + artist.strip())
    qTheStack = []
    for currentPath in dirs:
        for wFile in generate_next_file(currentPath):
            qTheStack.append((wFile[0], wFile[1]))
    if DEBUG:
        for elem in qTheStack:
            print(elem)
    bstart = time()
    OptionsStack = []
    AmountLoop = []
    for dude in qTheStack:
        option = populate_options(dude)
        if option is not None:
            OptionsStack.append(option)
            if SORT:
                if option.get('-t', null) != null:
                    option['-sort'] = get_sort_num(option['-t'])
                else:
                    option['-sort'] = get_sort_num(get_duration(option, option['-ext']))
            AmountLoop.append(option)
            if option.get('-pt2', null) != null:
                CopyOption = option.copy()
                CopyOption['-pass2'] = True
                CopyOption['-sort'] = get_sort_num(CopyOption['-t2'])
                AmountLoop.append(CopyOption)
    if SORT and not LINEAR:
        AmountLoop.sort(key=lambda item: (item['-sort']), reverse=True)
    clrprint(str(len(AmountLoop)), 'Things loaded.' + '\n', clr='b,d')
    if LINEAR:
        run_linearly(AmountLoop, start)
    else:
        ffinput = JoinableQueue()
        fftimes = JoinableQueue()
        for video in AmountLoop:
            ffinput.put(video)
        ff_out_put = JoinableQueue()
        for i in range(FFNUM):
            worker = Process(target=run_ff, args=(ffinput, ff_out_put, fftimes))
            worker.daemon = True
            worker.start()
        for Bool in AmountLoop:
            say = get_details_for_printing(fftimes.get()[0])
            clrprint(say[0], say[1], say[2], clr='y,d,b')
            fftimes.task_done()
        ffinput.join()
        amqinput = JoinableQueue()
        amqtimes = JoinableQueue()
        amqsort = []
        while not ff_out_put.empty():
            blh = ff_out_put.get()
            amqsort.append(blh)
            ff_out_put.task_done()
        amqsort.sort(key=lambda item: (item['-sort']), reverse=True)
        for thing in amqsort:
            amqinput.put(thing)
        amqoutput = JoinableQueue()
        clrprint('\nStarting denoise pass.', clr='m')
        for i in range(TVAINUM):
            worker = Process(target=run_amq, args=(amqinput, amqoutput, amqtimes))
            worker.daemon = True
            worker.start()
        for Bool in AmountLoop:
            saywhat = amqtimes.get()
            say = get_details_for_printing(saywhat[0])
            clrprint(say[0], say[1], say[2], clr='y,d,b')
            print('Running total: ' + seconds_to_str(saywhat[1]) + '\n')
            amqtimes.task_done()
        amqinput.join()

        apoinput = JoinableQueue()
        apotimes = JoinableQueue()
        aposort = []
        while not amqoutput.empty():
            blh = amqoutput.get()
            aposort.append(blh)
            amqoutput.task_done()
        aposort.sort(key=lambda item: (item['-sort']), reverse=True)
        for thing in aposort:
            apoinput.put(thing)
        apooutput = JoinableQueue()
        clrprint('Starting enhancement pass.', clr='m')
        for i in range(TVAINUM):
            worker = Process(target=run_prot, args=(apoinput, apooutput, apotimes))
            worker.daemon = True
            worker.start()
        for Bool in AmountLoop:
            saywhat = apotimes.get()
            say = get_details_for_printing(saywhat[0])
            clrprint(say[0], say[1], say[2], clr='y,d,b')
            clrprint('Running total:', seconds_to_str(saywhat[1]) + '\n', clr='d,b')
            apotimes.task_done()
        apoinput.join()

        protsort = []
        protinput = JoinableQueue()
        prottimes = JoinableQueue()
        while not apooutput.empty():
            blh = apooutput.get()
            protsort.append(blh)
            apooutput.task_done()
        protoutput = JoinableQueue()
        protsort.sort(key=lambda item: (item['-sort']), reverse=True)
        for thing2 in protsort:
            protinput.put(thing2)
        clrprint('Starting interpolation pass.', clr='m')
        for i in range(APONUM):
            worker = Process(target=run_apo, args=(protinput, protoutput, prottimes))
            worker.daemon = True
            worker.start()
        for Bool in AmountLoop:
            saywhat = prottimes.get()
            say = get_details_for_printing(saywhat[0])
            clrprint(say[0], say[1], say[2], clr='y,d,b')
            clrprint('Running total:', seconds_to_str(saywhat[1]) + '\n', clr='d,b')
            prottimes.task_done()
        protinput.join()
        clrprint('Starting final pass.', clr='m')
        while not protoutput.empty():
            blh = protoutput.get()
            deets = convert_song(blh)
            if not deets[0]:
                clrprint(deets[1], clr='r')
            protoutput.task_done()
        end = time()
        clrprint('Total time:', seconds_to_str(end - start), clr='g,b')
