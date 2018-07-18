import telnetlib, time

class Generator():
    """
    Controls a signal generator source using Telnet communication.
    """
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        print 'Connecting to generator %s on port %i... ' %(self.ip, self.port)
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
