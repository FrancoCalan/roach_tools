#!/usr/bin/env python

import argparse
from valon_synth import *
# SYNTH_A = 0, SYNTH_B = 8
synth = {"A" : SYNTH_A, "B" : SYNTH_B}

parser = argparse.ArgumentParser(description='Get and set synthesizer clock.')
parser.add_argument("-u", "--usb", dest="usb",
                   default="/dev/ttyUSB0", help="USB path.")
parser.add_argument("-s", "--synth", type=str, dest="synth",
                   default = "B", help="Chosen synthesizer.")
parser.add_argument("-f", "--freq", type=int, dest="freq",
                   default=None, help="Set frequency.")
parser.add_argument("-l", "--lev", type=int, dest="level",
                   default=None, help="Set power level.")
parser.add_argument("-i", "--int_ref", dest="int_ref", action="store_true",
                   help="set internal reference")
parser.add_argument("-e", "--ext_ref", dest="ext_ref", action="store_true",
                   help="set external reference")
parser.set_defaults(ref=True)
args = parser.parse_args()

s = Synthesizer(args.usb)
try:
    synth_num = synth[args.synth]
except:
    print "Synth name error."
    exit()

synth_freq = s.get_frequency(synth_num)
synth_levl = s.get_rf_level(synth_num)
print "Frequency SYNTH_" + str(args.synth) + ": " + str(synth_freq) + "[MHz]"
print "RF level SYNTH_"  + str(args.synth) + ": " + str(synth_levl) + " (=" + str(synth_levl+2) + "[dBm])"
# False = internal, True = external
print "Reference : " + "external" if s.get_ref_select() else "internal"

if args.freq is not None:
    s.set_frequency(synth[args.synth], args.freq)
    synth_freq = s.get_frequency(synth_num)
    print "Updated frequency SYNTH_" + str(args.synth) + ": " + str(synth_freq) + "[MHz]"
    
if args.level is not None:
    s.set_rf_level(synth[args.synth], args.level)
    synth_levl = s.get_rf_level(synth_num)
    print "Updated power level SYNTH_" + str(args.synth) + ": " + str(synth_levl) + " (=" + str(synth_levl+2) + "[dBm])"

if args.int_ref:
    s.set_ref_select(False)
    print "Updated reference to internal"
if args.ext_ref:
    s.set_ref_select(True)
    print "Updated reference to external"

s.flash()
