#!/usr/bin/env python

import sys, os
sys.path.append(os.getcwd())
from roach_tools.calanfpga import CalanFpga
from roach_tools.adc_synchronator_freq.adc_synchronator_freq import AdcSynchronatorFreq

fpga = CalanFpga()
fpga.initialize()
AdcSynchronatorFreq(fpga).synchronize_adcs()
