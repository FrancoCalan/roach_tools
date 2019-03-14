#!/usr/bin/env python

import sys, os
sys.path.append(os.getcwd())
from roach_tools.calanfpga import CalanFpga
from roach_tools.frb_detector.frb_detector import FRBDetector

fpga = CalanFpga()
fpga.initialize()
FRBDetector(fpga).start_animation()
