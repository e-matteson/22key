#! /bin/python2
import re
from math import log

# TODO this assumes the ordering of bits in an int is the same on the teensy
#      and wherever this python script is running. that's not ideal.
# 
# TODO remove support for deprecated "shifted" commands from the parser


# Format of .kmap file:
# 
# lines beginning with // are ignored
# period is not-pressed, and any alphanumeric character is pressed
# 
# cfg file bit order is (LSB -> MSB):
# [22-31 zero]
#
#     21 20 19 18         17 16 15 14
#     13 12 11 10         9  8  7  6
#           5  4  3    2  1  0
#
# scanMatrix bit order is:
# [2, 14, 24-31 zero]
#
#     12 15 18 21         0  3  6  9
#     13 16 19 22         1  4  7  10
#           17 20 23   5  8  11
#

bit_order =  range(31, 23, -1) + [3, 10, 18, 4, 11, 19, 5, 12, 20, 31, 13, 21, 0, 6, 14, 1, 7, 15, 2, 8, 16, 31, 9, 17]
bit_order = [31-b for b in bit_order]
PADWIDTH = 10; #22 keys, uint32

########## HID usage code / macro dictionaries

# if shift is pressed at the same time as the chord for any of these keys, both
# the shift and the key will be sent.
shiftable_codes   = dict( #codes for bluetooth HID, which isn't implemented yet
    KEY_A         = 4,         KEY_B=5,         KEY_C=6,       KEY_D=7,     KEY_E=8,       
    KEY_F         = 9,         KEY_G=10,        KEY_H=11,      KEY_I=12,    KEY_J=13,      
    KEY_K         = 14,        KEY_L=15,        KEY_M=16,      KEY_N=17,    KEY_O=18,      
    KEY_P         = 19,        KEY_Q=20,        KEY_R=21,      KEY_S=22,    KEY_T=23,      
    KEY_U         = 24,        KEY_V=25,        KEY_W=26,      KEY_X=27,    KEY_Y=28,      
    KEY_Z         = 29,        KEY_ENTER=40,    KEY_BACKSPACE=42, KEY_TAB=43,  KEY_SPACE=44,
    KEY_CAPS_LOCK = 57, KEY_F1=58,       KEY_F2=59,     KEY_F3=60,   KEY_F4=61,     
    KEY_F5        = 62,       KEY_F6=63,       KEY_F7=64,     KEY_F8=65,   KEY_F9=66,     
    KEY_F10       = 67,      KEY_F11=68,      KEY_F12=69,    KEY_HOME=74, KEY_PAGE_UP=75, 
    KEY_END       = 77,      KEY_PAGE_DOWN=78, KEY_RIGHT=79,  KEY_LEFT=80, KEY_DOWN=81,   
    KEY_UP        = 82, KEY_ESC=41, KEY_PRINTSCREEN=70, KEY_SCROLL_LOCK=71,
    KEY_1         = 30, KEY_2                                 =31, KEY_3             =32,
    KEY_4         = 33, KEY_5 =34, KEY_6 =35,
    KEY_7         = 36, KEY_8=37 , KEY_9 =38,
    KEY_0         = 39, KEY_DELETE=76,
    BLANK          = 0  #for blank spaces in map
)  


