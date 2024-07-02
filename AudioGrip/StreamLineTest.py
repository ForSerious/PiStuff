import os
import sys
import subprocess
import traceback
import globals as g
from dMC import Converter
from tinytag import TinyTag


'''So, this should generate every file in the rootdir and return them one by one.'''
def generate_next_file(rootdir):
    for path, dirlist, filelist in os.walk(rootdir):
        for fn in filelist:
            if '~' not in fn and (fn.endswith('.wav') or fn.endswith('.flac') or fn.endswith('.wma') or fn.endswith(
                    '.ogg') or fn.endswith('.opus')):
                yield os.path.join(path, fn)

'''Replace any characters that cannot be uses in the Windows file system.'''
def clean_chars(ttag):
    if '?' in ttag:
        ttag = ttag.replace('?', '¿')
        print(ttag)
    if '"' in ttag:
        ttag = ttag.replace('"', "'")
    if ':' in ttag:
        ttag = ttag.replace(':', ';')
    if '/' in ttag:
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

'''Remove any leading zeros. Clean out the xs'''
def clean_zeros(number):
    if number is not None:
        while number[0] == '0':
            number = number[1:]
        return number.replace('x', '')
    else:
        return number

'''Create the command to convert to 32 bit wav. Create the command to process with stereo tool.'''
def convert_to_32_wav(tags):
    sts = 'H'
    if tags[10] is not None:
        sts = tags[10]
    try:
        command = g.DBPOWER + ' -infile="' + tags[0] + '" -outfile="' + g.DBOUTPATH + tags[1] + tags[2] + ' - ' + tags[4] + ' - ' + tags[5] +\
                  '.wav" -convert_to="Wave" -dspeffect1="Bit Depth=-depth={qt}32 float{qt}"-dspeffect2="Resample=-fre' \
                  'quency={qt}48000{qt}" -dspeffect3="ID Tag Processing=-delsingle0={qt}<>{qt} -delsingle1={qt}<DYN' \
                  'AMIC RANGE>{qt} -delsingle2={qt}<FOOBAR2000/DYNAMIC RANGE>{qt} -delsingle3={qt}<ALBUM DYNAMIC RA' \
                  'NGE>{qt} -delsingle4={qt}ALBUM DYNAMIC RANGE{qt} -delsingle5={qt}DYNAMIC RANGE{qt} -delsingle6={' \
                  'qt}FOOBAR2000/ALBUM DYNAMIC RANGE{qt} -delsingle7={qt}FOOBAR2000/DYNAMIC RANGE{qt} -add0={qt}Co' \
                  'mment=Declipped: ' + sts + '08{qt} -case={qt}0{qt} -exportart={qt}(none){qt} -importart' \
                  '={qt}(none){qt} -maxart={qt}(any){qt} -maxartkb={qt}(any){qt}"'
        if g.DEBUG:
            print('To wav 32 command')
            print(command)
        subprocess.call(command)
    except:
        return (False, traceback.format_exc())
    try:
        command = (g.STTOOL + ' "' + g.DBOUTPATH + tags[1] + tags[2] +
                  ' - ' + tags[4] + ' - ' + tags[5] + '.wav" "' + g.DBOUTPATH + tags[1]
                  + tags[2] + ' - ' + tags[4] + ' - ' + tags[5] + '.wav" -s ' + g.PREDIR + sts +
                   '.sts -1 -r 48000 -b 32f -k "' + g.STEREOKEY)
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

'''Create the command to convert to flac'''
def convert_to_flac(tags):
    try:
        command = g.DBPOWER + ' -infile="' + tags[0] + '" -outfile="' + g.FINALOUT + tags[1] + '\\' + tags[2] + ' - ' + tags[3] + '\\' + \
                  tags[4] + ' - ' + tags[5] + '.flac" -convert_to="FLAC" -compression-level-8 -dspeffect1="Bit ' \
                  'Depth=-depth={qt}32 float{qt}" -dspeffect2="Volume Normalize=-mode={qt}ebu{qt} -maxamp={qt}8{qt}' \
                  ' -desiredb={qt}' + tags[6] + '{qt} -adapt_wnd={qt}6000{qt} -fixed={qt}0{qt}" -dspeffect3="Bit' \
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

