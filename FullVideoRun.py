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
BETA = False
CRF = '22'
null = 'null'
FFMPEG = '"C:\\Program Files (x86)\\SVP 4\\utils\\ffmpeg.exe"'
TVAI = '"G:\\Program Files\\Topaz Labs LLC\\Topaz Video AI\\ffmpeg.exe"'
FFPROBE = '"C:\\Program Files (x86)\\SVP 4\\utils\\ffprobe.exe"'
MKVMERGE = '"C:\\Program Files\\MKVToolNix\\mkvmerge.exe"'
# Cut and frame rate correction processes
FFNUM = 3
# How many TVAI instances
TVAINUM = 1
# How many TVAI APO instances
APONUM = 1
PREDIR = 'D:\\'
FOLDERS = 'G:\\Vid\\FullRunList.txt'


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
    if elapsed == None:
        return strftime("%Y-%m-%d %H:%M:%S", localtime())
    else:
        return str(timedelta(seconds=elapsed))[:-4]


def get_ext(ext):
    if ext == 'png':
        return '\\%6d.png'
    else:
        return '.' + ext


def ff_pass(filepath):
    ff_start = time()
    ss = ''
    t = ''
    r = ''
    yadif = ''
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
    out_path = (filepath['-path'], filepath['-file'] + part)
    filepath['-out'] = out_path[1]
    if filepath.get('-yadif', null) != null:
        yadif = '-vf yadif '
    if filepath.get('-denoise', null) != null:
        #dnlevel = '4.0'
        #dnlevel = '2.0'
        dnlevel = '2'
        if filepath.get('-denoiselevel', null) != null:
            dnlevel = filepath['-denoiselevel']
        #yadif = '-vf hqdn3d=luma_spatial=' + dnlevel + ' '
        #yadif = '-vf nlmeans=s=' + dnlevel + ' '
        yadif = '-vf vaguedenoiser=threshold=' + dnlevel + ' '
    try:
        run_three = False
        now_png = False
        decimate = ''
        if filepath.get('-decimate', null) != null:
            #decimate = '-vf "shuffleframes=' + decimate_tmp + '" '
            decimate = '-vf "decimate=cycle=5:dupthresh=1.1" '
        if filepath.get('-vpy', null) != null and filepath.get('-deinterlace', null) != null:
            decimate = '-r ' + filepath['-r'] + ' ' + decimate
            generate_vpy(filepath, filepath['-file'])
            command = FFMPEG + ' -hide_banner -stats_period 2.0 -nostdin -f vapoursynth -i "' + os.path.join(filepath['-path'], filepath['-file'] +
            '.vpy') + '" -y ' + ss + t + '-map 0:v -map 0:a? -map 0:s? -map 0:d? -map 0:t? ' + decimate + '-c:v libx265 -crf' \
            ' 14 -preset slow "' + os.path.join(out_path[0], out_path[1] + '.mkv') + '"'
        if filepath.get('-vpy', null) == null and filepath.get('-deinterlace', null) != null:
            #if not os.path.exists(os.path.join(out_path[0], out_path[1])):
            #    os.mkdir(os.path.join(out_path[0], out_path[1]))
            if filepath.get('-bob', null) == null and filepath.get('-decimate', null) != null:
                decimate = ',"shuffleframes=0|-1","decimate=' + decimate_tmp + '" '
            else:
                decimate = ',"decimate=' + decimate_tmp + '" '
            command = FFMPEG + ' -hide_banner -stats_period 2.0 -nostdin -y -i "' + os.path.join(filepath['-path'],
            filepath['-file'] + '.' + filepath['-ext']) + '" ' + ss + t + '-r ' + filepath['-r'] + ' -filter_complex setsar=1,bwdif=mode=1:parity=-1:deint=0' + decimate + '-c:v libx265 -crf' \
            ' 14 -preset slow "' + os.path.join(out_path[0], out_path[1] + '.mkv') + '"'
            #now_png = True
        if filepath.get('-deinterlace', null) == null:
            command = FFMPEG + ' -hide_banner -stats_period 2.0 -nostdin -i "' + os.path.join(filepath['-path'],
                      filepath['-file'] + '.' + filepath['-ext']) + '" -y ' + ss + t + '-map 0:v -map 0:a? -map 0:s? -map 0:d? -map 0:t? ' + yadif + \
                      r + dering + '-c:v libx265 -crf 16 -preset slow -c:a copy -c:s copy -max_muxing_queue_size 4096 "' + os.path.join(out_path[0], out_path[1] +
                      '.mkv') + '"'
            if filepath.get('-vpy', null) != null:
                generate_vpy(filepath, out_path[1])
                run_three = True
                command3 = FFMPEG + ' -hide_banner -stats_period 2.0 -nostdin -f vapoursynth -i "' + os.path.join(filepath['-path'], out_path[1] +
                '.vpy') + '" -y -map 0:v -map 0:a? -map 0:s? -map 0:d? -map 0:t? ' + r + decimate + '-c:v libx265 -crf' \
                ' 14 -preset slow "' + os.path.join(out_path[0], out_path[1] + 'vpy' + '.mkv') + '"'
                out_path = (filepath['-path'], out_path[1] + 'vpy')
                filepath['-out'] = out_path[1]
        if filepath.get('-name', null) != null:
            if filepath.get('-pt2', null) != null:
                name = filepath['-name'] + part[:-3]
            else:
                name = filepath['-name']
        else:
            name = out_path[1]
        command2 = FFMPEG + ' -hide_banner -stats_period 2.0 -nostdin -i "' + os.path.join(filepath['-path'],
        filepath['-file'] + '.' + filepath['-ext']) + '" -y ' + ss + t + '-map 0:v -map 0:a? -map 0:s? -map' \
        ' 0:d? -map 0:t? ' + r + '-vn -c:a copy -c:s copy -c:d copy "' + os.path.join(out_path[0], name + '.mka') + '"'
        filepath['-mkapath'] = os.path.join(out_path[0], name + '.mka')
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
        if run_three and get_json_state(filepath).get('ff2', null) == null:
            subprocess.call(command3)
            save_json_state(filepath, 'ff2')
        filepath['-ext'] = 'mkv'
        if now_png:
            filepath['-ext'] = 'png'
            filepath['-folders'].append(os.path.join(out_path[0], out_path[1]))
    except:
        return None
    ff_end = time()
    the_name = filepath['-out']
    if filepath.get('-name', null) != null:
        the_name = filepath['-name']
    filepath['-took'] = the_name + ' time: ' + seconds_to_str(ff_end - ff_start)
    filepath['-sort'] = ff_end - ff_start
    filepath['-runtot'] = filepath['-sort']
    return filepath


