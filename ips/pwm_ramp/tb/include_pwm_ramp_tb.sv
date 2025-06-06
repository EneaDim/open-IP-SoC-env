// Include source files 
`include "ips/pkgs/top_pkg.sv"
`include "ips/pkgs/prim_util_pkg.sv"
`include "ips/pkgs/prim_mubi_pkg.sv"
`include "ips/pkgs/prim_secded_pkg.sv"
`ifndef SYN
  `include "rtl/pwm_ramp.v"
`else
  `include "verilog/primitives.v"
  `include "verilog/sky130_fd_sc_hd.v"
  `include "syn/pwm_ramp_synth.v"
`endif
