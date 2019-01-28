#!/usr/bin/env python

import sys, os
sys.path.append(os.getcwd())
from roach_tools.calanfpga import CalanFpga
from roach_tools.frequency_response.frequency_response import FrequencyResponse

fpga = CalanFpga()
fpga.initialize()
FrequencyResponse(fpga).run_frequency_response_test()
