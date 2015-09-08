#! /bin/python2


import re
import pprint
from collections import Counter
from collections import namedtuple
import random 
from warnings import warn


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
    return Counter(l).most_common()

def filter(freq, set_list):
    for i in range(len(set_list)):
        freq = [x for x in freq if (x[0][i] in set_list[i])]
    return freq

def make_reverse_layout(layout):
    reverse = {}
    for chord in layout.keys():
        for character in layout[chord]:
            reverse[character] = chord
            reverse[character] = chord
    return reverse

def calculate_cost(layout, freq1_dict, freq3_dict, weight):
    cost = 0
    num_right = 0
    chords = layout.keys()
    
    # single char metrics
    for chord in chords:
        # check number of switches
        for shifted in [0,1]:
            try:
                cost += (len(chord)+shifted) * freq1_dict[(layout[chord][shifted],)] *1
            except KeyError:
                warn("Character not found in corpus: %s" % layout[chord][shifted])
        
        for switch in chord:
            # check hand balance of individual characters
            if is_right(switch):
                num_right += 1.0/len(chords)
            if is_weak(switch):
                cost += freq1_dict[(layout[chord][0],)] * 1
                
    cost += abs(num_right - 0.5) *1

    # multiple char metrics
    chord_lookup = make_reverse_layout(layout)
    for triad in freq3_dict.keys():
        chord_seq = [chord_lookup[char] for char in triad]
        # get number of changed switches between consecutive pairs of chords
        # this penalizes long chords, so maybe the separate length check is unnecessary?
        # todo: think about how this interacts with repeated presses (eg. alt u u u u u)
        num_changed_list = [len(set(chord_seq[i+1]) ^ set(chord_seq[i])) for i in range(len(chord_seq)-1)]
        #for now, weight both transitions in the triad equally
        cost += sum(num_changed_list) * freq3_dict[triad] *1

        # list of keys newly pressed for each chord
        pressed = [chord_seq[0]] + [list(set(chord_seq[i+1]) - set(chord_seq[i])) for i in range(len(chord_seq)-1)]
        # remove empty sub-lists (transitions with only releases)
        pressed = [x for x in pressed if x]
        cost += does_finger_repeat(pressed) * freq3_dict[triad] *1
        
        for hand_func in [is_left, is_right]:
            one_hand_pressed = [x[0] for x in pressed if hand_func(x[0])]
            cost += is_direction_monotonic(one_hand_pressed) * freq3_dict[triad] *1
            cost += num_row_changes(one_hand_pressed) * freq3_dict[triad] *1
            
    return cost


def swap(layout, locked_pairs, num_to_swap):
    chords = layout.keys()
    for n in range(num_to_swap):
        i = random.randrange(len(chords))
        j = random.randrange(len(chords))
        if (layout[chords[i]] in locked_pairs) or (layout[chords[j]] in locked_pairs):
            #todo copy bug?
            tmp = layout[chords[i]]
            layout[chords[i]] = layout[chords[j]]
            layout[chords[j]] = tmp
        else:
            i_shifted = random.randrange(2)
            j_shifted = random.randrange(2)
            tmp = layout[chords[i]][i_shifted]
            layout[chords[i]][i_shifted] = layout[chords[j]][j_shifted]
            layout[chords[j]][j_shifted] = tmp
    return layout
            

        
def optimize(initial_layout, freq1, freq3, weight, p, locked_pairs):
    iterations = 200
    freq1_dict = dict(freq1)
    freq3_dict = 0
    cost = calculate_cost(initial_layout, freq1_dict, freq3_dict, weight)
    layout = initial_layout
    print "initial:"
    print layout
    print cost
        
    for i in range(iterations):
        print 
        print "iter %d:" % (i,)
        new_layout = swap(layout.copy(), locked_pairs, 2)
        new_cost = calculate_cost(new_layout, freq1_dict, freq3_dict, weight)
        print new_layout
        print new_cost

        if (new_cost <= cost) or (random.random() < p):
            print "accepted!"
            layout = new_layout.copy()
            cost = new_cost
            
    print "done"
    # print layout
    print cost
    return layout

def main():
    pp = pprint.PrettyPrinter()

    # log=get_log("/var/log/logkeys.log")
    # mycorpus=get_log("mycorpus.txt")
    # books=get_log("books.short.txt")
    # log = corpus
    # log = books
    # log = ['a','b','c','d','a','a','b']
    log = "FEZ~Z~Z~Z<E<E<E<E<E"

    #define key sets
    full=set(log)
    len1 = set([x for x in full if len(x)==1 or x=='<Space>'])
    alphas = set([chr(x) for x in (range(65, 65+26) + range(97, 97+26))])
    specials = set([x for x in full if len(x)>1 and x!='<Space>' and x!='<#>'])
    mods = set(['<RMeta>', '<LShft>', '<Esc>', '<RCtrl>', '<LAlt>', '<RShft>', '<LCtrl>'])
    moves = set(['<PgDn>', '<PgUp>', '<Home>', '<End>', '<Right>', '<Down>', '<Up>', '<Left>'])
    nums = set([str(x) for x in range(0,10)])
    repeat = set(['<#>'])

    freq1 = count_freq(log, 1)
    freq2 = count_freq(log, 2)
    freq3 = count_freq(log, 3)
    freq4 = count_freq(log, 4)
    return (freq1, freq3)
 


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

