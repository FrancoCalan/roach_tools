#!/usr/bin/env python

import sys, corr, time, argparse

parser = argparse.ArgumentParser(description='Upload bofs files and program the to ROACH')
parser.add_argument('-i', '--ip', dest='roach_ip',
                    default=None, help='ROACH IP address.')
parser.add_argument('-p', '--port', dest='roach_port',
                    default=7147, type=int, help='ROACH port.')
parser.add_argument('-b', '--bof', dest='boffile',
                    default=None, help='bof file to upload.')
parser.add_argument('-f', '--force_upload', dest='force',
                    action='store_true', default=False, help='delete bof with same name (if exists), and replace it with new one.')
parser.add_argument('-s', '--skip_prog', dest='prog_fpga',
                    action='store_false', default=True, help='skip FPGA programming (assumes already programmed).')
parser.add_argument('-u', '--skip_upload', dest='upload_bof',
                    action='store_false', default=True, help='skip bof upload (assumes already in ROACH).')
args = parser.parse_args()

print "Connecting to ROACH... "
fpga = corr.katcp_wrapper.FpgaClient(args.roach_ip)
time.sleep(0.5)
if fpga.is_connected():
    print 'ok'
else:
    raise Exception('Unable to connect to ROACH')

# upload bof
if args.upload_bof:
    print "Uploading bof... "
    fpga.upload_bof(args.boffile, 60000, force_upload=True)
    time.sleep(0.5)
    print "ok"
else:
    print "Skip uploading"

# program bof
if args.prog_fpga:
    print "Programming FPGA with bof... "
    fpga.progdev(args.boffile)
    print "ok"
else:
    print "Skip programming"

print "done"
