#!/usr/bin/env python

import sys, corr
fpga = corr.katcp_wrapper.FpgaClient(sys.argv[1])
fpga.upload_program_bof(sys.argv[2], 3000)