def amq_pass(filepath, filename):
    ff_start = time()
    out_path = (filepath['-path'], filename + 'amq')
    filepath['-out'] = out_path[1]
    filepath['-folders'].append(os.path.join(filepath['-path'], out_path[1]))
    try:
        if not os.path.exists(os.path.join(filepath['-path'], filepath['-out'])):
            os.mkdir(os.path.join(filepath['-path'], filepath['-out']))
        if DEBUG:
            print('The Make Folder: ')
            print('"' + os.path.join(filepath['-path'], filepath['-out']) + '"')
    except OSError as exc:
        if exc.errno != errno.EEXIST:
            raise
        pass
    blend = '0'
    if filepath.get('-blend', 'null') != null:
        blend = filepath['-blend']
    if filepath.get('-theia', null) != null:
        t_noise = filepath.get('-tnoise', '-0.39')
        t_blur = filepath.get('-tblur', '0.0')
        t_comp = filepath.get('-tcomp', '0.33')
        command = TVAI + ' -hide_banner -stats_period 2.0 -nostdin -y -i "' + \
                  os.path.join(filepath['-path'], filename + get_ext(filepath['-ext'])) + '" -r ' + filepath['-r'] + ' -filter_complex scale=w=' + filepath['-w'] + ':h=' + \
                  filepath['-h'] + ',setsar=1,tvai_up=model=thf-4:scale=1.0:w=' + filepath['-w'] + ':h=' + filepath['-h'] + \
                  ':noise=' + t_noise + ':blur=' + t_blur + ':compression=' + t_comp + ':device=0:vram=1:instances=1 -c:v png -compression_level 2 -pred mixed -pix_fmt rgb24 -sws_flags +accurate_rnd+full_chroma_int "' + \
                  os.path.join(out_path[0], out_path[1]) + '\\%6d.png"'
    elif filepath.get('-nyx', null) != null:
        n_version = filepath.get('-nyxver', '2')
        if n_version == '2':
            n_version = 'nyx-2'
        if n_version == '1':
            n_version = 'nyx-1'
        if n_version == '3':
            n_version = 'nxf-1'
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
        command = TVAI + ' -hide_banner -stats_period 2.0 -nostdin -y -i "' + \
                  os.path.join(filepath['-path'], filename + get_ext(filepath['-ext'])) + '" -r ' + filepath['-r'] + ' -filter_complex scale=w=' + filepath['-w'] + ':h=' + \
                  filepath['-h'] + ',setsar=1,tvai_up=model=' + n_version + ':scale=1:preblur=' + n_preblur + ':noise=' + n_noise + \
                  ':details=' + n_details + ':halo=' + n_halo + ':blur=' + n_blur + ':compression=' + n_comp + ':blend=' + n_blend + n_auto + ':dev' \
                  'ice=0:vram=1:instances=1 -c:v png -compression_level 2 -pred mixed -pix_fmt rgb24 -sws_flags +accurate_rnd+full_chroma_int "' + os.path.join(out_path[0], out_path[1]) + '\\%6d.png"'
    else:
        am = 'amq-13'
        if filepath.get('-high', null) != null:
            am = 'ahq-12'
        command = TVAI + ' -hide_banner -stats_period 2.0 -nostdin -y -i "' + \
                  os.path.join(filepath['-path'], filename + get_ext(filepath['-ext'])) + '" -r ' + filepath['-r'] + ' -filter_complex scale=w=' + filepath['-w'] + ':h=' + filepath['-h'] + ',' \
                  'setsar=1,tvai_up=model=' + am + ':scale=1.0:w=' + filepath['-w'] + ':h=' + filepath['-h'] + ':blend=' + blend + ':device=0:vra' \
                  'm=1:instances=1 -c:v png -compression_level 2 -pred mixed -pix_fmt rgb24 -sws_flags +accurate_rnd+full_chroma_int "' + os.path.join(out_path[0], out_path[1]) + '\\%6d.png"'
    try:
        if DEBUG:
            print('The Command: ')
            print(command)
        if get_json_state(filepath).get('amq', null) == null:
            if BETA:
                beta_env = make_beta_environment_variable()
                subprocess.call(command, env=beta_env)
            else:
                subprocess.call(command)
            save_json_state(filepath, 'amq')
        filepath['-ext'] = 'png'
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
    filepath['-took'] = the_name + ' time: ' + seconds_to_str(ff_end - ff_start)
    filepath['-sort'] = ff_end - ff_start
    if filepath.get('-runtot', None) is not None:
        filepath['-runtot'] = filepath['-runtot'] + filepath['-sort']
    else:
        filepath['-runtot'] = filepath['-sort']
    return filepath


