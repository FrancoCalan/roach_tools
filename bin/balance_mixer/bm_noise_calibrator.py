#!/usr/bin/env python

import sys, os
sys.path.append(os.getcwd())
from roach_tools.calanfpga import CalanFpga
from roach_tools.balance_mixer.bm_noise_calibrator import BmNoiseCalibrator

fpga = CalanFpga()
fpga.initialize()
BmNoiseCalibrator(fpga).run_bm_noise_test()
