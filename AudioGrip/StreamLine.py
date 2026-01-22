import os
import sys
import subprocess
import traceback
import globals as g
import clrprint
from dMC import Converter
from multiprocessing import Process, JoinableQueue
from time import time, strftime, localtime
from datetime import timedelta


def generate_next_file(rootdir):
    """So, this should generate every file in the rootdir and return them one by one."""
    for path, dirlist, filelist in os.walk(rootdir):
        for fn in filelist:
            if '~' not in fn and (fn.endswith('.wav') or fn.endswith('.flac') or fn.endswith('.wma') or fn.endswith(
                    '.ogg') or fn.endswith('.mp3') or fn.endswith('.m4a') or fn.endswith('.opus')):
                yield os.path.join(path, fn)


def clean_chars(ttag):
    """Replace any characters that cannot be used in the Windows file system."""
    if '?' in ttag:
        ttag = ttag.replace('?', '¿')
        #print(ttag)
    if '"' in ttag:
        ttag = ttag.replace('"', "'")
    if ':' in ttag:
        ttag = ttag.replace(':', ';')
    if '\\' in ttag:
        ttag = ttag.replace('\\', '-')
    if '/' in ttag:
        ttag = ttag.replace('/', '-')
    if '*' in ttag:
        ttag = ttag.replace('*', '-')
    if '|' in ttag:
        ttag = ttag.replace('|', '-')
    if '>' in ttag:
        ttag = ttag.replace('>', '-')
    if '<' in ttag:
        ttag = ttag.replace('<', '-')
    return ttag


def clean_zeros(number):
    """Remove any leading zeros. Clean out the 'x's"""
    if number is not None:
        while number[0] == '0':
            number = number[1:]
        return number.replace('x', '')
    else:
        return number


def convert_to_32_wav(tags):
    """Create the command to convert to 32 bit wav. Create the command to process with stereo tool."""
    sts = 'H'
    if tags[10] is not None:
        sts = tags[10]
    try:
        command = g.DBPOWER + ' -infile="' + tags[0] + \
                  '" -outfile="' + g.DBOUTPATH + tags[1] + tags[2] + ' - ' + \
                  tags[4] + ' - ' + tags[5] + '.wav" -convert_to="Wave" -dspeffect1="Bit Depth=-depth={qt}32 float{qt}"' \
                  '-dspeffect2="Resample=-frequency={qt}48000{qt}" -dspeffect3="ID Tag' \
                  ' Processing=-delsingle0={qt}<>{qt} -delsingle1={qt}<DYNAMIC RANGE>{qt}' \
                  ' -delsingle2={qt}<FOOBAR2000/DYNAMIC RANGE>{qt} -delsingle3={qt}<ALBUM' \
                  ' DYNAMIC RANGE>{qt} -delsingle4={qt}ALBUM DYNAMIC RANGE{qt} -delsingle5' \
                  '={qt}DYNAMIC RANGE{qt} -delsingle6={qt}FOOBAR2000/ALBUM DYNAMIC RANGE{' \
                  'qt} -delsingle7={qt}FOOBAR2000/DYNAMIC RANGE{qt} -add0={qt}Comment=' \
                  'Declipped: ' + sts + g.VERSION_NUMBER + '{qt} -case={qt}0{qt} -exportart={qt}(none){qt} -importart' \
                  '={qt}(none){qt} -maxart={qt}(any){qt} -maxartkb={qt}(any){qt}"'
        if g.DEBUG:
            print('To wav 32 command')
            print(command)
        subprocess.call(command)
    except:
        return (False, traceback.format_exc())
    try:
        command = (g.STTOOL + ' "' + g.DBOUTPATH + tags[1] + tags[2] + ' - ' + tags[4] + ' - ' + tags[5] + '.wav" "' +
                   g.DBOUTPATH + tags[1] + tags[2] + ' - ' + tags[4] + ' - ' + tags[5] + '.wav" -s ' + g.STSPATH + sts +
                   '.sts -1 -r 48000 -b 32f -k "' + g.STEREOKEY + '"')
        if g.DEBUG:
            print('Stereo Tool command')
            print(command)
        subprocess.call(command)
    except:
        return (False, traceback.format_exc())
    if tags[1] == 'ZZ':
        return (False, 'Dummy file.')
    else:
        return (True, g.DBOUTPATH + tags[1] + tags[2] + ' - ' + tags[4] + ' - ' + tags[5] + '.wav')


