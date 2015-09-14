#! /bin/python2
import re
import pprint
from collections import Counter
from collections import namedtuple
import random 
from warnings import warn
from copy import deepcopy
# from layout_printer import print_layout
# from layout_printer import read_layout


SHIFT_INDEX = 18

def load_log(filename):
    f=open(filename, "r")
    log=f.read()
    f.close()
    #remove logging start/stop timestamp messages and surrounding newlogs
    log=re.sub("\n+[lL]ogging [(started)(stopped)]+ at [-0-9 :]+(> \n\n)?", "x", log)
    log =re.sub("\n", "<ret>", log)
    log =re.sub(" ", "<space>", log)
    #remove +num from repeat marker
    log =re.sub("<#\+[0-9]+>", "<#>", log)
    #split into individual keystrokes
    #ignore some weird characters - don't know how they got there
    log = re.findall(r"(<[A-Za-z#]+>|[^\240\x00\304\212])",log)
    return log

def print_table(freq,factor=1):
    print '______________________'
    for line in freq:
        # print line
        #todo remove temporary <space> filter
        if "<space>" in line[0]:
            continue
        print '\t'.join(line[0])+'\t- '+str(line[1]*factor)
    print '______________________'

def count_freq(log, num):
    l = []
    for i in range(len(log)-num-1):
        l.append(tuple(log[i:i+num]))
    c = Counter(l)
    total = sum(c.values())
    return [(x[0], float(x[1])/total) for x in c.most_common()]

def filter(freq, set_list):
    for i in range(len(set_list)):
        freq = [x for x in freq if (x[0][i] in set_list[i])]
    return freq

def filter2(freq, filters):
    filtered_freq = []
    for f in range(len(filters)):
        # for ngram in freq:
            # print (False not in [x in filters[f] for x in ngram])
            # print ([x for x in ngram[0]])

        freq = [ngram for ngram in freq if (False not in [x in filters[f] for x in ngram[0]])]
    return freq

def get_corpus(debug_corpus=[]):
    if debug_corpus:
        corpus = debug_corpus
    else:
        # log=load_log("/var/log/logkeys.log") # 
        log=load_log("logkeys.log")  #
        mycorpus=load_log("mycorpus.txt")
        # books=load_log("books.short.txt")
        corpus = log
    
    #define key sets
    full=set(corpus)
    len1 = set([x for x in full if len(x)==1 or x=='<space>'])
    alphas = set([chr(x) for x in (range(65, 65+26) + range(97, 97+26))])
    specials = set([x for x in full if len(x)>1 and x!='<space>' and x!='<#>'])
    mods = set(['<rmeta>', '<lshft>', '<esc>', '<rctrl>', '<lalt>', '<rshft>', '<lctrl>'])
    nonmods = full - mods
    moves = set(['<pgdn>', '<pgup>', '<home>', '<end>', '<right>', '<down>', '<up>', '<left>'])
    nums = set([str(x) for x in range(0,10)])
    repeat = set(['<#>'])

    freq1 = count_freq(corpus, 1)
    freq2 = count_freq(corpus, 2)
    freq3 = count_freq(corpus, 3)
  
#   print_table(freq1, factor=1000)  
    # print_table(freq2, factor=1000)  
    # print_table(filter(freq3, [full - set(['<Space>'])]), factor=1000)
#    print_table(freq3, factor=1000)
    # exit()
#    print_table(filter(freq3, [full-mods-moves]))
    # print_table(filter(freq1, [alphas]))
    
    # print_table(filter(freq2, [alphas]))
    print_table(filter(freq2, [alphas]))
    return (dict(freq1), dict(freq3))


def print_layout(layout, all_keys_arranged, filename):    
    f_cfg = open(filename, 'w')
    template=['%s\t\t', '%s%s%s%s   %s%s%s%s\t', '%s%s%s%s   %s%s%s%s\t', '  %s%s%s %s%s%s  \t'] 
    names_to_entries = {}
    for chord in layout.keys():
        for shifted in [0,1]:
            name = layout[chord][shifted]
            if name:
                binary = indices2binary(chord, shifted)
                names_to_entries[name] = [(name,), tuple(binary[0:8]), tuple(binary[8:16]), tuple(binary[16:22])]
                
    str = ""               
    for row in all_keys_arranged:
        # n=len(row)
        for i in range(4):
            for name in row:
                str+= template[i] % names_to_entries[name][i]
            str += '\n'    
        # str += '\n' + '#'*70 + '\n'    
        str += '\n'
    f_cfg.write(str)

def read_layout(filename):
    #todo check for duplicate chord assignments
    f_cfg = open(filename, 'r')
    layout = {}
    while 1:
        lines = []
        while len(lines) < 4:
            l = f_cfg.readline()
            #check for EoF
            if l == "":
                if len(lines) != 0:
                    print "WARNING: lines ignored at end of file"
                return layout

            # skip blank lines and comments    
            if l.strip() == "" or l[0:2].strip() == "//":
                continue

            # shifted version of previously defined chord
            if len(l.split())>1 and l.split()[1].strip() == "shifted":
                if len(lines) != 0:
                    print "WARNING: lines ignored before shifted command"
                unshifted_char = l.split()[2].strip()
                shifted_char = l.split()[0].strip()
                found_unshifted_char = False
                for chord in layout:
                    if layout[chord][0] == unshifted_char:
                        if layout[chord][1]:
                            raise RuntimeError("same chord given for: %s %s" %
                                               (layout[chord][1], shifted_char))
                        layout[chord][1] = shifted_char
                        found_unshifted_char = True
                        break
                if not found_unshifted_char:
                    raise RuntimeError("unknown character referenced in shifted command")
                lines = [] 
            # part of normal chord ascii art
            else:
                lines.append(re.split('[ \t]+', l.strip()))
        for b in range(len(lines[0])):
            chunks = []
            [chunks.extend(lines[row][b*2:b*2+2]) for row in range(1,4)]
            chunks =  ''.join(chunks)            
            (indices, shifted) = binary2indices(chunks)
            try:
                if layout[indices][shifted]:
                    raise RuntimeError("same chord given for: %s %s" %
                                       (layout[indices][shifted],lines[0][b]))
                layout[indices][shifted] =  lines[0][b]
            except KeyError:
                value = ['','']
                value[shifted] = lines[0][b]
                layout[indices] = value
    return layout

