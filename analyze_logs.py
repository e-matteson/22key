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
import time

SHIFT_INDEX = 18
Weight = namedtuple("Weight", "num_switches, weak_finger, hand_balance, num_presses, finger_reused, direction_change, row_change")

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

def print_table(freq,factor=1000):
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

def filter_freqs(freq, filters):
    filtered_freq = []
    for f in range(len(filters)):
        freq = [ngram for ngram in freq if (False not in [x in filters[f] for x in ngram[0]])]
    return freq

def get_corpus(filename, ngram_lengths, categories=[], debug_corpus=[], use_dict=True):
    if debug_corpus:
        corpus = debug_corpus
    else:
        # log=load_log("/var/log/logkeys.log") # 
        # log=load_log("logkeys.log")  #
        # mycorpus=load_log("mycorpus.txt")
        # books=load_log("books.short.txt")
        corpus = load_log(filename)
    
    #define key sets. some depend on each other, so set those after
    full=set(corpus)
    category_dict = {
        "full" :full,
        "len1" : set([x for x in full if len(x)==1 or x=='<space>']),
        "alphas" : set([chr(x) for x in (range(65, 65+26) + range(97, 97+26))]),
        "specials" : set([x for x in full if len(x)>1 and x!='<space>' and x!='<#>']),
        "mods" : set(['<rmeta>','<lshft>','<esc>','<rctrl>','<lalt>','<rshft>','<lctrl>']),
        "moves" : set(['<pgdn>','<pgup>','<home>','<end>','<right>','<down>','<up>','<left>']),
        "nums" : set([str(x) for x in range(0,10)]),
        "repeat" : set(['<#>'])}
    # //should have removed space as well before first long optimizations...
    category_dict["nonmods"] = full - category_dict["mods"] - set(['<#>', '<enter>', '<bcksp>', '<space>'])
        
    freqs = tuple(count_freq(corpus, n) for n in ngram_lengths)

    # optionally filter
    if categories:
        freqs = tuple(filter_freqs(f, [category_dict[c] for c in categories]) for f in freqs)
    if use_dict:
        freqs = tuple(dict(f) for f in freqs)
    return freqs

def print_layout(layout, all_keys_arranged, filename, notes=''):
    print all_keys_arranged
    f_cfg = open(filename, 'w')
    template=['%s\t\t', '%s%s%s%s   %s%s%s%s\t', '%s%s%s%s   %s%s%s%s\t', '  %s%s%s %s%s%s  \t']
    unknown_entry=["UNKNOWN", ('-',)*8, ('-',)*8, ('-',)*6]
    names_to_entries = {}
    for chord in layout.keys():
        for shifted in [0,1]:
            name = layout[chord][shifted]
            if name:
                binary = indices2binary(chord, shifted)
                names_to_entries[name] = [(name,), tuple(binary[0:8]), tuple(binary[8:16]), tuple(binary[16:22])]
                
    str = ""
    if notes:
        str += "// " + re.sub("\n", "\n// ", notes) + "\n"
    for row in all_keys_arranged:
        # n=len(row)
        for i in range(4):
            for name in row:
                try:
                    str+= template[i] % names_to_entries[name][i]
                except KeyError:
                    # print ((name,)+("-",)*22)
                    str+= template[i] % unknown_entry[i]
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

def is_top(switch):
    """ return true if switch is in a top row """
    return bool(switch % 2)

def is_bottom(switch):
    """ return true if switch is in a bottom row """
    return not is_top(switch)

def is_left(switch):
    """ return true if switch is under left hand """
    return switch <= 7

def is_right(switch):
    """ return true if switch is under right hand """
    return 8 <= switch <= 15

def does_direction_change(left_right_list): #todo test
    """ left_right_list is list of first switch in each chord of an n-gram, filtered for one hand/row only"""
    # this version considers both rows - so it accepts some 'same finger, diff row' transitions as monotonic
    # directions = [0 < (left_right_list[i+1]-left_right_list[i]) for i in range(len(left_right_list)-1)]
    # lobster = old_direction_helper(left_right_list)
    # directions = list(direction_helper(left_right_list))
    # return directions.count(True) and directions.count(False)
    # dirr=new_direction_helper(left_right_list)
    dirrrr = derp(left_right_list)
    # assert(dirr == dirrrr)
    return dirrrr
    # return (True in directions) and (False in directions)
    
def derp(l):
    directions = list(direction_helper(l))
    return (True in directions) and (False in directions)

def old_direction_helper(l):
    return [0 < (l[i+1]-l[i]) for i in range(len(l)-1)]

def direction_helper(l):
    iterable = iter(l)
    old_x = next(iterable)
    for x in iterable:
        yield (x - old_x) > 0
        old_x = x
        
