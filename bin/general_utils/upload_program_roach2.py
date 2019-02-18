#!/usr/bin/env python

import sys, corr, argparse, telnetlib, os, time

parser = argparse.ArgumentParser(description="Upload and program .bof/.bof.gz models to ROACH2 board.")
parser.add_argument("-i", "--ip", type=str, dest="roach_ip", 
                    default="192.168.1.12", help="ROACH IP address.")
parser.add_argument("-b", "--bof", type=str, dest="boffile",
                    help=".bof/.bof.gz file or path to program.")
parser.add_argument("-u", "--upload", dest="upload", action="store_true",
                    help="Upload boffile to ROACH's permanent memory.")
parser.add_argument("-p", "--program", dest="program", action="store_true",
                    help="Program boffile to FPGA.")
args = parser.parse_args()

fpga = corr.katcp_wrapper.FpgaClient(args.roach_ip)

if args.upload:
    print "Uploading bof into ROACH's permanent memory..."
    tn = telnetlib.Telnet(args.roach_ip, 7147)
    tn.write("?uploadbof 3000 " + args.boffile + "\n")
    time.sleep(1)
    os.system("nc " + args.roach_ip + " 3000 < " + args.boffile)
    print "\nROACH message:"
    print tn.read_very_eager()
    print "done"
    tn.close()

if args.program:
    print "Programming FPGA..."
    boffile_basename = os.path.basename(args.boffile)
    fpga.progdev(args.boffile)
    print "done"

print "All done."
