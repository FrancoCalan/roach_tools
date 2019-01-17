#!/usr/bin/env python

import sys, os
sys.path.append(os.getcwd())
from roach_tools.calanfpga import CalanFpga
from roach_tools.adc5g_calibration.adc5g_calibrator import Adc5gCalibrator

fpga = CalanFpga()
fpga.initialize()
Adc5gCalibrator(fpga).perform_calibrations()
