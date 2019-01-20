#!/usr/bin/env python

import sys, os
sys.path.append(os.getcwd())
from roach_tools.calanfpga import CalanFpga
from roach_tools.transfer_function import TransferFunction

fpga = CalanFpga()
fpga.initialize()
TransferFunction(fpga).run_transfer_function_test()
