package fft_fsm_pkg;
  typedef enum logic [2:0] { 
    IDLE, 
    ACTIVE_WRITE,
    READ_1,
    READ_2,
    COMPUTE,
    WRITE_RESULT_1,
    WRITE_RESULT_2,
    DONE
  } state_fsm ;

endpackage
