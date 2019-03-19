#!/usr/bin/env python

import sys, os
sys.path.append(os.getcwd())
from roach_tools.calanfpga import CalanFpga
from roach_tools.multi_beam_former.multibeam_animator import MultibeamAnimator

fpga = CalanFpga()
fpga.initialize()
MultibeamAnimator(fpga).start_animation()
