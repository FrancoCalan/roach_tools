#!/usr/bin/env python

import sys, os
sys.path.append(os.getcwd())
from roach_tools.calanfpga import CalanFpga
from roach_tools.balance_mixer.bm_calibrator import BmCalibrator

fpga = CalanFpga()
fpga.initialize()
BmCalibrator(fpga).run_bm_test()
