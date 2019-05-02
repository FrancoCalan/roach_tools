#!/usr/bin/env python

import sys, os
sys.path.append(os.getcwd())
from roach_tools.calanfpga import CalanFpga
from roach_tools.multi_beam_former.mbf_calibrator_sync import MBFCalibratorSync

fpga = CalanFpga()
fpga.initialize()
MBFCalibratorSync(fpga).calibrate_mbf()
