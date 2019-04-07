#!/usr/bin/env python

import sys, os
sys.path.append(os.getcwd())
from roach_tools.calanfpga import CalanFpga
from roach_tools.adc_synchronator_time.adc_synchronator_time import AdcSynchronatorTime

fpga = CalanFpga()
fpga.initialize()
AdcSynchronatorTime(fpga).synchronize_adcs()
