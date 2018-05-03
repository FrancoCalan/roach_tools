#!/usr/bin/env python

from roach_tools.calanfpga import CalanFpga
from roach_tools.adc_synchronator import AdcSynchronator

fpga = CalanFpga()
fpga.initialize()
AdcSynchronator(fpga).synchronize_adcs()
