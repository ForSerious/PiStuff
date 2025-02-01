import os
import sys
import json
import copy
from datetime import timedelta
from time import time, strftime, localtime

DEBUG = False
null = 'null'
OVERRIDEFILE = 'G:\\Code\\PiStuff\\VideoGrip\\Options.txt'
TEMPLATE = 'G:\\Code\\PiStuff\\VideoGrip\\Template.json'
FOLDERS = 'G:\\Code\\PiStuff\\VideoGrip\\MigrateList.txt'
PREDIR = 'G:\\Vault\\ShowFiles\\'


def generate_next_file(rootdir):
    for path, dirlist, filelist in os.walk(rootdir):
        for fn in filelist:
            if '~' not in fn and (fn.endswith('.txt') or fn.endswith('.json')):
                yield (path, fn)


def seconds_to_str(elapsed=None):
    if elapsed == None:
        return strftime("%Y-%m-%d %H:%M:%S", localtime())
    else:
        return str(timedelta(seconds=elapsed))[:-4]


def read_options(optionslist):
    options = {}
    for option in optionslist:
        halves = option.split(' ')
        options[halves[0]] = halves[1].strip()
    return options


def populate_options(file_path):
    inQuestion = os.path.join(file_path[0], file_path[1])
    if os.path.exists(inQuestion):
        optionsFile = open(inQuestion, 'r', -1, 'utf-8')
        if inQuestion.endswith('txt'):
            optionslist = optionsFile.readlines()
            the_way = read_options(optionslist)
        else:
            the_way = json.load(optionsFile)
        if the_way.get('-name', null) != null:
            the_way['-name'] = the_way['-name'].replace('_', ' ')
        return the_way
    else:
        print('You need to make an options file.')
        print(file_path)
        return None


def open_template():
    if os.path.exists(TEMPLATE):
        print('Opening template')
        templateFile = open(TEMPLATE, 'r')
        jsontemplate = json.load(templateFile)
        return jsontemplate
    else:
        print('Could not find the template file!')
        return None


def open_overrides():
    if os.path.exists(OVERRIDEFILE):
        print('Opening overrides')
        overrideFile = open(OVERRIDEFILE, 'r', -1, 'utf-8')
        optionslist = overrideFile.readlines()
        over = read_options(optionslist)
        return over
    else:
        print('Could not find the override file!')
        return None


if __name__ == '__main__':
    if len(sys.argv) <= 1:
        start = time()
        the_template = open_template()
        the_overrides = open_overrides()
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
        print(str(len(qTheStack)) + ' Things loaded.')
        itemcount = 0
        printcount = 1001
        bstart = time()
        OptionsStack = []
        AmountLoop = []
        for dude in qTheStack:
            option = populate_options(dude)
            if option is not None:
                OptionsStack.append((option, dude))
        for optionFile in OptionsStack:
            temp_template = copy.deepcopy(the_template)
            temp_template['-name'] = optionFile[0].get('-name', null)
            if the_overrides.get('name', null) != null:
                new_title = optionFile[0]['-name'][9:]
            else:
                new_title = optionFile[0]['-name']
            if the_overrides.get('ss', null) != null:
                new_ss_value = optionFile[0].get('-ss', null)
                new_ss2_value = optionFile[0].get('-ss2', null)
                if new_ss_value != null:
                    temp_template['-ss'] = new_ss_value
                else:
                    temp_template.pop('-ss', None)
                if new_ss2_value != null:
                    temp_template['-ss2'] = new_ss2_value
                else:
                    temp_template.pop('-ss2', None)
            if the_overrides.get('t', null) != null:
                new_t_value = optionFile[0].get('-t', null)
                new_t2_value = optionFile[0].get('-t2', null)
                if new_t_value != null:
                    temp_template['-t'] = new_t_value
                else:
                    temp_template.pop('-t', None)
                if new_t2_value != null:
                    temp_template['-t2'] = new_t2_value
                else:
                    temp_template.pop('-t2', None)
            new_pt2_value = optionFile[0].get('-pt2', null)
            if new_pt2_value == null:
                temp_template.pop('-pt2', None)
            if the_overrides.get('merge', null) != null:
                new_merge_value = optionFile[0].get('-mergecommand', null)
                new_append_value = optionFile[0].get('-appendcommand', null)
                new_merge_value = new_merge_value.replace('rxxTitle', new_title)
                new_append_value = new_append_value.replace('rxxTitle', new_title)
                new_merge_value = new_merge_value.replace('rxx4', new_title)
                new_append_value = new_append_value.replace('rxx4', new_title)
                if new_merge_value != null:
                    temp_template['-mergecommand'] = new_merge_value
                else:
                    temp_template.pop('-mergecommand', None)
                if new_append_value != null:
                    temp_template['-appendcommand'] = new_append_value
                else:
                    temp_template.pop('-appendcommand', None)
            else:
                new_merge_value = temp_template.get('-mergecommand', null)
                new_append_value = temp_template.get('-appendcommand', null)
                old_merge_value = optionFile[0].get('-mergecommand', null)
                old_append_value = optionFile[0].get('-appendcommand', null)
                if old_merge_value != null:
                    if new_merge_value != null:
                        new_merge_value = new_merge_value.replace('rxxTitle', new_title)
                        temp_template['-mergecommand'] = new_merge_value
                else:
                    temp_template.pop('-mergecommand', None)
                if old_append_value != null:
                    if new_append_value != null:
                        new_append_value = new_append_value.replace('rxxTitle', new_title)
                        temp_template['-appendcommand'] = new_append_value
                else:
                    temp_template.pop('-appendcommand', None)
            paths = optionFile[1]
            ext = paths[1][-3:]
            add = ''
            if ext == 'txt':
                newname = paths[1][:-4]
            else:
                add = '\\new'
                newname = paths[1][:-5]
            if not os.path.exists(paths[0] + add):
                os.mkdir(os.path.join(paths[0] + add))
            outfile = open(os.path.join(paths[0] + add, newname + '.json'), 'w')
            json.dump(temp_template, outfile, indent=2)
            outfile.close()
        end = time()
        print('Total time: ' + seconds_to_str(end - start))
    else:
        print('Sorry, not going to work.')
