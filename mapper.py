#! /bin/python2

import re

# Format of .kmap file:
# 
# lines beginning with # are ignored
# period is not-pressed, and any alphanumeric character is pressed

# TODO deal with mod recognition

# TODO figure out mapping between cfg file bit order and
# scanMatrix bit order, and conversion to-from int on both
# attiny and x86. Should both be little-endian at least ...
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
#
bit_order =  range(31, 23, -1) + [3, 10, 18, 4, 11, 19, 5, 12, 20, 31, 13, 21, 0, 6, 14, 1, 7, 15, 2, 8, 16, 31, 9, 17]
# bit_order =  [17, 9, 31, 16, 8, 2, 15, 7, 1, 14, 6, 0, 21, 13, 31, 20, 12, 5, 19, 11, 4, 18, 10, 3]
#[31, 30, 29, 28, 27, 26, 25, 24, 17, 9,  ** 31, 16, 8,  2,  15, 7,  1,  14, 6,  0,  21, 13, 31, 20, 12, 5,  19, 11, 4,  18, 10, 3]

#[0,  1,  2,  3,  4,  5,  6,  7,  8,  9,  ** 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31
#[31, 30, 29, 28, 27, 26, 25, 24, 23, 22, ** 21, 20, 19, 18, 17, 16, 15, 14, 13, 12, 11, 10, 9,  8,  7,  6,  5,  4,  3,  2,  1,  0]
#----------------------------------------------------------------------------------------------------------------------------------
#[0,  1,  2,  3,  4,  5,  6,  7,  8,  9,  ** 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 14

# print range(32) 
# print bit_order[::-1]
bit_order = [31-b for b in bit_order]
print len(bit_order)
print bit_order
x = [0]*32
x[31-2] = 1
# print ''.join([x[i] for i in bit_order])
print [x[i] for i in bit_order]
# bit_order = range(32);

PADWIDTH = 10; #22 keys, uint32




########## HID usage code / macro dictionaries

shiftable_codes = dict(key_a=4, key_b=5, key_c=6, key_d=7, key_e=8, key_f=9, key_g=10, key_h=11, key_i=12, key_j=13, key_k=14, key_l=15, key_m=16, key_n=17, key_o=18, key_p=19, key_q=20, key_r=21, key_s=22, key_t=23, key_u=24, key_v=25, key_w=26, key_x=27, key_y=28, key_z=29, key_enter=40, key_delete=42, key_tab=43, key_space=44, key_capslock=57, key_f1=58, key_f2=59, key_f3=60, key_f4=61, key_f5=62, key_f6=63, key_f7=64, key_f8=65, key_f9=66, key_f10=67, key_f11=68, key_f12=69, key_home=74, key_pageup=75, key_end=77, key_pagedown=78, key_right=79, key_left=80, key_down=81, key_up=82)

shift = 1
exact_codes = dict(key_1=[(30,0)], key_2=[(31,0)], key_3=[(32,0)], key_4=[(33,0)], key_5=[(34,0)], key_6=[(35,0)], key_7=[(36,0)], key_8=[(37,0)], key_9=[(38,0)], key_0=[(39,0)], key_bang=[(30,1)], key_at=[(31,shift)], key_hash=[(32,shift)], key_dollar=[(33,shift)], key_percent=[(34,shift)], key_caret=[(35,shift)], key_ampersand=[(36,shift)], key_asterisk=[(37,shift)], key_minus=[(45,0)], key_underscore=[(45,shift)],  key_equals=[(46,0)], key_plus=[(46,shift)], key_backslash=[(49,0)], key_pipe=[(49,shift)], key_semicolon=[(51,0)],  key_colon=[(51,shift)], key_quote=[(52,0)], key_doublequote=[(52,shift)], key_grave=[(53,0)], key_tilde=[(53,shift)], key_comma=[(54,0)], key_leftangle=[(54,shift)], key_period=[(55,0)],  key_rightangle=[(55,shift)], key_slash=[(56,0)], key_question=[(56,shift)], macro_bracket=[(47,0),(48,0),(80,0)], macro_curly=[(47,shift),(48,shift),(80,0)], macro_paren=[(38,shift),(39,shift),(80,0)])

modifiers =  dict(key_ctrl="MODIFIERKEY_CTRL", key_alt="MODIFIERKEY_ALT", key_gui="MODIFIERKEY_GUI", key_shift="MODIFIERKEY_SHIFT")

def gather_4_lines(f_cfg):
    lines=[]
    found_shifted_command = False
    while len(lines) < 4:
        l = f_cfg.readline()
        if l == "":
            # EoF
            break
        if(l[0].strip() != "#"  and l.strip() != ""):
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
    assert map["mod_shift"].count("1") ==1
    shift_switch_num =  map["mod_shift"].index("1")
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
        print ''.join(map[name])
        map[name] = ''.join([map[name][j] for j in bit_order]) 
        print map[name]
        map[name] = int(map[name],2)
    print map
    return (map, shift_switch_num)

########## structure of .c file
top_str1 = "#define SHIFT_SWITCH_NUM %d \n#define CTRL_SWITCH_NUM %d \n#define ALT_SWITCH_NUM %d \n#define GUI_SWITCH_NUM %d \n"
top_str2 = "void translate(uint32_t _state){\n\n "
top_str3 = "   //blank out mods except shift, set mod_byte\n\n"
if_str_mod = "  if(masked _state == %d){\t\t//%s\n    mod_byte |= %d;\n }\n"

start_exact = "\n  //exact matches that depend on shift, some are macros\n\n"
if_str_exact1 = "  if(_state == %d){\t\t//%s\n"
if_str_exact2 = "    send(%d, %d, mod_byte);\n"
if_str_exact3 = "  }\n"

start_plain ="\n  //matches disregarding shift\n  //set shift_flag, clear shift bit in state\n  bool shift_flag=_state && 1<<SHIFT_SWITCH_NUM; \n  _state &= ~ 1<<SHIFT_SWITCH_NUM;\n"
if_str_plain ="  if(_state == %d){\t\t//%s\n    send(%d, shift_flag, mod_byte);\n  }\n"

bottom_str = "  else{\n    //only mods are down\n    send(0, shift_flag, mod_byte);}\n}"

# write c file
# todo warn if there are unknown or missing keys in keymap file
def write_c(map, shift_switch_num):
    f_c = open('translate.c', 'w')
    shiftable_keys = shiftable_codes.keys()
    exact_keys = exact_codes.keys()
    modifier_keys = modifiers.keys()
    print map 
    exit(1)
    map_keys = map.keys()

    f_c.write(top_str % shift_switch_num)
    for name in modifier_keys:
        if name in map_keys:
            f_c.write( if_str_mod % (map[name], name, modifiers[name]) )

    f_c.write(start_exact)
    for name in exact_keys:
        if name in map_keys:
            f_c.write( if_str_exact1 % (map[name], name) )
            print exact_codes[name]
            for k in exact_codes[name]:
                f_c.write( if_str_exact2 % (k[0], k[1]) )
            f_c.write( if_str_exact3)

    f_c.write(start_plain)
    for name in shiftable_keys:
        if name in map_keys:
            f_c.write( if_str_plain % (map[name], name, shiftable_codes[name]) )

    f_c.write( bottom_str)
    print "done writing translate.c"


(map, shift_switch_num) = parse_kmap("keymaps/smalldvorak.kmap")
print map
write_c(map, shift_switch_num)
