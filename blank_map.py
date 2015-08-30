#! /bin/python2


f_cfg = open('keymap2', 'w')


# decide how to deal with these - check and set flags first?
# what's difference between seding

names=[["KEY_leftshift", "KEY_leftcontrol", "KEY_leftalt", "KEY_escape"],
       ["KEY_A", "KEY_B", "KEY_C", "KEY_D", "KEY_E"],
       ["KEY_F", "KEY_G", "KEY_H", "KEY_I", "KEY_J"],
       ["KEY_K", "KEY_L", "KEY_M", "KEY_N", "KEY_O"],
       ["KEY_P", "KEY_Q", "KEY_R", "KEY_S", "KEY_T"],
       ["KEY_U", "KEY_V", "KEY_W", "KEY_X", "KEY_Y"],
       ["KEY_Z","KEY_enter", "KEY_space", "KEY_backslash", "KEY_tab"],
       [ "KEY_right", "KEY_left","KEY_down", "KEY_up"],
       ["KEY_home",  "KEY_end", "KEY_pageup", "KEY_pagedown"],
       ["KEY_1", "KEY_2", "KEY_3", "KEY_4", "KEY_5"],
       ["KEY_6", "KEY_7", "KEY_8", "KEY_9", "KEY_0"],
       ["KEY_F1", "KEY_F2", "KEY_F3", "KEY_F4", "KEY_F5", "KEY_F6"],
       ["KEY_F7", "KEY_F8", "KEY_F9", "KEY_F10", "KEY_F11", "KEY_F12"], 
       ["KEY_bang", "KEY_at", "KEY_hash", "KEY_dollar", "KEY_percent"],
       ["KEY_caret", "KEY_ampersand", "KEY_asterisk", "KEY_minus", "KEY_underscore"],
       ["KEY_equals",  "KEY_plus", "KEY_pipe", "KEY_semicolon", "KEY_colon"],
       ["KEY_quote", "KEY_doublequote", "KEY_slash", "KEY_question", "KEY_capslock"],
       ["macro_bracket", "macro_curly", "macro_paren", "KEY_grave", "KEY_tilde"],
       ["KEY_comma", "KEY_period", "KEY_leftangle", "KEY_rightangle","KEY_delete" ]]


syms=['%s\t\t', '....   ....\t\t', '....   ....\t\t', '  ... ...  \t\t']

str = ""
for row in names:
    n=len(row)
    for n in range(len(row)):
        str+= syms[0] % row[n]
    str += '\n' + syms[1]*len(row) + '\n'
    str += syms[2]*len(row) + '\n'
    str += syms[3]*len(row) + '\n\n'

f_cfg.write(str)
# print str
        
        
                    
# unused_keys = ["KEY_F13", "KEY_F14", "KEY_F15", "KEY_F16", "KEY_F17", "KEY_F18", "KEY_F19", "KEY_F20", "KEY_F21", "KEY_F22", "KEY_F23", "KEY_F24", "KEY_Help", "KEY_Menu", "KP_NumLock", "KP_Divide", "KP_Multiply", "KP_Subtract", "KP_Add", "KP_Enter", "KP_1", "KP_2", "KP_3", "KP_4", "KP_5", "KP_6", "KP_7", "KP_8", "KP_9", "KP_0", "KP_Point", "KEY_NonUSBackslash", "KP_Equals","KEY_PrintScreen", "KEY_ScrollLock", "KEY_Pause", "KEY_Insert", "KEY_RightGUI","KEY_LeftGUI",   "KEY_RightControl", "KEY_RightShift", "KEY_RightAlt", "KEY_DeleteForward",
               

       

# "%s\t\t
# ....   ....\t


# %s\t\t%s\t\t%s\t\t%s\n....   ....\t....   ....\t....   ....\t....   ....\n....   ....\t....   ....\t....   ....\t....   ....\t....   ....\n  ... ...\t  ... ...\t  ... ...\t  ... ...\t  ... ...\n\n"
