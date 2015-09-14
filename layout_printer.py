#! /bin/python2

import re
# from analyze_logs import make_reverse_layout


def print_layout_1col(layout):
    # print layout
    template='%s\n%s%s%s%s   %s%s%s%s\n%s%s%s%s   %s%s%s%s\n  %s%s%s %s%s%s\n\n'
# indices2binary(indices)
    str = ""
    for chord in layout.keys():
        print chord
        for shifted in [0,1]:
            if layout[chord][shifted]:
                str+= template % tuple([layout[chord][shifted]] + indices2binary(chord,shifted))
    print str




# dv_arranged = [[a o e u], [h t n s], [\' , . p], [g c r l], [; q j k], [m w v s], [y i x], [f d b],
#                "<right>", "<left>", "<down>", "<up>", "<home>", "<end>","<pgdn>", "<pgup>"
               
# ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", , "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "<del>", "<tab>",  "!", "@", "#", "$", "%", "^", "&", "*", "-", "_", "=", "+", "\\",  "|", ";",  ":",  "\'", '\"',  r"`", "~", ",", "<", ".", ">", r"/", "?", "[", "{", "(", "<cpslk>", "f1", "f2", "f3", "f4", "f5", "f6", "f7", "f8", "f9", "f10", "f11", "f12"]
# , "A"
# print binary2indices(indices2binary((0,),0))


# f_cfg.write(str)

# print str
# print_layout({(4,):["a", "A"]})
        
                    
# unused_keys = ["KEY_F13", "KEY_F14", "KEY_F15", "KEY_F16", "KEY_F17", "KEY_F18", "KEY_F19", "KEY_F20", "KEY_F21", "KEY_F22", "KEY_F23", "KEY_F24", "KEY_Help", "KEY_Menu", "KP_NumLock", "KP_Divide", "KP_Multiply", "KP_Subtract", "KP_Add", "KP_Enter", "KP_1", "KP_2", "KP_3", "KP_4", "KP_5", "KP_6", "KP_7", "KP_8", "KP_9", "KP_0", "KP_Point", "KEY_NonUSBackslash", "KP_Equals","KEY_PrintScreen", "KEY_ScrollLock", "KEY_Pause", "KEY_Insert", "KEY_RightGUI","KEY_LeftGUI",   "KEY_RightControl", "KEY_RightShift", "KEY_RightAlt", "KEY_DeleteForward",
               

       

# "%s\t\t
# ....   ....\t


# %s\t\t%s\t\t%s\t\t%s\n....   ....\t....   ....\t....   ....\t....   ....\n....   ....\t....   ....\t....   ....\t....   ....\t....   ....\n  ... ...\t  ... ...\t  ... ...\t  ... ...\t  ... ...\n\n"
