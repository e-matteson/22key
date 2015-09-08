#! /bin/python2


import re
import pprint
from collections import Counter
from collections import namedtuple
import random 
from warnings import warn
from copy import deepcopy

def get_log(filename):
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
    return [(x[0], float(x[1])/sum(c.values())) for x in c.most_common()]

def filter(freq, set_list):
    for i in range(len(set_list)):
        freq = [x for x in freq if (x[0][i] in set_list[i])]
    return freq

def get_corpus(debug_corpus=[]):
    pp = pprint.PrettyPrinter()

    if debug_corpus:
        corpus = debug_corpus
    else:
        log=load_log("/var/log/logkeys.log") # 
        # mycorpus=load_log("mycorpus.txt")
        # books=load_log("books.short.txt")
        corpus = log
    
    #define key sets
    full=set(corpus)
    len1 = set([x for x in full if len(x)==1 or x=='<Space>'])
    alphas = set([chr(x) for x in (range(65, 65+26) + range(97, 97+26))])
    specials = set([x for x in full if len(x)>1 and x!='<Space>' and x!='<#>'])
    mods = set(['<RMeta>', '<LShft>', '<Esc>', '<RCtrl>', '<LAlt>', '<RShft>', '<LCtrl>'])
    moves = set(['<PgDn>', '<PgUp>', '<Home>', '<End>', '<Right>', '<Down>', '<Up>', '<Left>'])
    nums = set([str(x) for x in range(0,10)])
    repeat = set(['<#>'])

    freq1 = count_freq(corpus, 1)
    freq3 = count_freq(corpus, 3)

    print_table(filter(freq1, [alphas]))
    print_table(filter(freq3, [alphas]))
    return (dict(freq1), dict(freq3))

def make_reverse_layout(layout):
    reverse = {}
    for chord in layout.keys():
        for character in layout[chord]:
            reverse[character] = chord
            reverse[character] = chord
    return reverse

def get_constants():
    all_keys = ["a", "A", "b", "B", "c", "C", "d", "D", "e", "E", "f", "F", "g", "G", "h", "H", "i", "I", "j", "J", "k", "K", "l", "L", "m", "M", "n", "N", "o", "O", "p", "P", "q", "Q", "r", "R", "s", "S", "t", "T", "u", "U", "v", "V", "w", "W", "x", "X", "y", "Y", "z", "Z", "<del>", "<tab>",  "<cpslk>", "f1", "f2", "f3", "f4", "f5", "f6", "f7", "f8", "f9", "f10", "f11", "f12", "<home>", "<pgup>", "<end>", "<pgdn>", "<right>", "<left>", "<down>", "<up>", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "!", "@", "#", "$", "%", "^", "&", "*", "-", "_", "=", "+", "\\",  "|", ";",  ":",  "\'", '\"',  r"`", "~", ",", "<", ".", ">", r"/", "?", "[", "{", "(" ]

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
    # all two-hand doubles
    chords.extend([[x,y] for x in range(8) for y in range(8,16)])

    
    return (chords, all_keys, locked_pairs)


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
    directions = [0 < (left_right_list[i+1]-left_right_list[i]) for i in range(len(left_right_list)-1)]
    return directions.count(True) and directions.count(False)

def num_row_changes(left_right_list):
    """ left_right_list is list of first switch in each chord of an n-gram, filtered for one hand/row only."""
    return sum([abs(left_right_list[i+1]%2 - left_right_list[i]%2) for i in range(len(left_right_list)-1)])

def is_finger_reused(pressed):
    """ Checks for 'same finger / diff row' transition, only between first two elements of pressed.
    So, only between first two chords of n-gram."""
    if len(pressed) < 2:
        return False
    foo= [sorted([x,y]) for x in pressed[0] for y in pressed[1]]
    return bool([1 for x in foo if (x[0]%2 == 0) and (x[1] == x[0]+1)])

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
            
