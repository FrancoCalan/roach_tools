#!/usr/bin/env python

import sys, os
sys.path.append(os.getcwd())
from roach_tools.calanfpga import CalanFpga
from roach_tools.vector_voltmeter.vvfreq_test import VVFreqTest

fpga = CalanFpga()
fpga.initialize()
VMFreqTest(fpga).run_vmfreq_test()
