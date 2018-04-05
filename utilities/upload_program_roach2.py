#!/usr/bin/env python

import sys, os, time, telnetlib, argparse, corr

parser = argparse.ArgumentParser(description='Upload bofs files and program the to ROACH')
parser.add_argument('-i', '--ip', dest='roach_ip',
                    default=None, help='ROACH IP address.')
parser.add_argument('-p', '--port', dest='roach_port',
                    default=7147, type=int, help='ROACH port.')
parser.add_argument('-b', '--bof', dest='boffile',
                    default=None, help='bof file to upload.')
parser.add_argument('-s', '--skip_prog', dest='prog_fpga',
                    action='store_false', default=True, help='skip FPGA programming (assumes already programmed).')
parser.add_argument('-u', '--skip_upload', dest='upload_bof',
                    action='store_false', default=True, help='skip bof upload (assumes already in ROACH).')
args = parser.parse_args()

# connect ot roach
print "Connecting to ROACH... "
tn = telnetlib.Telnet(args.roach_ip, args.roach_port)
time.sleep(1)
print tn.read_until('\n'),
print tn.read_until('\n')

# upload bof
if args.upload_bof:
    print "Uploading bof... "
    tn.write('?uploadbof 3000 '+ args.boffile + '\n')
    time.sleep(1)
    print tn.read_until('\n'),
    os.system('nc ' + args.roach_ip + ' 3000 < ' + args.boffile)
    time.sleep(1)
    print tn.read_until('\n'),
    print tn.read_until('\n')
else:
    print "Skip uploading"
tn.close()

# program bof
if args.prog_fpga:
    print "Programming FPGA with bof... "
    fpga = corr.katcp_wrapper.FpgaClient(args.roach_ip, args.roach_port)
    time.sleep(1)
    fpga.progdev(os.path.basename(args.boffile))
    print 'ok'
else:
    print "Skip programming"

print "done"