def calculate_cost(layout_baz, freq1_dict, freq3_dict, weight):
    cost = 0
    num_right = 0
    num_left = 0
    chords = layout_baz.keys()
    
    # single char metrics
    for chord in chords:
        # check number of switches
        for shifted in [0,1]:
            try:
                cost += (len(chord)+shifted) * freq1_dict[(layout_baz[chord][shifted],)] * weight.num_switches
            except KeyError:
                warn("Character not found in corpus: %s" % layout_baz[chord][shifted])
                
        total_freq = freq1_dict[(layout_baz[chord][0],)] + freq1_dict[(layout_baz[chord][1],)]
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
    chord_lookup = make_reverse_layout(layout_baz)
    for triad in freq3_dict.keys():
        chord_seq = [chord_lookup[char] for char in triad]
        # get number of changed switches between consecutive pairs of chords
        # this penalizes long chords, so maybe the separate length check is unnecessary?
        # todo: think about how this interacts with repeated presses (eg. alt u u u u u)
        num_changed_list = [len(set(chord_seq[i+1]) ^ set(chord_seq[i])) for i in range(len(chord_seq)-1)]
        #for now, weight both transitions in the triad equally
        cost += sum(num_changed_list) * freq3_dict[triad] * weight.num_switch_changes

        # list of keys newly pressed for each chord
        pressed = [chord_seq[0]] + [list(set(chord_seq[i+1]) - set(chord_seq[i])) for i in range(len(chord_seq)-1)]
        # remove empty sub-lists (transitions with only releases)
        pressed = [x for x in pressed if x]
        cost += is_finger_reused(pressed) * freq3_dict[triad] * weight.finger_reused
        
        for hand_func in [is_left, is_right]:
            one_hand_pressed = [x[0] for x in pressed if hand_func(x[0])]
            cost += does_direction_change(one_hand_pressed) * freq3_dict[triad] * weight.direction_change
            cost += num_row_changes(one_hand_pressed) * freq3_dict[triad] * weight.row_change
    return cost

        
def optimize(initial_layout, freq1, freq3, weight, p, locked_pairs, iterations):
    cost = calculate_cost(initial_layout, freq1, freq3, weight)
    layout = deepcopy(initial_layout)
    print "initial:"
    print layout
    print cost
        
    for i in range(iterations):
        # print 
        # print "iter %d:" % (i,)
        new_layout = swap(layout, locked_pairs, 2)
        new_cost = calculate_cost(new_layout, freq1, freq3, weight)
        # print new_layout
        # print new_cost

        if (new_cost <= cost) or (random.random() < p):
            # print "accepted!"
            layout = deepcopy(new_layout)
            cost = new_cost
    print "done"
    print cost
    return layout

# new map for easier row/hand checking
#     7  5  3  1          9  11 13 15
#     6  4  2  0          8  10 12 14           
#           18 17 16   19 20 21

(chords, all_keys, locked_pairs) = get_constants()            
Weight = namedtuple("Weight", "num_switches, weak_finger, hand_balance, num_switch_changes, finger_reused, direction_change, row_change")

w = Weight(num_switches=0, weak_finger=0, hand_balance=0, num_switch_changes=0, finger_reused=0, direction_change=0, row_change=10)

#     7  5  3  1          9  11 13 15
#     6  4  2  0          8  10 12 14           
#           18 17 16   19 20 21
(freq1, freq3) = get_corpus("AzAEBcBcBEdcEdcEdcEdcEdcEdcEdcEdcEEEEEEEEEE")
# locked_pairs = [["d","c"], ["E","B"]]
locked_pairs = [["d","B"], ["c","z"],  ["E", "A"]]
# bad  = {(0,):["d","E"], (12,):["A","z"],  (2,):["B", "c"]} # 
bad  = {(9,):["d","B"], (12,):["c","z"],  (10,):["E", "A"]}
good = {(8,):["d","B"], (10,):["c","z"],  (12,):["E", "A"]}

# print calculate_cost({(8,10,12):["z","A"], (9,):["E","c"],  (9,10):["B", "d"]}, freq1, freq3, w)
# print calculate_cost({(8,10,12):["z","A"], (9,):["E","d"],  (9,10):["B", "c"]}, freq1, freq3, w)
# {(8,10,12):["z","A"], (9,):["E","d"],  (9,10):["B", "c"]}
# print optimize(bad, freq1, freq3, w, 0, locked_pairs, 50)

print calculate_cost(bad, freq1, freq3, w)
print calculate_cost(good, freq1, freq3, w)


# print_table(freq1)
# print "\n".join(exact_codes)
# print "\n".join(codes)
        

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
