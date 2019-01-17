#!/usr/bin/env python

import sys, os
sys.path.append(os.getcwd())
from roach_tools.calanfpga import CalanFpga
from roach_tools.kesteven_filter.beamwidth_animator import BeamwidthAnimator

fpga = CalanFpga()
fpga.initialize()
BeamwidthAnimator(fpga).start_animation()
