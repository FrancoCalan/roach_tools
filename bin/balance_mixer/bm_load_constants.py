#!/usr/bin/env python

import sys, os
sys.path.append(os.getcwd())
from roach_tools.calanfpga import CalanFpga
from roach_tools.balance_mixer.bm_load_constants import BmLoadConstants

fpga = CalanFpga()
fpga.initialize()
BmLoadConstants(fpga).load_constants()