# if shift is pressed at the same time as the chord for any of these keys, the
# chord will not be recognized and nothing will be sent.
exact_codes         = dict(
    KEY_MINUS       =[("KEY_MINUS","")], KEY_EQUAL     =[("KEY_EQUAL","")],
    KEY_BACKSLASH   = [("KEY_BACKSLASH","")], KEY_SEMICOLON                =[("KEY_SEMICOLON","")], KEY_QUOTE =[("KEY_QUOTE","")],
    KEY_GRAVE       = [("KEY_TILDE","|MODIFIERKEY_SHIFT")], KEY_COMMA      =[("KEY_COMMA","")], KEY_PERIOD    =[("KEY_PERIOD","")],
    KEY_SLASH       = [("KEY_SLASH","")],
    KEY_BANG        = [("KEY_1", "|MODIFIERKEY_SHIFT")], KEY_ASTERISK      =[("KEY_8","|MODIFIERKEY_SHIFT")],
    KEY_UNDERSCORE  = [("KEY_MINUS", "|MODIFIERKEY_SHIFT")], KEY_PLUS      =[("KEY_EQUAL","|MODIFIERKEY_SHIFT")],
    KEY_PIPE        = [("KEY_BACKSLASH", "|MODIFIERKEY_SHIFT")], KEY_COLON =[("KEY_SEMICOLON","|MODIFIERKEY_SHIFT")],
    KEY_DOUBLEQUOTE = [("KEY_QUOTE","|MODIFIERKEY_SHIFT")], KEY_TILDE      =[("KEY_TILDE", "")],
    KEY_LEFT_ANGLE   = [("KEY_COMMA","|MODIFIERKEY_SHIFT")], KEY_RIGHT_ANGLE =[("KEY_PERIOD", "|MODIFIERKEY_SHIFT")],
    KEY_QUESTION    = [("KEY_SLASH","|MODIFIERKEY_SHIFT")], KEY_AT         =[("KEY_2","|MODIFIERKEY_SHIFT")],
    KEY_HASH        = [("KEY_3","|MODIFIERKEY_SHIFT")], KEY_DOLLAR         =[("KEY_4","|MODIFIERKEY_SHIFT")],
    KEY_PERCENT     = [("KEY_5","|MODIFIERKEY_SHIFT")], KEY_CARET          =[("KEY_6","|MODIFIERKEY_SHIFT")],
    KEY_AMPERSAND   =[("KEY_7","|MODIFIERKEY_SHIFT")],
    KEY_LEFT_PAREN     =[("KEY_9","|MODIFIERKEY_SHIFT")],
    KEY_RIGHT_PAREN     =[("KEY_0","|MODIFIERKEY_SHIFT")],
    KEY_LEFT_BRACE     =[("KEY_LEFT_BRACE","")],
    KEY_RIGHT_BRACE     =[("KEY_RIGHT_BRACE","")],
    KEY_LEFT_CURLY     =[("KEY_LEFT_BRACE","|MODIFIERKEY_SHIFT")],
    KEY_RIGHT_CURLY     =[("KEY_RIGHT_BRACE","|MODIFIERKEY_SHIFT")],
    # MACRO_ST            =[("KEY_S", ""), ("KEY_T", "")],
    MACRO_NT            =[("KEY_N", ""), ("KEY_T", "")],
    MACRO_TH            =[("KEY_T", ""), ("KEY_H", "")],
    MACRO_NG            =[("KEY_N", ""), ("KEY_G", "")],
    MACRO_SWITCH_BUFFER =[("KEY_SPACE", ""), ("KEY_O", ""), ("KEY_Z", ""), ("KEY_B", "")],
    MACRO_COMPILE   =[("KEY_SPACE", ""), ("KEY_O", ""), ("KEY_Z", ""), ("KEY_C", "")],
    MACRO_HELM_MINI =[("KEY_SPACE", ""), ("KEY_O", ""), ("KEY_Z", ""), ("KEY_H", "")],
    MACRO_HELM_IMENU =[("KEY_SPACE", ""), ("KEY_O", ""), ("KEY_Z", ""), ("KEY_I", "")],
    MACRO_RUN       =[("KEY_SPACE", ""), ("KEY_O", ""), ("KEY_Z", ""), ("KEY_R", "")],
    MACRO_BRACE     =[("KEY_LEFT_BRACE",""),("KEY_RIGHT_BRACE",""),("KEY_LEFT","")],
    MACRO_CURLY     =[("KEY_LEFT_BRACE","|MODIFIERKEY_SHIFT"), ("KEY_RIGHT_BRACE","|MODIFIERKEY_SHIFT"), ("KEY_LEFT","")],
    MACRO_PAREN     =[("KEY_9","|MODIFIERKEY_SHIFT"), ("KEY_0","|MODIFIERKEY_SHIFT"),("KEY_LEFT","")])