def old_row_helper(left_right_list):
    # print [abs(left_right_list[i+1]%2 - left_right_list[i]%2) for i in range(len(left_right_list)-1)]
    return sum([abs(left_right_list[i+1]%2 - left_right_list[i]%2) for i in range(len(left_right_list)-1)])

def get_row_and_direction_changes(l):
    any_true = False
    any_false = False
    row_changes = 0
    for i in range(len(l)-1):
        row_changes += (l[i+1] - l[i])%2
        any_true = any_true  or (0 < (l[i+1]-l[i]))
        any_false = any_false or (0 > (l[i+1]-l[i]))
    return (row_changes, any_true and any_false)

# def old_row_helper3(left_right_list):
#     # print [abs(left_right_list[i+1]%2 - left_right_list[i]%2) for i in range(len(left_right_list)-1)]
#     for i in range(len(left_right_list)-1):
#     return row_changes
    
def num_row_changes(left_right_list):
    """ left_right_list is list of first switch in each chord of an n-gram, filtered for one hand/row only."""
    return old_row_helper(left_right_list)

def is_finger_reused(pressed):
    """ Checks for 'same finger / diff row' transition, only between first two elements of pressed.
    So, only between first two chords of n-gram."""
    if len(pressed) < 2:
        return False
    for x in pressed[0]:
        for y in pressed[1]:
            if (x-y==-1 and x%2==0) or (x-y==1 and x%2==1):
                return True
    return False

    #     7  5  3  1          9  11 13 15
    #     6  4  2  0          8  10 12 14           
    #           18 17 16   19 20 21

def is_weak(switch):
    return switch in range(4,8)+range(12,16)

def swap(layout_bar, locked_pairs, num_to_swap):
    layout_foo = deepcopy(layout_bar)
    chords = layout_foo.keys()
    for n in range(num_to_swap):
        i = random.randrange(len(chords))
        j = random.randrange(len(chords))
        if (layout_foo[chords[i]] in locked_pairs) or (layout_foo[chords[j]] in locked_pairs):
            #todo copy bug?
            tmp = layout_foo[chords[i]]
            layout_foo[chords[i]] = layout_foo[chords[j]]
            layout_foo[chords[j]] = tmp
        else:
            i_shifted = random.randrange(2)
            j_shifted = random.randrange(2)
            tmp = layout_foo[chords[i]][i_shifted]
            layout_foo[chords[i]][i_shifted] = layout_foo[chords[j]][j_shifted]
            layout_foo[chords[j]][j_shifted] = tmp
    return layout_foo
            
def calculate_cost(layout, freq1_dict, freq3_dict, weight):
    cost = 0
    num_right = 0
    num_left = 0
    chords = layout.keys()
    
    # single char metrics
    for chord in chords:
        # check number of switches
        total_freq=0
        for shifted in [0,1]:
            try:
                cost += (len(chord)+shifted) * freq1_dict[(layout[chord][shifted],)] * weight.num_switches
                total_freq += freq1_dict[(layout[chord][shifted],)]
            except KeyError:
                pass
                # warn("Character not found in corpus: %s" % layout[chord][shifted])
                # total_freq += 0
        for switch in chord:
            # check hand balance of individual characters
            if is_right(switch):
                num_right += total_freq
            else:
                num_left += total_freq
            if is_weak(switch):
                cost +=  total_freq * weight.weak_finger
        
    cost += abs(num_right - 0.5) * weight.hand_balance
    # multiple char metrics
    chord_lookup = make_reverse_layout(layout)
    for triad in freq3_dict.keys():
        try:
            chord_seq = [chord_lookup[char] for char in triad]
        except KeyError:
            # skip this triad if it contains an unknown character
            # warn("character from corpus not found in layout: %s" % char)
            continue
        # get number of changed switches between consecutive pairs of chords
        # this penalizes long chords, so maybe the separate length check is unnecessary?
        # todo: think about how this interacts with repeated presses (eg. alt u u u u u)
        # num_changed_list = [len(set(chord_seq[i+1]) ^ set(chord_seq[i])) for i in range(len(chord_seq)-1)]
        #for now, weight both transitions in the triad equally
        # cost += sum(num_changed_list) * freq3_dict[triad] * weight.num_switch_changes
        #replace with num presses - this old version counted releases too
        
        # list of keys newly pressed for each chord
        pressed = [list(chord_seq[0])] + [list(set(chord_seq[i+1]) - set(chord_seq[i])) for i in range(len(chord_seq)-1)]
        # remove empty sub-lists (transitions with only releases)
        pressed = [x for x in pressed if x]
        cost += sum([len(x) for x in pressed]) * freq3_dict[triad] * weight.num_presses
        cost += is_finger_reused(pressed) * freq3_dict[triad] * weight.finger_reused
        if weight.direction_change or weight.row_change:
            # skip this unless weights are non-zero
            for hand_func in [is_left, is_right]:
                one_hand_pressed = [x[0] for x in pressed if hand_func(x[0])]
                (row, dir) = get_row_and_direction_changes(one_hand_pressed) 
                cost += dir * freq3_dict[triad] * weight.direction_change
                cost += row * freq3_dict[triad] * weight.row_change
    return cost

    
