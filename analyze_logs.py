#! /bin/python2


import re
import pprint
from collections import Counter
from collections import namedtuple
import random 
from warnings import warn
from copy import deepcopy
from layout_printer import print_layout
from layout_printer import read_layout


Weight = namedtuple("Weight", "num_switches, weak_finger, hand_balance, num_presses, finger_reused, direction_change, row_change")


def load_log(filename):
    f=open(filename, "r")
    log=f.read()
    f.close()
    #remove logging start/stop timestamp messages and surrounding newlogs
    log=re.sub("\n+Logging [(started)(stopped)]+ at [-0-9 :]+(> \n\n)?", "x", log)
    log =re.sub("\n", "<Ret>", log)
    log =re.sub(" ", "<Space>", log)
    #remove +num from repeat marker
    log =re.sub("<#\+[0-9]+>", "<#>", log)
    #split into individual keystrokes
    #ignore some weird characters - don't know how they got there
    log = re.findall(r"(<[A-Za-z#]+>|[^\240\x00\304\212])",log)
    return log

def print_table(freq):
    print '______________________'
    for line in freq:
        # print line
        print '\t'.join(line[0])+'\t- '+str(line[1])
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

def get_corpus(debug_corpus=[]):
    if debug_corpus:
        corpus = debug_corpus
    else:
        # log=load_log("/var/log/logkeys.log") # 
        # mycorpus=load_log("mycorpus.txt")
        books=load_log("books.short.txt")
        corpus = books
    
    #define key sets
    full=set(corpus)
    len1 = set([x for x in full if len(x)==1 or x=='<Space>'])
    alphas = set([chr(x) for x in (range(65, 65+26) + range(97, 97+26))])
    specials = set([x for x in full if len(x)>1 and x!='<Space>' and x!='<#>'])
    mods = set(['<RMeta>', '<LShft>', '<Esc>', '<RCtrl>', '<LAlt>', '<RShft>', '<LCtrl>'])
    nonmods = full - mods
    moves = set(['<PgDn>', '<PgUp>', '<Home>', '<End>', '<Right>', '<Down>', '<Up>', '<Left>'])
    nums = set([str(x) for x in range(0,10)])
    repeat = set(['<#>'])

    freq1 = count_freq(corpus, 1)
    freq3 = count_freq(corpus, 3)

    # print_table(freq1)
    # print_table(filter(freq3, [full - set(['<Space>'])]))
    # print_table(freq3)
    # exit()
    # print_table(filter(freq3, [alphas]))
    # print_table(filter(freq1, [alphas]))

    return (dict(freq1), dict(freq3))

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
        # print pressed
        cost += sum([len(x) for x in pressed]) * freq3_dict[triad] * weight.num_presses
        cost += is_finger_reused(pressed) * freq3_dict[triad] * weight.finger_reused
        
        for hand_func in [is_left, is_right]:
            one_hand_pressed = [x[0] for x in pressed if hand_func(x[0])]
            # dir = does_direction_change(one_hand_pressed)
            # row = num_row_changes(one_hand_pressed)
            (row, dir) = get_row_and_direction_changes(one_hand_pressed) #TODO MAKE SURE CORRECT ANSWER, TRY SHORT CIRCUITING
            cost += dir * freq3_dict[triad] * weight.direction_change
            cost += row * freq3_dict[triad] * weight.row_change
             # 6.395    0.063   11.705
             # 6.837    0.068    9.940 | 6.064    0.060    8.729 || 6.116    0.061    8.836 | 6.070    0.060    8.791 | 
            # assert(row1 == row2)
            # assert(dir1 == dir2)
    return cost

        
