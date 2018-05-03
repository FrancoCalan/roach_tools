#!/usr/bin/env python

from roach_tools.calanfpga import CalanFpga
from roach_tools.spectra_animator import SpectraAnimator

fpga = CalanFpga()
fpga.initialize()
SpectraAnimator(fpga).start_animation()
