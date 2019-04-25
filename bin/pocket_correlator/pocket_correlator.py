#!/usr/bin/env python

import sys, os
sys.path.append(os.getcwd())
from roach_tools.calanfpga import CalanFpga
from roach_tools.pocket_correlator.pocket_correlator import PocketCorrelator

fpga = CalanFpga()
fpga.initialize()
PocketCorrelator(fpga).run_pocket_correlator_test()