def optimize(initial_layout, freq1, freq3, weight, p, locked_pairs, iterations):
    cost = calculate_cost(initial_layout, freq1, freq3, weight)
    layout = deepcopy(initial_layout)
    print "initial:"
    print layout
    print cost
        
    for i in range(iterations):
        new_layout = swap(layout, locked_pairs, 2)
        new_cost = calculate_cost(new_layout, freq1, freq3, weight)
        #short circuiting for speed if p is 0
        if (new_cost <= cost) or (p and (random.random() < p)): 
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
            layout[tuple(chords[i])] = all_keys[2*i:2*i+2]
        else:
            print 2*i+2
            layout[tuple(chords[i])] = ['', '']
    return layout


random.seed(0)

w = Weight(num_switches=50, weak_finger=10, hand_balance=0, num_presses=20, finger_reused=10, direction_change=30, row_change=10)

# pp = pprint.PrettyPrinter()
(chords, all_keys, all_keys_arranged, locked_pairs) = get_constants()            
(freq1, freq3) = get_corpus()

initial_layout = make_random_layout(chords, all_keys)
# print_layout_4col(make_reverse_layout(initial_layout), all_keys_arranged) 
print_layout(initial_layout, all_keys_arranged, 'initial') 

foo = read_layout("initial")
print initial_layout
print foo
for key in foo.keys():
    assert(initial_layout[key] == foo[key])
    
# assert(initial_layout == foo)
# new = optimize(initial_layout, freq1, freq3, w, 0.05, locked_pairs, 10000)
# print_layout(new, all_keys_arranged, 'newkeymap2') 








# print_table( freq1)
    # print freq1
    # print dict(freq1)[('q',)]
    # print_table(filter(freq1, [alphas]))
    # print_table(filter(freq1, [mods]))
    # print_table(filter(freq1, [full]))
    # print_table(filter(freq2, [full, repeat]))
    # print_table(filter(freq3, [alphas, alphas, alphas]))
    # print_table(filter(freq2, [alphas, alphas]))
    #print_table(filter(freq4, [alphas, alphas, alphas, alphas]))
    # print_table(filter(freq4, [full, full, full, full]))
    # print_table(filter(freq4, [len1, len1, len1, len1]))


# def old_row_helper2(left_right_list):
#     # print [abs(left_right_list[i+1]%2 - left_right_list[i]%2) for i in range(len(left_right_list)-1)]
#     return sum([(left_right_list[i+1] - left_right_list[i])%2 for i in range(len(left_right_list)-1)])
    
# def row_helper(left_right_list):
#     iterable = iter(left_right_list)
#     old_x = (next(iterable))%2
#     for x in iterable:
#         modx = x%2
#         yield (modx - old_x) != 0
#         old_x = modx
#     # return sum([0!=(left_right_list[i+1]%2 - left_right_list[i]%2) for i in range(len(left_right_list)-1)])

# def row_helper2(left_right_list):
#     iterable = iter(left_right_list)
#     old_x = next(iterable)
#     for x in iterable:
#         yield (x - old_x) % 2
#         old_x = x

# def aids(left_right_list):
#     return sum(list(row_helper(left_right_list)))
        
# def spam(left_right_list):
#     return sum(list(row_helper2(left_right_list)))

#"AzAEBcBcBEdcEdcEdcEdcEdcEdcEdcEdcEEEEEEEEEE")
# locked_pairs = [["d","c"], ["E","B"]]
# locked_pairs = [["d","B"], ["c","z"],  ["E", "A"]]
# bad  = {(0,2,4):["E", ""], (12,14):["A","z"],  (2,4):["", "B"], (8,):["d", ""] } # 
# bad  = {(9,):["d","B"], (12,):["c","z"],  (10,):["E", "A"]}
# good = {(8,):["d","B"], (10,):["c","z"],  (12,):["E", "A"]}
# print calculate_cost({(8,10,12):["z","A"], (9,):["E","c"],  (9,10):["B", "d"]}, freq1, freq3, w)
# print calculate_cost({(8,10,12):["z","A"], (9,):["E","d"],  (9,10):["B", "c"]}, freq1, freq3, w)
# {(8,10,12):["z","A"], (9,):["E","d"],  (9,10):["B", "c"]}
