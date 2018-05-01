#!/usr/bin/env python

import os, sys, importlib
from roach_tools.calanfpga import CalanFpga
from roach_tools.spectra_animator import SpectraAnimator

config_file = os.path.splitext(sys.argv[1])[0]
fpga = CalanFpga(importlib.import_module(config_file))
fpga.initialize()
SpectraAnimator(fpga).start_animation()