# def is_direction_monotonic(l): #todo test
#     """ l is list of first switch in each chord of an n-gram, filtered for one hand/row only"""
#     out = True
#     for func_row in [is_top, is_bottom]:
#         row = [x for x in l if func_row(x)] 
#         directions = [0 < (row[i+1]-row[i]) for i in range(len(row)-1)]
#         out = out and (directions.count(True)==0 or directions.count(False)==0)
#     return out

def is_direction_monotonic(left_right_list): #todo test
    """ left_right_list is list of first switch in each chord of an n-gram, filtered for one hand/row only"""
    # this version considers both rows - so it accepts some 'same finger, diff row' transitions as monotonic
    directions = [0 < (left_right_list[i+1]-left_right_list[i]) for i in range(len(left_right_list)-1)]
    return directions.count(True)==0 or directions.count(False)==0

def num_row_changes(left_right_list):
    """ left_right_list is list of first switch in each chord of an n-gram, filtered for one hand/row only."""
    return sum([abs(left_right_list[i+1]%2 - left_right_list[i]%2) for i in range(len(left_right_list)-1)])

def does_finger_repeat(pressed):
    """ Checks for 'same finger / diff row' transition, only between first two elements of pressed.
    So, only between first two chords of n-gram."""
    foo= [sorted([x,y]) for x in pressed[0] for y in pressed[1]]
    return bool([1 for x in foo if (x[0]%2 == 0) and (x[1] == x[0]+1)])

def is_weak(switch):
    return switch in range(4,8)+range(12,16)

# chord_seq=[[13], [6, 7], [7, 8], [7, 12, 13], [10, 12]]
# chord_seq=[[0], [8, 10], [8, 11], [8, 2, 4], [8, 6, 0]]
# chord_seq=[[15,7], [7], [2,4],[11, 13],[12]]

# new map for easier row/hand checking
#     7  5  3  1          9  11 13 15
#     6  4  2  0          8  10 12 14           
#           18 17 16   19 20 21

# for each newly pressed key, elif:
# * no key released                              -> 0  
# * no key released by same hand                 -> 1  
# * key released by same hand, diff row          -> 2  (todo: penalize more if modifier is held?)
# * key released by same hand, neighbor switch   -> 1  (todo: maybe runs worse than diff hand?)
# * key released by same hand, same row          -> 3


# conditions for consecutive same-hand presses in an n-gram:
# * row: no change                               -> 0
# * row: monotonic change                        -> 0 
# * row: non-monotonic change                    -> 2
# AND
# * dir: monotonic             -> 0
# * dir: non-monotonic         -> 3
# * dir: non-monotonic         -> 3


all_keys = ["a", "A", "b", "B", "c", "C", "d", "D", "e", "E", "f", "F", "g", "G", "h", "H", "i", "I", "j", "J", "k", "K", "l", "L", "m", "M", "n", "N", "o", "O", "p", "P", "q", "Q", "r", "R", "s", "S", "t", "T", "u", "U", "v", "V", "w", "W", "x", "X", "y", "Y", "z", "Z", "<del>", "<tab>",  "<cpslk>", "f1", "f2", "f3", "f4", "f5", "f6", "f7", "f8", "f9", "f10", "f11", "f12", "<home>", "<pgup>", "<end>", "<pgdn>", "<right>", "<left>", "<down>", "<up>", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "!", "@", "#", "$", "%", "^", "&", "*", "-", "_", "=", "+", "\\",  "|", ";",  ":",  "\'", '\"',  r"`", "~", ",", "<", ".", ">", r"/", "?", "[", "{", "(" ]

locked_pairs = [["a", "A"], ["b", "B"], ["c", "C"], ["d", "D"], ["e", "E"], ["f", "F"],
                ["g", "G"], ["h", "H"], ["i", "I"], ["j", "J"], ["k", "K"], ["l", "L"],
                ["m", "M"], ["n", "N"], ["o", "O"], ["p", "P"], ["q", "Q"], ["r", "R"],
                ["s", "S"], ["t", "T"], ["u", "U"], ["v", "V"], ["w", "W"], ["x", "X"],
                ["y", "Y"], ["z", "Z"]]

#     7  5  3  1          9  11 13 15
#     6  4  2  0          8  10 12 14           
#           18 17 16   19 20 21

# order matters! doesn't include shifted chords, or any thumb switches
# all singles
chords = range(0,16)
# all consecutive one-hand doubles
chords += [[chords[i], chords[i+1]] for i in range(0,16) if (i != 7)]
print chords
exit()
chords += [[chords[i], chords[i+1]] for i in range(8,16)]
# all two-hand doubles
for x in range(10,14)+range(18,22):
    for y in range(6,10)+range(14,18):
        chords.append([x, y])

chords = [sorted(x) for x in chords]        
print chords
# some triples?
# print chords
# print "%d of %d" % (len(chords)*2, len(all_keys)+26)

#normalize first!
# Weight = namedTuple("Weight", "num_keys, num_changes, strong_finger, weak_finger, balance_change, balance_all, run_same_row, run_diff_row" )
(freq1, freq3) = main()
initial_layout = {(10,11,12):["~","F"], (9,):["<","Z"],  (9,10):["e", "E"]}
calculate_cost(initial_layout, dict(freq1), dict(freq3), 0)

# print make_reverse_layout(initial_layout)
# print optimize(initial_layout, freq1, 0, 0, 0, locked_pairs)


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