def apo_pass(filepath, filename):
    ff_start = time()
    out_path = (filepath['-path'], filename + 'apo')
    filepath['-out'] = out_path[1]
    filepath['-folders'].append(os.path.join(filepath['-path'], out_path[1]))
    try:
        if not os.path.exists(os.path.join(filepath['-path'], filepath['-out'])):
            os.mkdir(os.path.join(filepath['-path'], filepath['-out']))
        if DEBUG:
            print('The Make Folder: ')
            print('"' + os.path.join(filepath['-path'], filepath['-out']) + '"')
    except OSError as exc:
        if exc.errno != errno.EEXIST:
            raise
        pass
    frame = ''
    if filepath['-ext'] == 'png':
        frame = ' -framerate ' + filepath['-r']
    model = 'apo-8'
    if filepath.get('-chr', null) != null:
        model = 'chr-2'
    if filepath.get('-chf', null) != null:
        model = 'chf-3'
    if filepath.get('-apf', null) != null:
        model = 'apf-1'
    try:
        command = TVAI + ' -hide_banner -stats_period 2.0 -nostdin' \
                  + frame + ' -y -i "' + os.path.join(filepath['-path'], filename + get_ext(filepath['-ext'])) + '" -filter_complex tvai_fi=model=' + model + ':slowmo=2.5:rdt=0.000001:device=0:vram=1:in' \
                  'stances=0 -c:v png -compression_level 2 -pred mixed -pix_fmt rgb24 -sws_flags +accurate_rnd+full_chroma_int "' + os.path.join(out_path[0], out_path[1]) + '\\%6d.png"'
        if DEBUG:
            print('The Command: ')
            print(command)
        if get_json_state(filepath).get('apo', null) == null:
            if BETA:
                beta_env = make_beta_environment_variable()
                subprocess.call(command, env=beta_env)
            else:
                subprocess.call(command)
            save_json_state(filepath, 'apo')
        filepath['-ext'] = 'png'
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
    filepath['-took'] = the_name + ' time: ' + seconds_to_str(ff_end - ff_start)
    filepath['-sort'] = ff_end - ff_start
    if filepath.get('-runtot', None) is not None:
        filepath['-runtot'] = filepath['-runtot'] + filepath['-sort']
    else:
        filepath['-runtot'] = filepath['-sort']
    return filepath


