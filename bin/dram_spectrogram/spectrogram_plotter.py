#!/usr/bin/env python

import sys, os
sys.path.append(os.getcwd())
from roach_tools.calanfpga import CalanFpga
from roach_tools.dram_spectrogram.dram_spectrogram_plotter import DramSpectrogramPlotter

fpga = CalanFpga()
fpga.initialize()
DramSpectrogramPlotter(fpga).show_plot()
