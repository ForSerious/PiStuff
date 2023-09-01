import ctypes

'''So, this should generate every file in the rootdir and return them one by one.'''
def generate_next_file(rootdir):
    for path, dirlist, filelist in os.walk(rootdir):
        for fn in filelist:
            if '~' not in fn and (fn.endswith('.wav') or fn.endswith('.flac') or fn.endswith('.wma') or fn.endswith(
                    '.ogg')) and not fn.endswith('ZZ.wav'):
                yield os.path.join(path, fn)

def convert_song(wFile):
    readDll = ctypes.WinDLL ("C:\\Program Files\\dBpoweramp\\dMCScripting.dll")
    hllApiProto = ctypes.WINFUNCTYPE(ctypes.c_void_p)
    hllApiParams = (1, "p1", 0)
    hllApi = hllApiProto (("Converter", readDll), hllApiParams)
    print(hllApi())

if __name__ == '__main__':
    print('Reading artists.')
    predir = 'G:\\Vault\\The Music\\'
    artistfile = open('C:\\Users\\Peasant\\Desktop\\Process\\Controls\\ArtistList.txt', 'r')
    artistlist = artistfile.readlines()
    dirs = []
    for currentPath in dirs:
        for wFile in generate_next_file(currentPath):
            print(convert_song(wFile))
    print('List loaded.')