def get_r(filepath):
    if (filepath.get('-apo', null) != null or filepath.get('-apf', null) != null or filepath.get('-chr', null) != null
            or filepath.get('-chf', null) != null):
        if filepath['-r'] == '23.976' or filepath['-r'] == '24':
            val = (float(filepath['-r']) * 2.5)
        else:
            val = (float(filepath['-r']) * 2)
    else:
        val = filepath['-r']
    return ' -r ' + str(val)


def ahq_pass(filepath, filename):
    ff_start = time()
    out_path = (filepath['-path'], filename + 'ahq')
    filepath['-out'] = out_path[1]
    filepath['-folders'].append(os.path.join(filepath['-path'], filepath['-out']))
    try:
        if not os.path.exists(os.path.join(filepath['-path'], filepath['-out'])):
            os.mkdir(os.path.join(filepath['-path'], filepath['-out']))
        if DEBUG:
            print('The Make Folder: ')
            print('"' + os.path.join(filepath['-path'], filepath['-out']) + '"')
    except OSError as exc:
        if exc.errno != errno.EEXIST:
            raise
        pass
    model = 'ahq-12'
    if filepath.get('-med', 'null') != null:
        model = 'amq-13'
    scale = '2.25'
    if filepath.get('-gaia', 'null') != null:
        scale = '0'
        model = 'ghq-5'
    if filepath.get('-hd', 'null') != null:
        scale = '1'
    blend = '0'
    if filepath.get('-blend', 'null') != null:
        blend = filepath['-blend']
    command = TVAI + ' -hide_banner -stats_period 2.0 -nostdin -y -i "' \
              + os.path.join(filepath['-path'], filename + get_ext(filepath['-ext'])) + '" -filter_complex scale=w=' + \
              filepath['-w'] + ':h=' + filepath['-h'] + ',setsar=1,tvai_up=model=' + model + ':scale=' + scale + ':w=1920:h=1080:blend=' + blend + ':device' \
              '=0:vram=1:instances=1,scale=w=1920:h=1080:flags=lanczos:threads=0:force_original_aspect_ratio=decrease,p' \
              'ad=1920:1080:-1:-1:color=black -c:v png -compression_level 2 -pred mixed -pix_fmt rgb24 -sws_flags +accurate_rnd+full_chroma_int "' + os.path.join(out_path[0], out_path[1]) + \
              '\\%6d.png"'
    try:
        if DEBUG:
            print('The Command: ')
            print(command)
        if get_json_state(filepath).get('ahq', null) == null:
            if BETA:
                beta_env = make_beta_environment_variable()
                subprocess.call(command, env=beta_env)
            else:
                subprocess.call(command)
            save_json_state(filepath, 'ahq')
        filepath['-ext'] = 'png'
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
    filepath['-took'] = the_name + ' time: ' + seconds_to_str(ff_end - ff_start)
    if filepath.get('-runtot', None) is not None:
        filepath['-runtot'] = filepath['-runtot'] + (ff_end - ff_start)
    else:
        filepath['-runtot'] = (ff_end - ff_start)
    return filepath


