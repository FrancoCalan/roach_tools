import numpy as np

class DummyGenerator():
    """
    Emulates a signal generator that can produces sinusoid and noise signals.
    """
    def __init__(self, Ts):
        self.Ts = Ts
        self.output_on = True
        self.off_power = 0
        self.freq = 10e6
        self.power = 0

    def turn_output_on(self):
        """
        Turn on the output of the generator.
        """
        self.on = True
        print "Generator output on"

    def turn_output_off(self):
        """
        Turn off the output of the generator.
        """
        self.on = False
        print "Generator output off"

    def set_freq_hz(self, freq):
        """
        Set the generator frequency. The frequency paramenter is in Hz.
        """
        self.freq = freq
        print "Generator frequency set to %sMHz"% freq

    def set_freq_mhz(self, freq):
        """
        Set the generator frequency. The frequency paramenter is in MHz.
        """
        self.freq = 1e6*freq
        print "Generator frequency set to %sHz"% freq

    def set_power_dbm(self, power):
        """
        Set generator output power. The power paramenter is in dBm.
        """
        self.power = power
        print "Generator power set to %sdBm"% power

    def close_connection(self):
        """
        Close connection with generator.
        """
        pass
        print "Connection with generator closed"

    def get_signal(self, nsamples):
        """
        Returns the corresponding signal array.
        """
        random_signal = 10**(self.off_power/10.0) * np.random.randn(nsamples)
        # if output is off, return a random Gaussian signal
        if not self.output_on:
            return random_signal
        # is output is on, return a sinusoidal signal mixed with Gaussian noise
        else:
            corrected_power = 100 * 10**(self.power/10.0)
            time_arr = gen_time_arr(self.Ts, nsamples)
            phase = 2*np.pi*np.random.random()
            sin_signal = corrected_power * np.sin(2*np.pi*self.freq*time_arr + phase)
            return  sin_signal + random_signal

def gen_time_arr(Ts, nsamples):
    """
    Generates a time array for a sampling signal given the sampling
    period (Ts) and the number of samples (nsamples).
    """
    return np.linspace(0, Ts*(nsamples-1), nsamples)
