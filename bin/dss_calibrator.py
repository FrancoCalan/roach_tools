#!/usr/bin/env python

import sys, os
sys.path.append(os.getcwd())
from roach_tools.calanfpga import CalanFpga
from roach_tools.dss_calibrator import DssCalibrator

fpga = CalanFpga()
fpga.initialize()
if fpga.settings.cal_adcs:
    fpga.calibrate_adcs()
DssCalibrator(fpga).run_consts_computation()
#DssCalibrator(fpga).run_srr_computation()