def prot_pass(filepath, filename):
    ff_start = time()
    fext = get_ext(filepath['-ext'])
    filt = ''
    if filepath['-ext'] != 'png':
        filt = ' -sws_flags spline+accurate_rnd+full_chroma_int'
    out_path = (filepath['-path'], filename + 'prot')
    filepath['-out'] = out_path[1]
    filepath['-folders'].append(os.path.join(filepath['-path'], out_path[1]))
    try:
        if not os.path.exists(os.path.join(filepath['-path'], out_path[1])):
            os.mkdir(os.path.join(filepath['-path'], out_path[1]))
        if DEBUG:
            print('Prot Make Folder: ')
            print(os.path.join(filepath['-path'], out_path[1]))
    except OSError as exc:
        if exc.errno != errno.EEXIST:
            raise
        pass
    scale = '2.25'
    if filepath.get('-hd', 'null') != null:
        scale = '1'
    theModel = 'prob-4'
    if filepath.get('-iris', 'null') != null:
        theModel = 'iris-1'
    blend = '0.0'
    if filepath.get('-blend', 'null') != null:
        blend = filepath['-blend']
    if filepath.get('-scale', 'null') != null:
        scale = filepath['-scale']
    if filepath.get('-auto', 'null') != null:
        command = TVAI + ' -hide_banner -stats_period 2.0 -nostdin -y -thread_queue_size 4096 -i "' \
                  + os.path.join(filepath['-path'], filename + fext) + '"' + filt + ' -filter_complex scale=w=' + \
                  filepath['-w'] + ':h=' + filepath['-h'] + ',setsar=1,tvai_up=model=' + theModel + ':scale=' + scale + ':w=0:h=0:preblur=' \
                  '0:noise=0:details=0:halo=0:blur=0:compression=0:estimate=8:blend=' + blend + ':device=0:vram=1:instances=1,scale=w=1920:h=1' \
                  '080:flags=lanczos:threads=0:force_original_aspect_ratio=decrease,pad=1920:1080:-1:-1:color' \
                  '=black -c:v png -compression_level 2 -pred mixed -pix_fmt rgb24 -sws_flags +accurate_rnd+full_chroma_int "' + os.path.join(out_path[0], out_path[1]) + '\\%6d.png"'
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
        command = TVAI + ' -hide_banner -stats_period 2.0 -nostdin -y -i "' \
                  + os.path.join(filepath['-path'], filename + fext) + '"' + filt + ' -filter_complex scale=w=' + \
                  filepath['-w'] + ':h=' + filepath['-h'] + ',setsar=1,tvai_up=model=' + theModel + ':scale=' + scale + ':w=1920:h=1080:prebl' \
                  'ur=' + prot_preblur + ':noise=' + prot_noise + ':details=' + prot_details + ':halo=' + prot_halo + ':blur=' + \
                  prot_blur + ':compression=' + prot_compression + prot_r_t_a + ':blend=' + blend + ':device=0:vram=1:instances=1,scale=' \
                  'w=1920:h=1080:flags=lanczos:threads=0:force_original_aspect_ratio=decrease,pad=1920:1080:-1:-1:color' \
                  '=black -c:v png -compression_level 2 -pred mixed -pix_fmt rgb24 -sws_flags +accurate_rnd+full_chroma_int "' + os.path.join(out_path[0], out_path[1]) + '\\%6d.png"'
    try:
        if DEBUG:
            print('The Command: ')
            print(command)
        if get_json_state(filepath).get('prot', null) == null:
            if BETA:
                beta_env = make_beta_environment_variable()
                subprocess.call(command, env=beta_env)
            else:
                subprocess.call(command)
            save_json_state(filepath, 'prot')
        filepath['-ext'] = 'png'
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
    filepath['-took'] = the_name + ' time: ' + seconds_to_str(ff_end - ff_start)
    if filepath.get('-runtot', None) is not None:
        filepath['-runtot'] = filepath['-runtot'] + (ff_end - ff_start)
    else:
        filepath['-runtot'] = (ff_end - ff_start)
    return filepath


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
    try:
        command = FFMPEG + ' -hide_banner -stats_period 2.0 -nostdin -framerate ' + (get_r(filepath)[4:]) + ' -y -i "' + \
                  os.path.join(filepath['-path'], filename + get_ext(filepath['-ext'])) + '" -c:v libx265 -crf ' + CRF + ' -pix_fmt' \
             ' yuv420p -preset slow -x265-params aq-mode=3 -sws_flags spline+accurate_rnd+full_chroma_int -vf "colo' \
             'rspace=bt709:iall=bt601-6-625:fast=0" -color_range 1 -colorspace 1 -color_primaries 1 -color_trc 1' \
             ' "' + os.path.join(out_path[0], out_path[1] + '.mkv') + '"'
        if filepath['-ext'] != 'png':
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
                os.remove(os.path.join(out_path[0], out_path[1] + '.mkv'))
                if filepath.get('-pt2', null) != null and os.path.exists(os.path.join(out_path[0], out_path[1][:-3] + '.mka')):
                    os.remove(os.path.join(out_path[0], out_path[1][:-3] + '.mka'))
                elif os.path.exists(os.path.join(out_path[0], name + '.mka')):
                    os.remove(os.path.join(out_path[0], name + '.mka'))
            if filepath.get('-appendcommand', null) != null:
                if os.path.exists(os.path.join(out_path[0], name + ' pt1 AI1.mkv')) and os.path.exists(os.path.join(out_path[0], name + ' pt2 AI1.mkv')):
                    append_command = make_append_command(filepath)
                    if DEBUG:
                        print('Append command: ')
                        print(append_command)
                    if get_json_state(filepath).get('append', null) == null:
                        subprocess.call(append_command)
                        save_json_state(filepath, 'append')
                    if filepath.get('-cleanmerge', null) != null:
                        os.remove(os.path.join(out_path[0], name + ' pt1 AI1.mkv'))
                        os.remove(os.path.join(out_path[0], name + ' pt2 AI1.mkv'))
    except:
        return (False, traceback.format_exc())
    if filepath.get('-clean', null) != null:
        pt2 = ''
        if filepath['-pass2']:
            pt2 = 'pt2'
        if os.path.exists(os.path.join(filepath['-path'], filepath['-file'] + pt2 + '_run.json')):
            os.remove(os.path.join(filepath['-path'], filepath['-file'] + pt2 + '_run.json'))
        remove_some_file(filepath, filepath['-file'] + pt2 + 'ff')
    return (True, out_path[1])


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
            print('Removed ' + str(i_num) + ' images.')
            the_name = file_path['-file']
            if file_path.get('-name', null) != null:
                the_name = file_path['-name']
            print(the_name + '  del time: ' + seconds_to_str(del_end - del_start))
            if len(file_path['-folders']) > 0 and final is True:
                clean_images(file_path, True)


