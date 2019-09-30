#!/usr/bin/env python

import sys, os
sys.path.append(os.getcwd())
from roach_tools.calanfpga import CalanFpga
from roach_tools.balance_mixer.bm_opt_calibrator import BmOptCalibrator

fpga = CalanFpga()
fpga.initialize()
BmOptCalibrator(fpga).run_bm_opt_test()
