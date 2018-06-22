#!/usr/bin/env python

import sys, os, telnetlib, time

roach_ip = sys.argv[1]
bof_path = sys.argv[2]
bof_name = os.path.basename(bof_path)

tn = telnetlib.Telnet(roach_ip, 7147)
tn.write("?uploadbof 3000 " + bof_name + "\n")
time.sleep(1)
os.system("nc " + roach_ip + " 3000 < " + bof_path)

print tn.read_very_eager()
tn.close()
