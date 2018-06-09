#!/usr/bin/env python

import sys, os
sys.path.append(os.getcwd())
from roach_tools.calanfpga import CalanFpga
from roach_tools.adc_histogram import AdcHistogram

fpga = CalanFpga()
fpga.initialize()
AdcHistogram(fpga).start_animation()
