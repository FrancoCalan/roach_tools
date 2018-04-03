#!/usr/bin/env python

import sys, corr, time, telnetlib, argparse

parser = argparse.ArgumentParser(description='Upload bofs files and program the to ROACH')
parser.add_argument('-i', '--ip', dest='roach_ip',
                    default=None, help='ROACH IP address.')
parser.add_argument('-p', '--port', dest='roach_port',
                    default=7147, type=int, help='ROACH port.')
parser.add_argument('-b', '--bof', dest='boffile',
                    default=None, help='bof file to upload.')
parser.add_argument('-f', '--force_upload', dest='force',
                    action='store_true', help='delete bof with same name (if exists), and replace it with new one.')
args = parser.parse_args()

print "Connecting to ROACH... "
fpga = corr.katcp_wrapper.FpgaClient(args.roach_ip)
time.sleep(0.5)
if fpga.is_connected():
    print 'ok'
else:
    raise Exception('Unable to connect to ROACH')

# Check if bof already exists
bof_exists = args.boffile in fpga.listbof()
if bof_exists:
    print "boffile already exists."
    if args.force:
        print "Force: deleting old boffile... "
        tn = telnetlib.Telnet(args.roach_ip, args.roach_port)
        time.sleep(0.5)
        tn.write('?delbof ' + args.boffile + '\n')
        time.sleep(0.5)
        tn_msg = tn.read_until('ok')
        print 'ok'
        print tn_msg
        tn.close()
    else: 
        print "Exiting. If you want to replace the current bof use the --force_upload option."
        exit()

# upload bof
print "Uploading bof... "
fpga.upload_bof(args.boffile, 60000, timeout=20)
time.sleep(0.5)
print "ok"

# program bof
print "Programming bof... "
fpga.progdev(args.boffile)
print "ok"
print "done"
