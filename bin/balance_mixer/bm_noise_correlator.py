#!/usr/bin/env python

import sys, os
sys.path.append(os.getcwd())
from roach_tools.calanfpga import CalanFpga
from roach_tools.balance_mixer.bm_noise_correlator import BmNoiseCorrelator

fpga = CalanFpga()
fpga.initialize()
BmNoiseCorrelator(fpga).start_animation()
