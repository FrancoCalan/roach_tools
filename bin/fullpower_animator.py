#!/usr/bin/env python

import sys, os
sys.path.append(os.getcwd())
from roach_tools.calanfpga import CalanFpga
from roach_tools.multi_beam_former.fullpower_animator import FullpowerAnimator

fpga = CalanFpga()
fpga.initialize()
FullpowerAnimator(fpga).start_animation()