def convert_to_flac(tags):
    """Create the command to convert to flac"""
    try:
        command = g.DBPOWER + ' -infile="' + tags[0] + '" -outfile="' + g.FINALOUT + tags[1] + '\\' + tags[2] + ' - ' + tags[3] + '\\' + \
                  tags[4] + ' - ' + tags[5] + '.flac" -convert_to="FLAC" -compression-level-8 -dspeffect1="Bit ' \
            'Depth=-depth={qt}32 float{qt}" -dspeffect2="Volume Normalize=-mode={qt}ebu{qt} -maxamp={qt}8{qt}'\
            ' -desiredb={qt}' + tags[6] + '{qt} -adapt_wnd={qt}6000{qt} -fixed={qt}0{qt}" -dspeffect3="Bit'\
            ' Depth=-depth={qt}16{qt} -dither={qt}tpdf{qt}"'
        if tags[8] is not None:
            command = command + ' -dspeffect4="Trim=-lengthms={qt}' + tags[8] + '{qt} -end"'
        if tags[7] is not None:
            if tags[8] is None:
                command = command + ' -dspeffect4="Trim=-lengthms={qt}' + tags[7] + '{qt}"'
            else:
                command = command + ' -dspeffect5="Trim=-lengthms={qt}' + tags[7] + '{qt}"'
        if g.DEBUG:
            print('Back to Flac command')
            print(command)
        subprocess.call(command)
    except:
        return (False, traceback.format_exc())
    return (True, tags[1] + ' - ' + tags[5])


def reco_file(tags):
    """Create the command to run ReComp"""
    if tags[9] is None:
        try:
            command = g.DBPOWER + ' -infile="' + tags[0] + '" -outfile="' + g.RECOMPPATH + tags[1] + tags[2] + ' - ' + tags[4] + ' - ' + tags[5]\
                      + '.wav" -convert_to="Wave" -dspeffect1="Bit Depth=-depth={qt}16{qt} -dither={qt}tpdf{qt}"'
            if g.DEBUG:
                print('To wav 16 in recomp command')
                print(command)
            subprocess.call(command)
        except:
            return (False, traceback.format_exc())
        try:
            command = g.JAVAPATH + ' -jar ' + g.COMPJARPATH + ' "' + g.RECOMPPATH + tags[1] + tags[2] + ' - ' + tags[4] +\
                      ' - ' + tags[5] + '.wav" "' + g.RECOMPPATH + tags[1] + tags[2] + ' - '\
                      + tags[4] + ' - ' + tags[5] + '.wav" "' + g.LOGPATH + '" 8'
            subprocess.call(command)
        except:
            return (False, traceback.format_exc())
        tags[0] = g.RECOMPPATH + tags[1] + tags[2] + ' - ' + tags[4] + ' - ' + tags[5] + '.wav'
        return convert_to_flac(tags)
    else:
        return convert_to_flac(tags)


def convert_song(file_path):
    """Pull all the needed tags from the song to create the commands needed to convert."""
    startConvert = time()
    if g.DEBUG:
        print(file_path)
    converter = Converter()
    element = ''
    tagval = ''
    i_at = 1
    artist_tag = None
    year = None
    album = None
    track = None
    title = None
    rawgain = None
    trim = None
    trim2 = None
    reco = None
    sts = None
    testval = converter.ReadIDTag(file_path, 0, element, tagval)
    if testval[0].lower() == 'reco':
        reco = testval[1]
    if testval[0].lower() == 'trim':
        trim = testval[1]
    if testval[0].lower() == 'trim2':
        trim2 = testval[1]
    if testval[0].lower() == 'gain':
        rawgain = testval[1]
    if testval[0].lower() == 'album':
        album = testval[1]
    if testval[0].lower() == 'artist':
        artist_tag = testval[1]
    if testval[0].lower() == 'title':
        title = testval[1]
    if testval[0].lower() == 'track':
        track = testval[1]
    if testval[0].lower() == 'year':
        year = testval[1]
    if testval[0].lower() == 'sts':
        sts = testval[1]
    while testval[0].lower() != '':
        testval = converter.ReadIDTag(file_path, i_at, element, tagval)
        i_at = i_at + 1
        # print('testval ' + testval[0].lower() + ': ' + testval[1])
        if testval[0].lower() == 'reco':
            reco = testval[1]
        if testval[0].lower() == 'trim':
            trim = testval[1]
        if testval[0].lower() == 'trim2':
            trim2 = testval[1]
        if testval[0].lower() == 'gain':
            rawgain = testval[1].replace('x', '')
        if testval[0].lower() == 'album':
            album = testval[1]
        if testval[0].lower() == 'artist':
            artist_tag = testval[1]
        if testval[0].lower() == 'title':
            title = testval[1]
        if testval[0].lower() == 'track':
            track = testval[1]
        if testval[0].lower() == 'year':
            year = testval[1]
        if testval[0].lower() == 'sts':
            sts = testval[1]
    if g.DEBUG:
        print("Reco: " + str(reco))
        print("Trim Back: " + str(trim))
        print("Trim Front: " + str(trim2))
        print("Gain: " + str(rawgain))
        print("sts: " + str(sts))
    album = clean_chars(album)
    title = clean_chars(title)
    artist_tag = clean_chars(artist_tag)
    gain = '0'
    if rawgain is not None:
        gain = rawgain.replace('x', '')
    track_number = track
    if '/' in track_number:
        temp = track_number.split('/')
        track_number = temp[0]
    if len(track_number) < 2:
        track_number = '0' + track_number
    if year is None:
        year = '0000'
    tags = [file_path, artist_tag, year, album, track_number, title, gain, clean_zeros(trim), clean_zeros(trim2), reco, sts]
    output = convert_to_32_wav(tags)
    if output[0]:
        tags[0] = output[1]
    else:
        return [output[1], None]
    if g.DEBUG:
        print('wav 32 done:')
        print(tags[0])
    output = reco_file(tags)
    if g.DEBUG:
        print('reco done: ' + tags[0])
        #print(tags[0])
    endConvert = time()
    timeTaken = endConvert - startConvert
    return ['Took: ' + seconds_to_str(timeTaken) + ' ' + output[1], timeTaken]


