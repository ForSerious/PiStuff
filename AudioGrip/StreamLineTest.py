import os
import sys
import subprocess
import traceback
from dMC import Converter
from multiprocessing import Process, Queue, Pool
from tinytag import TinyTag

DEBUG = True

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
        command = '"C:\\Program Files\\dBpoweramp\\CoreConverter.exe" -infile="' + tags[0] + '" -outfile="C:\\U' \
                  'sers\\Peasant\\Desktop\\Process\\Batch\\' + tags[1] + tags[2] + ' - ' + tags[4] + ' - ' + tags[5] +\
                  '.wav" -convert_to="Wave" -dspeffect1="Bit Depth=-depth={qt}32 float{qt}"-dspeffect2="Resample=-fre' \
                  'quency={qt}48000{qt}" -dspeffect3="ID Tag Processing=-delsingle0={qt}<>{qt} -delsingle1={qt}<DYN' \
                  'AMIC RANGE>{qt} -delsingle2={qt}<FOOBAR2000/DYNAMIC RANGE>{qt} -delsingle3={qt}<ALBUM DYNAMIC RA' \
                  'NGE>{qt} -delsingle4={qt}ALBUM DYNAMIC RANGE{qt} -delsingle5={qt}DYNAMIC RANGE{qt} -delsingle6={' \
                  'qt}FOOBAR2000/ALBUM DYNAMIC RANGE{qt} -delsingle7={qt}FOOBAR2000/DYNAMIC RANGE{qt} -add0={qt}Co' \
                  'mment=Declipped: ' + sts + '08{qt} -case={qt}0{qt} -exportart={qt}(none){qt} -importart' \
                  '={qt}(none){qt} -maxart={qt}(any){qt} -maxartkb={qt}(any){qt}"'
        if DEBUG:
            print('To wav 32 command')
            print(command)
        subprocess.call(command)
    except:
        return (False, traceback.format_exc())
    try:
        command = '"G:\\stereo_tool_cmd.exe" "C:\\Users\\Peasant\\Desktop\\Process\\Batch\\' + tags[1] + tags[2] + \
                  ' - ' + tags[4] + ' - ' + tags[5] + '.wav" "C:\\Users\\Peasant\\Desktop\\Process\\Batch\\' + tags[1] \
                  + tags[2] + ' - ' + tags[4] + ' - ' + tags[5] + '.wav" -s G:\\' + sts + '.sts -1 -r 48000 -b 32f -k "' \
                                                                                          '<3f1ca7d95f71983602e58101812939c173f5b1992131d9e728ed858371c433b8>"'
        if DEBUG:
            print('Stereo Tool command')
            print(command)
        subprocess.call(command)
    except:
        return (False, traceback.format_exc())
    if tags[1] == 'ZZ':
        return (False, 'Dummy file.')
    else:
        return (True, 'C:\\Users\\Peasant\\Desktop\\Process\\Batch\\' + tags[1] + tags[2] + ' - ' + tags[4] + ' - ' + tags[5] + \
                '.wav')

'''Create the command to convert to flac'''
def convert_to_flac(tags):
    try:
        command = '"C:\\Program Files\\dBpoweramp\\CoreConverter.exe"' + ' -infile="' + tags[0] + '" -outfile="G:\\Clip\\CDN-48kHz\\' + tags[1] + '\\' + tags[2] + ' - ' + tags[3] + '\\' + \
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
        if DEBUG:
            print('Back to Flac command')
            print(command)
        subprocess.call(command)
    except:
        return (False, traceback.format_exc())
    return (True, tags[1] + ' - ' + tags[5])

'''Create the command to run ReComp'''
def reco_file(tags, converter):
    if tags[9] is None:
        try:
            command = '"C:\\Program Files\\dBpoweramp\\CoreConverter.exe"' + ' -infile="' + tags[0] + '" -outfile="C:\\' \
                                                                                                      'Users\\Peasant\\Desktop\\Process\\ReComp\\' + tags[1] + tags[2] + ' - ' + tags[4] + ' - ' + tags[5] \
                      + '.wav" -convert_to="Wave" -dspeffect1="Bit Depth=-depth={qt}16{qt} -dither={qt}tpdf{qt}"'
            if DEBUG:
                print('To wav 16 in recomp command')
                print(command)
            subprocess.call(command)
        except:
            return (False, traceback.format_exc())
        try:
            command = '"C:\\Program Files\\Java\\jre-1.8\\bin\\java.exe" -jar "C:\\Users\\Peasant\\Desktop\\Process' \
                      '\\comp.jar" "C:\\Users\\Peasant\\Desktop\\Process\\ReComp\\' + tags[1] + tags[2] + ' - ' + tags[4] + \
                      ' - ' + tags[5] + '.wav" "C:\\Users\\Peasant\\Desktop\\Process\\ReComp\\' + tags[1] + tags[2] + ' - ' \
                      + tags[4] + ' - ' + tags[5] + '.wav" "C:\\Users\\Peasant\\Desktop\\Process\\Controls\\ReComp.log" 8'
            subprocess.call(command)
        except:
            return (False, traceback.format_exc())
        tags[0] = 'C:\\Users\\Peasant\\Desktop\\Process\\ReComp\\' + tags[1] + tags[2] + ' - ' + tags[4] + ' - ' + \
                  tags[5] + '.wav'
        return convert_to_flac(tags)
    else:
        return convert_to_flac(tags)

##Pull all the needed tags from the song to create the commands needed to convert.
def convert_song(file_path):
    if DEBUG:
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
    if DEBUG:
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
    if DEBUG:
        print('wav 32 done:')
        print(tags[0])
    output = reco_file(tags, converter)
    if DEBUG:
        print('reco done: ' + tags[0])
        #print(tags[0])
    return output[1]

if __name__ == '__main__':
    if len(sys.argv) <= 1:
        print('Reading artists.')
        predir = 'G:\\Vault\\The Music\\'
        artistfile = open('C:\\Users\\Peasant\\Desktop\\Process\\Controls\\ArtistList.txt', 'r', -1, 'utf-8')
        artistlist = artistfile.readlines()
        dirs = []
        for artist in artistlist:
            if DEBUG:
                print(artist.strip())
            dirs.append(predir + artist.strip())
        qTheStack = []
        for currentPath in dirs:
            print(repr(currentPath))
            for wFile in generate_next_file(currentPath):
                print(repr(wFile))
                #print(convert_song(wFile))
                qTheStack.append(wFile)
        qTheStack = sorted(qTheStack, key = lambda x: TinyTag.get(x, False).duration, reverse=True)
        if DEBUG:
            for elem in qTheStack:
                print(elem)
        de = 0
        #for dummy in generate_next_file('C:\\Users\\Peasant\\Desktop\\Starters'):
            #qTheStack.insert(de, dummy)
            #de = de + 1
        print('List loaded.')
        for thing in qTheStack:
            #print(repr(thing))
            print(convert_song(thing))
        #print('List loaded.')
        #pool = Pool(12)
        #result = pool.map(convert_song, qTheStack)
        #for item in result:
            #print(item)
        logPath = 'C:\\Users\\Peasant\\Desktop\\Process\\Controls\\Recomp.log'
        if os.path.exists(logPath):
            os.startfile(logPath)
    else:
        convert_song(os.path.join(sys.argv[1]))
