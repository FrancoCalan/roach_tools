#!/usr/bin/env python

import sys, os
sys.path.append(os.getcwd())
from roach_tools.calanfpga import CalanFpga
from roach_tools.beamwidth_animator import BeamwidthAnimator

fpga = CalanFpga()
fpga.initialize()
BeamwidthAnimator(fpga).start_animation()
