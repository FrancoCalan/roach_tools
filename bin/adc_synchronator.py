#!/usr/bin/env python

import sys, os
sys.path.append(os.getcwd())
from roach_tools.calanfpga import CalanFpga
from roach_tools.adc_synchronator import AdcSynchronator

fpga = CalanFpga()
fpga.initialize()
if fpga.settings.cal_adcs:
    fpga.calibrate_adcs()
AdcSynchronator(fpga).synchronize_adcs()
