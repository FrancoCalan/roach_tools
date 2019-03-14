#!/usr/bin/env python

import sys, os
sys.path.append(os.getcwd())
from roach_tools.calanfpga import CalanFpga
from roach_tools.multi_beam_former.mbf_calibrator import MBFCalibrator

fpga = CalanFpga()
fpga.initialize()
MBFCalibrator(fpga).calibrate_mbf()
