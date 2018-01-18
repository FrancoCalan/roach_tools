#!/usr/bin/env python

import sys, corr, time
fpga = corr.katcp_wrapper.FpgaClient(sys.argv[1])
time.sleep(0.5)
fpga.upload_bof(sys.argv[2], 60000)
