#!/usr/bin/env python

import sys, os
sys.path.append(os.getcwd())
from roach_tools.calanfpga import CalanFpga
from roach_tools.snapshot_animator import SnapshotAnimator

fpga = CalanFpga()
fpga.initialize()
SnapshotAnimator(fpga).start_animation()