def read_options(optionslist):
    options = {}
    for option in optionslist:
        halves = option.split(' ')
        options[halves[0]] = halves[1].strip()
    return options


def convert_song(file_path):
    if DEBUG:
        print(file_path)
    totstart = time()
    output = (True, file_path['-out'])
    the_name = file_path['-file']
    if file_path.get('-name', null) != null:
        the_name = file_path['-name']
    if file_path.get('-fin', null) != null:
        finstart = time()
        output = final_pass(file_path, output[1])
        finend = time()
        print(the_name + '  fin time: ' + seconds_to_str(finend - finstart))
    if DEBUG:
        print('reco done: ' + output[1])
    clean_images(file_path, True)
    totend = time()
    print('Total ' + the_name + ' time: ' + seconds_to_str(file_path.get('-runtot', 0.0) + (totend - totstart)) + '\n')
    return output


def populate_options(file_path):
    ext = file_path[1][-3:]
    newpath = file_path[1][:-4]
    if os.path.exists(os.path.join(file_path[0], newpath + '.json')):
        print('Starting: ' + newpath)
        run_file = open(os.path.join(file_path[0], newpath + '.json'), 'r')
        the_way = json.load(run_file)
    elif os.path.exists(os.path.join(file_path[0], newpath + '.txt')):
        print('Starting: ' + newpath)
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
    dar = get_dar(the_way, ext)
    if DEBUG:
        print(dar)
    the_way['-w'] = dar[0]
    the_way['-h'] = dar[1]
    the_way['-ext'] = ext
    if the_way.get('-name', null) != null:
        the_way['-name'] = the_way['-name'].replace('_', ' ')
    if the_way.get('-crf', null) != null:
        global CRF
        CRF = the_way['-crf']
    the_way['-mkapath'] = os.path.join(file_path[0], file_path[1])
    if the_way.get('-r', null) == null:
        print('You forgot -r!')
        return None
    return the_way


