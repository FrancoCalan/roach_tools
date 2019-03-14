#!/usr/bin/env python

import sys, os
sys.path.append(os.getcwd())
from roach_tools.calanfpga import CalanFpga
from roach_tools.digital_sideband_separation.dss_calibrator import DssCalibrator

fpga = CalanFpga()
fpga.initialize()
dc = DssCalibrator(fpga)
if fpga.settings.sync_adcs:
    dc.synchronize_adcs()
dc.run_dss_test()
