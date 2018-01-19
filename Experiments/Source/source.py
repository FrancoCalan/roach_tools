import telnetlib, time

class Source():
    """
    Controls a signal generator source using Telnet communication.
    """
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.connection = telnetlib.Telnet(self.ip, self.port)
        
    def turn_on(self):
        """
        Turn on source.
        """
        self.connection.write('outp on\r\n')
        time.sleep(0.1)

    def turn_off(self):
        """
        Turn off source.
        """
        self.connection.write('outp off\r\n')
        time.sleep(0.1)

    def set_freq_hz(self, freq):
        """
        Set the source frequency. The frequency paramenter is in Hz.
        """
        self.connection.write('freq %s\r\n'% str(freq))
        time.sleep(0.2)

    def set_freq_mhz(self, freq):
        """
        Set the source frequency. The frequency paramenter is in MHz.
        """
        self.connection.write('freq %s\r\n'% str(1000000*freq))
        time.sleep(0.2)

    def set_power_dbm(self, power):
        """
        Set source output power. The power paramenter is in dBm.
        """
        self.connection.write('power %s dbm\r\n'% str(power))
        time.sleep(0.1)

    def close_connection(self):
        """
        Close connection with source.
        """
        self.connection.close()
