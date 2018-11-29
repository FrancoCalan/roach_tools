#!/usr/bin/env python

import sys, os
sys.path.append(os.getcwd())
from roach_tools.calanfpga import CalanFpga
from roach_tools.kestfilt_animator import KestfiltAnimator

fpga = CalanFpga()
fpga.initialize()
KestfiltAnimator(fpga).start_animation()
