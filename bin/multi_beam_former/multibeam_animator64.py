#!/usr/bin/env python

import sys, os
sys.path.append(os.getcwd())
from roach_tools.calanfpga import CalanFpga
from roach_tools.multi_beam_former.multibeam_animator64 import MultibeamAnimator64

fpga = CalanFpga()
fpga.initialize()
MultibeamAnimator64(fpga).start_animation()