def optimize(initial_layout, freq1, freq3, weight, heats, locked_pairs, iterations):
    cost = calculate_cost(initial_layout, freq1, freq3, weight)
    layout = deepcopy(initial_layout)
    print "initial:"
    print layout
    print cost

    for iter in range(iterations):
        print iter
        new_layout = swap(layout, locked_pairs, 2)
        new_cost = calculate_cost(new_layout, freq1, freq3, weight)
        
        if iter == heats[0][0]:
            heats.pop(0)
            
        #short circuiting for speed if p is 0
        if (new_cost <= cost) or (heats[0][1] and (random.random() < heats[0][1])): 
            # print "accepted!"
            layout = deepcopy(new_layout)
            cost = new_cost
    print "done"
    print cost
    return layout

def make_random_layout(chords, keys):
    #keep upper/lower letters together
    layout={}
    random.shuffle(chords)
    
    # make length even number
    if len(keys)%2:  
        keys.append('')
    print len(keys)
    # put consecutive pairs of characters with same chord (a,A,b,B...)
    for i in range(len(chords)):
        if 2*i+2 <= len(keys):
            layout[tuple(chords[i])] = keys[2*i:2*i+2]
        else:
            print 2*i+2
            layout[tuple(chords[i])] = ['', '']
    return layout

def print_ngram_image(layout_file, freq):
    ngrams = [list(x[0]) for x in freq[0:100]]
    layout = read_layout(layout_file)
    print_layout(layout, ngrams, "ngram_"+layout_file)
    # dv_arranged = [[a o e u], [h t n s], [\' , . p], [g c r l], [; q j k], [m w v s], [y i x], [f d b],


#random.seed(0)


# pp = pprint.PrettyPrinter()

# use heat/probability heat[i][1] until iteration heat[i][0]

def run_optimizer(corpus_file, out_file, num_iters, heats, weights):
    commit = "aa512"
    (chords, all_keys, all_keys_arranged, locked_pairs) = get_constants()            
    (freq1, freq3) = get_corpus(corpus_file, [1,3], ["nonmods"])
    initial_layout = make_random_layout(chords, all_keys)
    print_layout(initial_layout, all_keys_arranged, 'init_'+out_file)
    start = time.time()
    new_layout = optimize(initial_layout, freq1, freq3, weights, heats, locked_pairs, num_iters)
    print "time: %0.4f hours" % ((time.time() - start) / 60. / 60.,)
    notes = corpus_file + '\n' + str(weights)+'\n' + str(num_iters) + ' iters\n' + str(heats) + '\ncommit: ' + commit
    print_layout(new_layout, all_keys_arranged, out_file, notes) 



# w1 = Weight(num_switches=5, weak_finger=10, hand_balance=5,
#            num_presses=50, finger_reused=20, direction_change=20, row_change=20)
def single_optimizer_run():
    # UNCHANGED SINCE LAST RUN 
    w1 = Weight(num_switches=5, weak_finger=5, hand_balance=5,
                num_presses=50, finger_reused=5, direction_change=5, row_change=5)

    tenths = [x * 10**5 for x in range(1,11)]
    logprobs = [0.8, 0.4, 0.2, 0.1, 0.05, 0.025, 0.0125, 0.00625, .003125, 0]

    heats1 =  zip(tenths, logprobs)
    run_optimizer("mycorpus.txt", "mapTEST.kmp", 100, heats1, w1)
    # run_optimizer("logkeys.log", "map6.kmp", 10**6, heats1, w1)
    
(freq1,freq2, freq3) = get_corpus("mycorpus.txt", [1,2,3], ["nonmods"], use_dict=False)
print_ngram_image("map3.kmp", freq2)

# print freq3

    # freq2 = count_freq(corpus, 2)
    # freq3 = count_freq(corpus, 3)
  
#   print_table(freq1, factor=1000)  
    # print_table(freq2, factor=1000)  
    # print_table(filter_freqs(freq3, [full - set(['<Space>'])]), factor=1000)
    # exit()
#    print_table(filter_freqs(freq3, [full-mods-moves]))
    # print_table(filter_freqs(freq1, [alphas]))
    
    # print_table(filter_freqs(freq2, [alphas]))
    # print_table(filter_freqs(freq2, [alphas]))
   # return (dict(freq1), dict(freq3))
    # print 
    # print freq2