def run_ff(q, out, repo):
    while True:
        if q.empty():
            break
        king = q.get()
        if king.get('-ff', null) != null:
            out.put(ff_pass(king))
        else:
            out.put(king)
        repo.put((king.get('-took', 'ff 00:00:00'), king.get('-runtot', 0.0)))
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
        if the_way.get('-apo', null) != null or the_way.get('-apf', null) != null or the_way.get('-chr', null) != null or the_way.get('-chf', null) != null:
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
    return str(width), str(height)


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
        'clip = havsfunc.QTGMC(Input=clip, Preset="Placebo", TFF=' + TFF + ')\n' #\
        #'clip = core.std.SetFieldBased(clip, ' + field +')\n'
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
    denoise_level = '1.0'
    source_noise_type = '0'
    sigma = '2.0'
    if the_way.get('-denoiselevel', null) != null:
        denoise_level = the_way['-denoiselevel']
        sigma = the_way['-denoiselevel']
    if the_way.get('-noisesigma', null) != null:
        sigma = the_way['-noisesigma']
    if the_way.get('-sourcenoisetype', null) != null:
        source_noise_type = the_way['-sourcenoisetype']
    decimate = ''
    # if the_way.get('-decimate', null) != null:
    #     decimate = 'clip = core.vivtc.VDecimate(clip , cycle=5, chroma=0)\n'
    #     ofps = '24000'
    the_script = 'import os\nimport sys\nimport vapoursynth as vs\ncore = vs.core\n' \
                 'import havsfunc\nclip = core.lsmas.LWLibavSource(source="' + the_way['-path'].replace('\\', '/') + '/' + the_file + '.' \
                 + the_way['-ext'] + '", format="YUV420P8", stream_index=0, cache=0, prefer_hw=0)\n' \
                 'clip = core.std.SetFrameProps(clip, _Matrix=5)\n' \
                 'clip = clip if not core.text.FrameProps(clip,"_Transfer") else core.std.SetFrameProps(clip, _Transfer=5)\n' \
                 'clip = clip if not core.text.FrameProps(clip,"_Primaries") else core.std.SetFrameProps(clip, _Primaries=5)\n' \
                 'clip = core.std.SetFrameProp(clip=clip, prop="_ColorRange", intval=1)\n' \
                 'clip = core.std.AssumeFPS(clip=clip, fpsnum=' + ifps + ', fpsden=' + fpsden + ')\n' \
                 + deinterlace + \
                 'clip = havsfunc.QTGMC(Input=clip, Preset="Very Slow", TFF=' + TFF + ', NoiseProcess=1, NoiseRestore=0.0, DenoiseMC=True, NoiseTR=2, Sigma=' + sigma + ')\n' \
                 + decimate + 'clip = clip[::2]\n' \
                 'clip = core.std.AssumeFPS(clip=clip, fpsnum=' + ofps + ', fpsden=' + fpsden + ')\nclip.set_output()\n'
    f_out_put = open(os.path.join(the_way['-path'], the_file + '.vpy'), 'w')
    f_out_put.write(the_script)
    f_out_put.close()


def make_merge_command(the_way, filename):
    the_command = MKVMERGE + ' ' + the_way['-mergecommand'].replace('~', ' ')
    the_command = the_command.replace('rxx1', os.path.join(the_way['-path'], filename + '.mkv'))
    the_command = the_command.replace('rxxPt1', os.path.join(the_way['-path'], filename + '.mkv'))
    the_command = the_command.replace('rxxOrigin', os.path.join(the_way['-path'], the_way['-file'] + '.mkv'))
    # the_command = the_command.replace('rxx2', os.path.join(the_way['-path'], the_way['-mkaname'] + '.mka'))
    the_command = the_command.replace('rxx2', the_way['-mkapath'])
    the_command = the_command.replace('rxxMka', the_way['-mkapath'])
    if the_way.get('-pt2', null) != null:
        the_command = the_command.replace('rxx3', os.path.join(the_way['-path'], filename + '1.mkv'))
        the_command = the_command.replace('rxxOut', os.path.join(the_way['-path'], filename + '1.mkv'))
    else:
        if the_way.get('-name', null) != null:
            the_command = the_command.replace('rxx3', os.path.join(the_way['-path'], the_way['-name'] + '.mkv'))
            the_command = the_command.replace('rxxOut', os.path.join(the_way['-path'], the_way['-name'] + '.mkv'))
            the_command = the_command.replace('rxx4', the_way['-name'])
            the_command = the_command.replace('rxxTitle', the_way['-name'])
        else :
            the_command = the_command.replace('rxx3', os.path.join(the_way['-path'], the_way['-file'] + '.mkv'))
            the_command = the_command.replace('rxxOut', os.path.join(the_way['-path'], the_way['-file'] + '.mkv'))
            the_command = the_command.replace('rxx4', the_way['-file'])
            the_command = the_command.replace('rxxTitle', the_way['-file'])
    return the_command


def make_append_command(the_way):
    the_command = MKVMERGE + ' ' + the_way['-appendcommand'].replace('~', ' ')
    if the_way.get('-name', null) != null:
        name = the_way['-name']
    else:
        name = the_way['-file']
    the_command = the_command.replace('rxx3', os.path.join(the_way['-path'], name + '.mkv'))
    the_command = the_command.replace('rxx1', os.path.join(the_way['-path'], name + ' pt1 AI1.mkv'))
    the_command = the_command.replace('rxx2', os.path.join(the_way['-path'], name + ' pt2 AI1.mkv'))
    the_command = the_command.replace('rxx4', name)
    the_command = the_command.replace('rxxOut', os.path.join(the_way['-path'], name + '.mkv'))
    the_command = the_command.replace('rxxPt1', os.path.join(the_way['-path'], name + ' pt1 AI1.mkv'))
    the_command = the_command.replace('rxxPt2', os.path.join(the_way['-path'], name + ' pt2 AI1.mkv'))
    the_command = the_command.replace('rxxTitle', name)
    return the_command