modifiers =  dict(KEY_CTRL="MODIFIERKEY_CTRL", KEY_ALT="MODIFIERKEY_ALT", KEY_GUI="MODIFIERKEY_GUI", KEY_SHIFT="MODIFIERKEY_SHIFT")

def gather_4_lines(f_cfg):
    lines=[]
    found_shifted_command = False
    while len(lines) < 4:
        l = f_cfg.readline()
        if l == "":
            # EoF
            break
        # skip blank lines and comments
        if(l.strip() != "" and l.strip()[0:2] != "//" ):
            if l.split()[0].strip() == "shifted":
                # reached the end of the layout images,
                # we're in the "shifted" command region now
                found_shifted_command = True
                break
            # else this is part of a keymap image
            lines.append(re.split('[ \t]+', l.strip()))
    return (lines, found_shifted_command)

def lines_to_dict_of_1hot_switch_lists(lines):
    map_subdictionary = {}
    for b in range(len(lines[0])):
        switch_list = []
        [switch_list.extend(lines[row][b*2:b*2+2]) for row in range(1,4)]
        # print '*************************'
        # print switch_list
        switch_list = [re.sub('\.', '0', c) for c in switch_list]
        switch_list = [re.sub('[^0]', '1', c) for c in switch_list]
        switch_list = list('0'*PADWIDTH + ''.join(switch_list))
        # print switch_list
        map_subdictionary[lines[0][b]] = switch_list
    return map_subdictionary

def parse_kmap(filename):
    f_cfg = open(filename, 'r')
    map = {}
    in_shifted_command_region = False
    shifted_dict = {}
    shift_switch_num=None
    while 1:
        lines = []
        if not in_shifted_command_region:
            # gather up 4 lines, parse the keymaps in each column
            # store one-hot list of activated switches in map
            (lines,in_shifted_command_region) = gather_4_lines(f_cfg)
            if not lines:
                # EoF. probably. todo: will lines be empty in any other case?
                break
            if len(lines) != 4: # 
                print "WARNING: lines ignored in keymap"
                print lines
                continue
                # raise Exception("todo handle this better")
            map.update(lines_to_dict_of_1hot_switch_lists(lines))
        else:
            # parse the "shifted" commands
            l = f_cfg.readline()
            if l == "":
                # EoF
                break
            if l.strip() != "" and l.split()[0] == "shifted":
                # not blank line, is a line with a "shifted" command
                #  dict: shifted -> unshifted
                shifted_dict[l.split()[1]] = l.split()[2]

    # shift must bound to exactly one switch
    assert map["KEY_SHIFT"].count("1") ==1
    shift_switch_num =  map["KEY_SHIFT"].index("1")
    if shifted_dict:
        # handle shifted commands
        print shift_switch_num
        # error
        print shifted_dict
        for shifted_name in shifted_dict.keys():
            unshifted_name = shifted_dict[shifted_name]
            print
            print shifted_name
            map[shifted_name] = map[unshifted_name]
            map[shifted_name][shift_switch_num] = '1'
            print map[shifted_name]

    # turn all 1hot lists into ints representing state 
    for name in map.keys():
        print name
        print map[name]
        print len(map[name])
        print len(bit_order)
        map[name] = ''.join([map[name][j] for j in bit_order]) 
        map[name] = int(map[name],2)
    return (map, shift_switch_num)


########## structure of c file
top_str1 = "#define BLANK 0 \nvoid translateAndSendState(uint32_t state){\n"
top_str2 = "  //blank out mods except shift, set mod_byte\n  char mod_byte = 0;\n"

