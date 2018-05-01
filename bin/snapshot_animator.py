#!/usr/bin/env python

import os, sys, importlib
from roach_tools.calanfpga import CalanFpga
from roach_tools.snapshot_animator import SnapshotAnimator

config_file = os.path.splitext(sys.argv[1])[0]
fpga = CalanFpga(importlib.import_module(config_file))
fpga.initialize()
SnapshotAnimator(fpga).start_animation()
