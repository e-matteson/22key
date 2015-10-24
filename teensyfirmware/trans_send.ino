
#define SHIFT_SWITCH_NUM 104856 


void translate_and_send(uint32_t _state){
  /* Serial.println(_state); */
    //blank out mods except shift, set mod_byte
  char mod_byte = 0;
  //exact matches that depend on shift, some are macros

  //matches disregarding shift
  //set shift_flag, clear shift bit in state
  bool shift_flag=_state && 1<<SHIFT_SWITCH_NUM; 
  /* _state &= ~ 1<<SHIFT_SWITCH_NUM; */
  Serial.print("in tas: ");
  Serial.println(_state);
  if(_state == 32768){		//KEY_d
    send(7, shift_flag, mod_byte);
  }
  else if(_state == 131072){		//KEY_g
    send(10, shift_flag, mod_byte);
  }
  else if(_state == 65536){		//KEY_f
    send(9, shift_flag, mod_byte);
  }
  else if(_state == 8192){		//KEY_a
    send(4, shift_flag, mod_byte);
  }
  else if(_state == 16384){		//KEY_b
    send(5, shift_flag, mod_byte);
  }
  else if(_state == 4){		//KEY_m
    send(16, shift_flag, mod_byte);
  }
  else if(_state == 1){		//KEY_v
    send(25, shift_flag, mod_byte);
  }
  else if(_state == 4096){		//KEY_o
    send(18, shift_flag, mod_byte);
  }
  else if(_state == 128){		//KEY_n
    send(17, shift_flag, mod_byte);
  }
  else if(_state == 1048576){		//KEY_i
    send(12, shift_flag, mod_byte);
  }
  else if(_state == 512){		//KEY_h
    send(11, shift_flag, mod_byte);
  }
  else if(_state == 8){		//KEY_k
    send(14, shift_flag, mod_byte);
  }
  else if(_state == 16){		//KEY_j
    send(13, shift_flag, mod_byte);
  }
  else if(_state == 1024){		//KEY_u
    send(24, shift_flag, mod_byte);
  }
  else if(_state == 256){		//KEY_t
    send(23, shift_flag, mod_byte);
  }
  else if(_state == 2){		//KEY_w
    /* Serial.println("in 2"); */
    send(26, shift_flag, mod_byte);
  }
  else if(_state == 3072){		//KEY_q
    send(20, shift_flag, mod_byte);
  }
  else if(_state == 262144){		//KEY_p
    send(19, shift_flag, mod_byte);
  }
  else if(_state == 64){		//KEY_s
    send(22, shift_flag, mod_byte);
  }
  else if(_state == 2097152){		//KEY_x
    send(27, shift_flag, mod_byte);
  }
  else if(_state == 524288){		//KEY_y
    send(28, shift_flag, mod_byte);
  }
  else if(_state == 2048){		//KEY_e
    send(8, shift_flag, mod_byte);
  }
  else{
    //only mods are down
    Serial.println("else");
    send(0, shift_flag, mod_byte);
  }
}
