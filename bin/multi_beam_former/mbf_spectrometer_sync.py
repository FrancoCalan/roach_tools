#!/usr/bin/env python

import sys, os
sys.path.append(os.getcwd())
from roach_tools.calanfpga import CalanFpga
from roach_tools.multi_beam_former.mbf_spectrometer_sync import MBFSpectrometerSync

fpga = CalanFpga()
fpga.initialize()
MBFSpectrometerSync(fpga).start_animation()
