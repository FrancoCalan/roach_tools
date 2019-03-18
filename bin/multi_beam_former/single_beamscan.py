#!/usr/bin/env python

import sys, os
sys.path.append(os.getcwd())
from roach_tools.calanfpga import CalanFpga
from roach_tools.multi_beam_former.single_beamscan import SingleBeamscan

fpga = CalanFpga()
fpga.initialize()
SingleBeamscan(fpga).perform_single_beamscan()
