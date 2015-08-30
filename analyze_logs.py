#! /bin/python2


import re
import pprint
from collections import Counter

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

def main():
    pp = pprint.PrettyPrinter()

    log=get_log("/var/log/logkeys.log")
    corpus=get_log("corpus.txt")
    log = corpus
    
    # log = ['a','b','c','d','a','a','b']

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

    # print_table(filter(freq1, [alphas]))
    # print_table(filter(freq1, [mods]))
    # print_table(filter(freq1, [full]))


    # print_table(filter(freq2, [full, repeat]))

      
    print_table(filter(freq4, [alphas, alphas, alphas, alphas]))
    # print_table(filter(freq4, [full, full, full, full]))
    # print_table(filter(freq4, [len1, len1, len1, len1]))
 
main()


