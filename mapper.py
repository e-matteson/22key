#! /bin/python2

import re

# Format of keymap.cfg:
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
#     21 20 19 18         17 16 15 14
#     13 12 11 10         9  8  7  6
#           5  4  3    2  1  0



bit_order = range(32);
PADWIDTH = 10; #22 keys, uint32




########## structure of .c file
top_str = "//#include avr stuff? \nvoid translate(uint32_t state){\n\n    //blank out mods except shift, set mod_byte\n\n"

if_str_mod = "  if(masked _state == %d){\t\t//%s\n    mod_byte |= %d;\n }\n"

start_exact = "\n  //exact matches that depend on shift, some are macros\n\n"
if_str_exact1 = "  if(_state == %d){\t\t//%s\n"
if_str_exact2 = "    send(%d, %d, mod_byte);\n"
if_str_exact3 = "  }\n"

start_plain ="\n  //matches disregarding shift\n  set shift_flag, blank out shift bit in _state\n"
if_str_plain ="  if(_state == %d){\t\t//%s\n    send(%d, shift_flag, mod_byte);\n  }\n"

bottom_str = "  else{\n    //only mods are down\n    send(0, shift_flag, mod_byte);}\n}"



########## HID usage code / macro dictionaries

plain_codes = dict(KEY_A=4, KEY_B=5, KEY_C=6, KEY_D=7, KEY_E=8, KEY_F=9, KEY_G=10, KEY_H=11, KEY_I=12, KEY_J=13, KEY_K=14, KEY_L=15, KEY_M=16, KEY_N=17, KEY_O=18, KEY_P=19, KEY_Q=20, KEY_R=21, KEY_S=22, KEY_T=23, KEY_U=24, KEY_V=25, KEY_W=26, KEY_X=27, KEY_Y=28, KEY_Z=29, KEY_enter=40, KEY_delete=42, KEY_tab=43, KEY_space=44, KEY_capslock=57, KEY_F1=58, KEY_F2=59, KEY_F3=60, KEY_F4=61, KEY_F5=62, KEY_F6=63, KEY_F7=64, KEY_F8=65, KEY_F9=66, KEY_F10=67, KEY_F11=68, KEY_F12=69, KEY_home=74, KEY_pageup=75, KEY_end=77, KEY_pagedown=78, KEY_right=79, KEY_left=80, KEY_down=81, KEY_up=82)

shift = 1
exact_codes = dict(KEY_1=[(30,0)], KEY_2=[(31,0)], KEY_3=[(32,0)], KEY_4=[(33,0)], KEY_5=[(34,0)], KEY_6=[(35,0)], KEY_7=[(36,0)], KEY_8=[(37,0)], KEY_9=[(38,0)], KEY_0=[(39,0)], KEY_bang=[(30,1)], KEY_at=[(31,shift)], KEY_hash=[(32,shift)], KEY_dollar=[(33,shift)], KEY_percent=[(34,shift)], KEY_caret=[(35,shift)], KEY_ampersand=[(36,shift)], KEY_asterisk=[(37,shift)], KEY_minus=[(45,0)], KEY_underscore=[(45,shift)],  KEY_equals=[(46,0)], KEY_plus=[(46,shift)], KEY_backslash=[(49,0)], KEY_pipe=[(49,shift)], KEY_semicolon=[(51,0)],  KEY_colon=[(51,shift)], KEY_quote=[(52,0)], KEY_doublequote=[(52,shift)], KEY_grave=[(53,0)], KEY_tilde=[(53,shift)], KEY_comma=[(54,0)], KEY_leftangle=[(54,shift)], KEY_period=[(55,0)],  KEY_rightangle=[(55,shift)], KEY_slash=[(56,0)], KEY_question=[(56,shift)], macro_bracket=[(47,0),(48,0),(80,0)], macro_curly=[(47,shift),(48,shift),(80,0)], macro_paren=[(38,shift),(39,shift),(80,0)])

modifiers =  dict(KEY_leftcontrol=1, KEY_leftalt=4) #not usage codes, bitmasks for mod_byte!
# todo shift (and escape?) is special
 # KEY_LeftShift=225,    KEY_Escape=41 
# modifiers =  {KEY_LeftControl=224, KEY_LeftShift=225, KEY_LeftAlt=226, KEY_Escape=41}


def parse_original_format(filename):
    f_cfg = open(filename, 'r')
    
    # parse keymap file
    text = f_cfg.read()
    text = re.sub('\.', '0', text)
    text = re.sub('x', '1', text)
    map = re.findall('^((?:[^#\n]+\n){4})', text, flags=re.MULTILINE)
    map =  [re.split('\s+', x.strip()) for x in map]
    return map

def parse_new_format(filename):
    f_cfg = open(filename, 'r')
    map = {}
    while 1:
        lines = []
        while len(lines) < 4:
            l = f_cfg.readline()
            if l == "":
                if len(lines) != 0:
                    print "WARNING: lines ignored at end of file"
                return map
                
            if(l[0].strip() != "#"  and l.strip() != ""):
                # print "something: %s" % l
                lines.append(re.split('[ \t]+', l.strip()))

        for b in range(len(lines[0])):
            chunks = []
            [chunks.extend(lines[row][b*2:b*2+2]) for row in range(1,4)]
            print '*************************'
            print chunks
            chunks = [re.sub('\.', '0', c) for c in chunks]
            chunks = [re.sub('[^0]', '1', c) for c in chunks]
            chunks = '0'*PADWIDTH + ''.join(chunks)
            chunks = ''.join([chunks[j] for j in bit_order])
            chunks = int(chunks,2)
            map[lines[0][b]] = chunks
            

# write c file
# todo warn if there are unknown or missing keys in keymap file    
def write_c(map):
    f_c = open('translate.c', 'w')
    plain_keys = plain_codes.keys()
    exact_keys = exact_codes.keys()
    modifier_keys = modifiers.keys()
    map_keys = map.keys()
    
    f_c.write(top_str)
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
    for name in plain_keys:
        if name in map_keys:
            f_c.write( if_str_plain % (map[name], name, plain_codes[name]) )
        
    f_c.write( bottom_str)


map = parse_new_format("keymap")
write_c(map)