def indices2binary(indices, shifted):
    press_symbol = "*"
    binary = ['.']*22
    for i in indices:
        binary[i] = press_symbol
    binary = reorder_optimizer2printer(binary)
    if shifted:
        binary[SHIFT_INDEX] = press_symbol
    return binary

def binary2indices(binary):
    binary = list(binary)
    shifted = binary[SHIFT_INDEX] != '.'
    binary[SHIFT_INDEX] = '.'
    binary = reorder_printer2optimizer(binary)
    indices = tuple([i for i,x in enumerate(binary) if x != '.'])
    # indices = [
    return (indices, shifted)
    
# def reorder_optimizer2original(binary):
    # return [binary[i] for i in [21, 20, 19, 16, 17, 18, 14, 12, 10, 8, 0, 2, 4, 6, 15, 13, 11, 9, 1, 3, 5, 7]]

def reorder_printer2optimizer(binary):
    return [binary[i] for i in [11, 3, 10, 2, 9, 1, 8, 0, 12, 4, 13, 5, 14, 6, 15, 7, 18, 17, 16, 19, 20, 21]]

def reorder_optimizer2printer(binary):
    return [binary[i] for i in [7, 5, 3, 1, 9, 11, 13, 15, 6, 4, 2, 0, 8, 10, 12, 14, 18, 17, 16, 19, 20, 21]]


def make_reverse_layout(layout):
    reverse = {}
    for chord in layout.keys():
        for character in layout[chord]:
            reverse[character] = chord
            # reverse[character] = chord
    return reverse

def get_constants():
    #this structure is used by layout_printer to arrange the keys on the page
    all_keys_arranged = [["a", "A", "b", "B"], ["c", "C", "d", "D"], ["e", "E", "f", "F"], ["g", "G", "h", "H"], ["i", "I", "j", "J"], ["k", "K", "l", "L"], ["m", "M", "n", "N"], ["o", "O", "p", "P"], ["q", "Q", "r", "R"], ["s", "S", "t", "T"], ["u", "U", "v", "V"], ["w", "W", "x", "X"], ["y", "Y", "z", "Z"], ["<right>", "<left>", "<down>", "<up>"],[ "<home>", "<end>","<pgdn>", "<pgup>"], ["1", "2", "3", "4"], ["5", "6", "7", "8"], ["9", "0", "<del>", "<tab>"],  ["!", "@", "#", "$"], ["%", "^", "&", "*"], ["-", "_", "=", "+"], ["\\",  "|", ";",  ":"],  ["\'", '\"',  r"`", "~"], [",", "<", ".", ">"], [r"/", "?", "[", "{"], ["(", "<cpslk>"], ["f1", "f2", "f3", "f4"], ["f5", "f6", "f7", "f8"], ["f9", "f10", "f11", "f12"]]

    #flat version, used by optimizer
    all_keys = [x for y in all_keys_arranged for x in y]
    
    locked_pairs = [["a", "A"], ["b", "B"], ["c", "C"], ["d", "D"], ["e", "E"], ["f", "F"],
                    ["g", "G"], ["h", "H"], ["i", "I"], ["j", "J"], ["k", "K"], ["l", "L"],
                    ["m", "M"], ["n", "N"], ["o", "O"], ["p", "P"], ["q", "Q"], ["r", "R"],
                    ["s", "S"], ["t", "T"], ["u", "U"], ["v", "V"], ["w", "W"], ["x", "X"],
                    ["y", "Y"], ["z", "Z"]]

    # this is messy and fragile but constructs the list of chords i want to use
    # some cost checks will break if any non-consecutive single-hand chords are used
    chords = [[x] for x in range(0,16)]
    # all consecutive one-hand doubles
    chords += [[chords[i][0], chords[i+1][0]] for i in range(0,15) if (i != 7)]
    # all two-hand doubles that don't include pinkies
    chords.extend([[x,y] for x in range(8) for y in range(8,16) if (x not in [6,7]) and (y not in [14,15])])
    # add a few pinky chords to bring it to 70.
    chords.extend([[6,8],[6,9], [0,14], [0,15]])
    return (chords, all_keys, all_keys_arranged, locked_pairs)




#random.seed(0)

#w = Weight(num_switches=50, weak_finger=10, hand_balance=0, num_presses=20, finger_reused=10, direction_change=30, row_change=10)

# pp = pprint.PrettyPrinter()
(chords, all_keys, all_keys_arranged, locked_pairs) = get_constants()            
(freq1, freq3) = get_corpus()
# print freq3
#lay = read_layout("dvorak.kmap.bak")
#print_layout(lay, [["a", "o", "e", "u",], ["h", "t", "n", "s",]], "dvtest.kmap")
 # dv_arranged = [[a o e u], [h t n s], [\' , . p], [g c r l], [; q j k], [m w v s], [y i x], [f d b],


