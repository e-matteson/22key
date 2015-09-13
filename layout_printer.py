#! /bin/python2

# from analyze_logs import make_reverse_layout

SHIFT_INDEX = 18

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

def print_layout(layout, all_keys_arranged, filename):
    f_cfg = open(filename, 'w')
    template=['%s\t\t', '%s%s%s%s   %s%s%s%s\t', '%s%s%s%s   %s%s%s%s\t', '  %s%s%s %s%s%s  \t']
  
    names_to_entries = {}
    for chord in layout.keys():
        for shifted in [0,1]:
            name = layout[chord][shifted]
            if name:
                binary = indices2binary(chord, shifted)
                names_to_entries[name] = [(name,), tuple(binary[0:8]), tuple(binary[8:16]), tuple(binary[16:22])]
                
    str = ""               
    for row in all_keys_arranged:
        # n=len(row)
        for i in range(4):
            for name in row:
                str+= template[i] % names_to_entries[name][i]
            str += '\n'    
        # str += '\n' + '#'*70 + '\n'    
        str += '\n'
    f_cfg.write(str)
    
def indices2binary(indices, shifted):
    press_symbol = "*"
    binary = ['.']*22
    for i in indices:
        binary[i] = press_symbol
    binary = reorder_optimizer2printer(binary)
    if shifted:
        binary[SHIFT_INDEX] = press_symbol
    return binary

def reorder_optimizer2original(binary):
    return [binary[i] for i in [21, 20, 19, 16, 17, 18, 14, 12, 10, 8, 0, 2, 4, 6, 15, 13, 11, 9, 1, 3, 5, 7]]

def reorder_printer2optimizer(binary):
    return [binary[i] for i in [11, 3, 10, 2, 9, 1, 8, 0, 12, 4, 13, 5, 14, 6, 15, 7, 18, 17, 16, 19, 20, 21]]

def reorder_optimizer2printer(binary):
    return [binary[i] for i in [7, 5, 3, 1, 9, 11, 13, 15, 6, 4, 2, 0, 8, 10, 12, 14, 18, 17, 16, 19, 20, 21]]

# f_cfg.write(str)

# print str
# print_layout({(4,):["a", "A"]})
        
                    
# unused_keys = ["KEY_F13", "KEY_F14", "KEY_F15", "KEY_F16", "KEY_F17", "KEY_F18", "KEY_F19", "KEY_F20", "KEY_F21", "KEY_F22", "KEY_F23", "KEY_F24", "KEY_Help", "KEY_Menu", "KP_NumLock", "KP_Divide", "KP_Multiply", "KP_Subtract", "KP_Add", "KP_Enter", "KP_1", "KP_2", "KP_3", "KP_4", "KP_5", "KP_6", "KP_7", "KP_8", "KP_9", "KP_0", "KP_Point", "KEY_NonUSBackslash", "KP_Equals","KEY_PrintScreen", "KEY_ScrollLock", "KEY_Pause", "KEY_Insert", "KEY_RightGUI","KEY_LeftGUI",   "KEY_RightControl", "KEY_RightShift", "KEY_RightAlt", "KEY_DeleteForward",
               

       

# "%s\t\t
# ....   ....\t


# %s\t\t%s\t\t%s\t\t%s\n....   ....\t....   ....\t....   ....\t....   ....\n....   ....\t....   ....\t....   ....\t....   ....\t....   ....\n  ... ...\t  ... ...\t  ... ...\t  ... ...\t  ... ...\n\n"
