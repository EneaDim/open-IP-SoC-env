// Include source files 
`include "ips/pkgs/top_pkg.sv"
`include "ips/pkgs/prim_util_pkg.sv"
`include "ips/pkgs/prim_mubi_pkg.sv"
`include "ips/pkgs/prim_secded_pkg.sv"
`ifndef SYN
  `include "rtl/fft_fsm.v"
`else
  `include "verilog/primitives.v"
  `include "verilog/sky130_fd_sc_hd.v"
  `include "syn/fft_fsm_synth.v"
`endif