'''Create the command to run ReComp'''
def reco_file(tags):
    if tags[9] is None:
        try:
            command = g.DBPOWER + ' -infile="' + tags[0] + '" -outfile="' + g.RECOMPPATH + tags[1] + tags[2] + ' - ' + tags[4] + ' - ' + tags[5] \
                      + '.wav" -convert_to="Wave" -dspeffect1="Bit Depth=-depth={qt}16{qt} -dither={qt}tpdf{qt}"'
            if g.DEBUG:
                print('To wav 16 in recomp command')
                print(command)
            subprocess.call(command)
        except:
            return (False, traceback.format_exc())
        try:
            command = g.JAVAPATH + ' -jar ' + g.COMPJARPATH + ' "' + g.RECOMPPATH + tags[1] + tags[2] + ' - ' + tags[4] + \
                      ' - ' + tags[5] + '.wav" "' + g.RECOMPPATH + tags[1] + tags[2] + ' - ' \
                      + tags[4] + ' - ' + tags[5] + '.wav" ' + g.LOGPATH + ' 8'
            subprocess.call(command)
        except:
            return (False, traceback.format_exc())
        tags[0] = g.RECOMPPATH + tags[1] + tags[2] + ' - ' + tags[4] + ' - ' + \
                  tags[5] + '.wav'
        return convert_to_flac(tags)
    else:
        return convert_to_flac(tags)

##Pull all the needed tags from the song to create the commands needed to convert.
def convert_song(file_path):
    if g.DEBUG:
        print(file_path)
    converter = Converter()
    element = ''
    tagval = ''
    i = 1
    artist = None
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
        artist = testval[1]
    if testval[0].lower() == 'title':
        title = testval[1]
    if testval[0].lower() == 'track':
        track = testval[1]
    if testval[0].lower() == 'year':
        year = testval[1]
    if testval[0].lower() == 'sts':
        sts = testval[1]
    while testval[0].lower() != '':
        testval = converter.ReadIDTag(file_path, i, element, tagval)
        i = i + 1
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
            artist = testval[1]
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
    try:
        album = clean_chars(album)
    except:
        song = TinyTag.get(file_path)
        album = clean_chars(song.album)
    try:    
        title = clean_chars(title)
    except:
        song = TinyTag.get(file_path)
        title = clean_chars(song.title)
    try:
        artist = clean_chars(artist)
    except:
        song = TinyTag.get(file_path)
        artist = clean_chars(song.artist)
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
    tags = [file_path, artist, year, album, track_number, title, gain, clean_zeros(trim), clean_zeros(trim2), reco, sts]
    output = convert_to_32_wav(tags)
    if output[0]:
        tags[0] = output[1]
    else:
        return output[1]
    if g.DEBUG:
        print('wav 32 done:')
        print(tags[0])
    output = reco_file(tags)
    if g.DEBUG:
        print('reco done: ' + tags[0])
    return output[1]

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
            for wFile in generate_next_file(currentPath):
                print(repr(wFile))
                #print(convert_song(wFile))
                qTheStack.append(wFile)
        qTheStack = sorted(qTheStack, key=lambda x: TinyTag.get(x, False).duration, reverse=True)
        if g.DEBUG:
            for elem in qTheStack:
                print(elem)
        print('List loaded.')
        for thing in qTheStack:
            #print(repr(thing))
            print(convert_song(thing))
        if os.path.exists(g.LOGPATH):
            os.startfile(g.LOGPATH)
    else:
        convert_song(os.path.join(sys.argv[1]))
