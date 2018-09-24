#!/usr/bin/env python

import sys, os
sys.path.append(os.getcwd())
from roach_tools.calanfpga import CalanFpga
from roach_tools.dss_calibrator import DssCalibrator

fpga = CalanFpga()
fpga.initialize()
if fpga.settings.cal_adcs:
    fpga.calibrate_adcs()
dc = DssCalibrator(fpga)
if fpga.settings.sync_adcs:
    dc.synchronize_adcs()
dc.run_dss_test()