if_str_mod1 = "  if(state & 1<<%d){\t\t//%s\n"
if_str_mod2 = "    mod_byte |= %s;\n    state &= ~ (1<<%d);\n  }\n"  
if_str_zero = "  if(state == 0){\n    sendOverUSB(0, mod_byte);\n    return;\n}"

start_exact = "\n  //exact matches that depend on shift, some are macros\n\n"
if_str_exact1 = "  if(state == %d){\t\t//%s\n"
if_str_exact2 = "    sendOverUSB(%s, mod_byte %s);\n"
if_str_exact3 = "    return;\n  }\n"

start_plain1 = "\n  //matches disregarding shift\n  //set shift_flag, clear shift bit in state\n"
start_plain2 = "  if(state & 1<<%d){\n   mod_byte |= MODIFIERKEY_SHIFT;\n  }\n"
start_plain3 = "  state &= ~ (1<<%d);\n"
if_str_plain1 ="  if(state == %d){\t\t//%s\n"
if_str_plain2 ="    sendOverUSB(%s, mod_byte);\n    return;\n  }\n"

bottom_str1 = "  //else unknown combo, or only mods are down\n  Serial.println(\"warning: unknown switch combination\");\n"
bottom_str2 = "  sendOverUSB(0, mod_byte);\n}"

def write_c(map, output_filename):
    print "begin write_c()"
    f_c = open(output_filename, 'w')
    shiftable_keys = shiftable_codes.keys()
    exact_keys = exact_codes.keys()
    modifier_keys = modifiers.keys()
    map_keys = map.keys()
    f_c.write(top_str1)
    f_c.write(top_str2)
    # check for modifiers, set modbyte (handle shift after the exact section instead)
    for name in modifier_keys:
        if name in map_keys and name != "KEY_SHIFT":
            # assumes modifiers mapped to only a single switch
            position = int(log(map[name],2)) 
            f_c.write( if_str_mod1 % (position, name))
            f_c.write( if_str_mod2 %  (modifiers[name], position))

    # check for zero state early, cuz its common
    f_c.write( if_str_zero)

    # check for exact, unshiftable matches
    f_c.write(start_exact)
    for name in exact_keys:
        if name in map_keys:
            f_c.write( if_str_exact1 % (map[name], name) )
            print exact_codes[name]
            for k in exact_codes[name]:
                f_c.write( if_str_exact2 % (k[0], k[1]) )
            f_c.write( if_str_exact3)

    # check for shiftable matches
    position = int(log(map["KEY_SHIFT"],2)) 
    f_c.write(start_plain1)
    f_c.write(start_plain2 % position)
    f_c.write(start_plain3 % position)
    for name in shiftable_keys:
        if name in map_keys:
            # f_c.write( if_str_plain1 % (map[name], name))
            f_c.write( if_str_plain1 % (map[name], name))
            f_c.write( if_str_plain2 % name)
            #todo: for bluetooth, use shiftable_codes[name] in plain2 to get usage code instead

    f_c.write(bottom_str1)
    f_c.write(bottom_str2)
    print "done writing to file"


(map, shift_switch_num) = parse_kmap("keymaps/dvorak2.kmap")
write_c(map, 'teensyfirmware/translate.ino')




# f1		f2		f3		f4		
# ....   ....	....   ....	....   ....	....   ....	
# ....   ....	....   ....	....   ....	....   ....	
#   ... ...  	  ... ...  	  ... ...  	  ... ...  	

# f5		f6		f7		f8		
# ....   ....	....   ....	....   ....	....   ....	
# ....   ....	....   ....	....   ....	....   ....	
#   ... ...  	  ... ...  	  ... ...  	  ... ...  	

# f9		f10		f11		f12		
# ....   ....	....   ....	....   ....	....   ....	
# ....   ....	....   ....	....   ....	....   ....	
#   ... ...  	  ... ...  	  ... ...  	  ... ...  	

