#!/usr/bin/env python

import sys, os
sys.path.append(os.getcwd())
from roach_tools.calanfpga import CalanFpga
from roach_tools.balance_mixer.bm_auto_calibrator2 import BmAutoCalibrator

fpga = CalanFpga()
fpga.initialize()
BmAutoCalibrator(fpga).run_bm_auto_test()
