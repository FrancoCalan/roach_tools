#!/usr/bin/env python

import sys, os
sys.path.append(os.getcwd())
from roach_tools.calanfpga import CalanFpga
from roach_tools.balance_mixer.bm_tone_lnr_computation import BmToneLnrComputation

fpga = CalanFpga()
fpga.initialize()
BmToneLnrComputation(fpga).run_lnr_computation()
