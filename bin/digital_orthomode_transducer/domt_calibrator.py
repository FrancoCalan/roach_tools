#!/usr/bin/env python

import sys, os
sys.path.append(os.getcwd())
from roach_tools.calanfpga import CalanFpga
from roach_tools.digital_orthomode_transducer.domt_calibrator import DomtCalibrator

fpga = CalanFpga()
fpga.initialize()
DomtCalibrator(fpga).run_domt_test()