def run_city(q, out):
    while True:
        if q.empty():
            break
        out.put(convert_song(q.get()))
        q.task_done()
    return out


def seconds_to_str(elapsed=None):
    if elapsed is None:
        return strftime("%Y-%m-%d %H:%M:%S", localtime())
    else:
        return str(timedelta(seconds=elapsed))[:-7]


def duration_compare(file_path):
    if 'converter2' not in locals():
        converter2 = Converter()
    length = converter2.AudioProperties(file_path)
    length = length[(length.find("Length") + 24):(length.find("Length") + 36)]
    return length

if __name__ == '__main__':
    if len(sys.argv) <= 1:
        start = time()
        print('Reading artists.')
        artistfile = open(g.FOLDERLISTPATH, 'r', -1, 'utf-8')
        artistlist = artistfile.readlines()
        dirs = []
        for artist in artistlist:
            if g.DEBUG:
                print(artist.strip())
            dirs.append(g.PREDIR + artist.strip())
        qTheStack = []
        converter2 = Converter()
        for currentPath in dirs:
            for wFile in generate_next_file(currentPath):
                #print(repr(wFile))
                #print(convert_song(wFile))
                qTheStack.append(wFile)
        qTheStack = sorted(qTheStack, key=lambda x: duration_compare(x), reverse=True)
        reduce = 61
        howMany = len(qTheStack)
        if howMany > 9:
            reduce = 60
        if howMany > 99:
            reduce = 59
        if howMany > 999:
            reduce = 58
        if g.DEBUG:
            for elem in qTheStack:
                print(elem)
        de = 0
        for dummy in generate_next_file(g.DUMMYPATH):
            qTheStack.insert(de, dummy)
            de = de + 1
        qInput = JoinableQueue()
        for path in qTheStack:
            qInput.put(path)
        totalNumberOfSongs = str(len(qTheStack) - g.NUMBEROFCORES)
        print(totalNumberOfSongs + ' Songs loaded.')
        qOutput = JoinableQueue()
        for i in range(g.NUMBEROFCORES):
            worker = Process(target=run_city, args=(qInput, qOutput))
            worker.daemon = True
            worker.start()
        itemcount = -(g.NUMBEROFCORES - 1)
        times = []
        color = 'b'
        cycle = 1
        for blh in qTheStack:
            smite = str(itemcount)
            if itemcount == 100:
                reduce = reduce - 1
            if itemcount == 1000:
                reduce = reduce - 1
            if len(smite) < 2:
                smite = '0' + smite
            mess = qOutput.get(True, 33200)
            if(cycle == g.NUMBEROFCORES):
                color = 'g'
                cycle = 0
            if mess[1] is not None:
                times.append(mess[1])
                if len(times) > g.NUMBEROFCORES:
                    times.pop(0)
                tots = 0
                for amount in times:
                    tots = tots + amount
                average = tots / len(times)
                clrprint.clrprint(smite + '/' + totalNumberOfSongs + '|avg: ' + seconds_to_str(average) +'| ' + (mess[0][:reduce]), clr=color)
            else:
                clrprint.clrprint(smite + '/' + totalNumberOfSongs + ': ' + mess[0], clr=color)
            itemcount = itemcount + 1
            cycle = cycle + 1
            if color == 'g':
                color = 'b'
        qInput.join()
        end = time()
        print('Total time: ' + seconds_to_str(end - start))
        if os.path.exists(g.LOGPATH):
            os.startfile(g.LOGPATH)
    else:
        convert_song(os.path.join(sys.argv[1]))
