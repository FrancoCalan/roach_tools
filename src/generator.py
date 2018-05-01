###############################################################################
#                                                                             #
#   Millimeter-wave Laboratory, Department of Astronomy, University of Chile  #
#   http://www.das.uchile.cl/lab_mwl                                          #
#   Copyright (C) 2017 Franco Curotto                                         #
#                                                                             #
#   This program is free software; you can redistribute it and/or modify      #
#   it under the terms of the GNU General Public License as published by      #
#   the Free Software Foundation; either version 3 of the License, or         #
#   (at your option) any later version.                                       #
#                                                                             #
#   This program is distributed in the hope that it will be useful,           #
#   but WITHOUT ANY WARRANTY; without even the implied warranty of            #
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the             #
#   GNU General Public License for more details.                              #
#                                                                             #
#   You should have received a copy of the GNU General Public License along   #
#   with this program; if not, write to the Free Software Foundation, Inc.,   #
#   51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.               #
#                                                                             #
###############################################################################

import telnetlib, time

class Generator():
    """
    Controls a signal generator source using Telnet communication.
    """
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        print 'Connecting to generator %s on port %i... ' %(self.ip, self.port),
        self.connection = telnetlib.Telnet(self.ip, self.port)
        print "ok"
        
    def turn_output_on(self):
        """
        Turn on the output of the generator.
        """
        self.connection.write('outp on\r\n')
        time.sleep(0.1)
        print "Generator output on"

    def turn_output_off(self):
        """
        Turn off the output of the generator.
        """
        self.connection.write('outp off\r\n')
        time.sleep(0.1)
        print "Generator output off"

    def set_freq_hz(self, freq):
        """
        Set the generator frequency. The frequency paramenter is in Hz.
        """
        self.connection.write('freq %s\r\n'% str(freq))
        time.sleep(0.2)
        print "Generator frequency set to %sMHz"% freq

    def set_freq_mhz(self, freq):
        """
        Set the generator frequency. The frequency paramenter is in MHz.
        """
        self.connection.write('freq %s\r\n'% str(1000000*freq))
        time.sleep(0.2)
        print "Generator frequency set to %sHz"% freq

    def set_power_dbm(self, power):
        """
        Set generator output power. The power paramenter is in dBm.
        """
        self.connection.write('power %s dbm\r\n'% str(power))
        time.sleep(0.1)
        print "Generator power set to %sdBm"% power

    def close_connection(self):
        """
        Close connection with generator.
        """
        self.connection.close()
        print "Connection with generator closed"