def remove_some_file(filepath, filename):
    if filename[-2:] == 'ff' or filename[-3:] == 'vpy':
        if os.path.exists(os.path.join(filepath['-path'], filename[:-5] + 'ff.mkv')):
            os.remove(os.path.join(filepath['-path'], filename[:-5] + 'ff.mkv'))
        if os.path.exists(os.path.join(filepath['-path'], filename[:-3] + 'vpy.mkv')):
            os.remove(os.path.join(filepath['-path'], filename[:-3] + 'vpy.mkv'))
        if os.path.exists(os.path.join(filepath['-path'], filename[:-2] + 'ff.mkv')):
            os.remove(os.path.join(filepath['-path'], filename[:-2] + 'ff.mkv'))
        if os.path.exists(os.path.join(filepath['-path'], filename[:-2] + ' ff.mkv')):
            os.remove(os.path.join(filepath['-path'], filename[:-2] + ' ff.mkv'))


def get_json_state(filepath):
    pt2 = ''
    if filepath['-pass2']:
        pt2 = 'pt2'
    state = {}
    if os.path.exists(os.path.join(filepath['-path'], filepath['-file'] + pt2 + '_run.json')):
        state_file = open(os.path.join(filepath['-path'], filepath['-file'] + pt2 + '_run.json'), 'r')
        state = json.load(state_file)
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


def make_beta_environment_variable():
    beta_env = os.environ.copy()
    beta_env["TVAI_MODEL_DIR"] = 'C:\\ProgramData\\Topaz Labs LLC\\Topaz Video AI Beta\\models'
    return beta_env


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
        ffinput = JoinableQueue()
        fftimes = JoinableQueue()
        for dude in qTheStack:
            option = populate_options(dude)
            if option is not None:
                OptionsStack.append(option)
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
        AmountLoop.sort(key=lambda item: (item['-sort']), reverse=True)
        print(str(len(AmountLoop)) + ' Things loaded.')
        for video in AmountLoop:
            ffinput.put(video)
        ff_out_put = JoinableQueue()
        for i in range(FFNUM):
            worker = Process(target=run_ff, args=(ffinput, ff_out_put, fftimes))
            worker.daemon = True
            worker.start()
        for Bool in AmountLoop:
            say = fftimes.get()
            print(say[0])
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
        print('Starting AMQ.')
        for i in range(TVAINUM):
            worker = Process(target=run_amq, args=(amqinput, amqoutput, amqtimes))
            worker.daemon = True
            worker.start()
        for Bool in AmountLoop:
            say = amqtimes.get()
            print(say[0])
            print('Running total: ' + seconds_to_str(say[1]) + '\n')
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
        print('Starting Prot and AHQ.')
        for i in range(TVAINUM):
            worker = Process(target=run_prot, args=(apoinput, apooutput, apotimes))
            worker.daemon = True
            worker.start()
        for Bool in AmountLoop:
            say = apotimes.get()
            print(say[0])
            print('Running total: ' + seconds_to_str(say[1]) + '\n')
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
        print('Starting APO.')
        for i in range(APONUM):
            worker = Process(target=run_apo, args=(protinput, protoutput, prottimes))
            worker.daemon = True
            worker.start()
        for Bool in AmountLoop:
            say = prottimes.get()
            print(say[0])
            print('Running total: ' + seconds_to_str(say[1]) + '\n')
            prottimes.task_done()
        protinput.join()
        print('Starting Fin.')
        while not protoutput.empty():
            blh = protoutput.get()
            smite = str(itemcount)
            if len(smite) < 2:
                smite = '0' + smite
            deets = convert_song(blh)
            if not deets[0]:
                print(smite + ': ' + deets[1])
            printcount = printcount - 1
            if printcount == 0:
                bend = time()
                print(smite + ': ' + seconds_to_str(bend - bstart))
                bstart = bend
                printcount = 1000
            itemcount = itemcount + 1
            protoutput.task_done()
        end = time()
        print('Total time: ' + seconds_to_str(end - start))
    else:
        print('Sorry, not going to work.')
