import numpy as np
from itertools import chain
from dummy_generator import DummyGenerator

class DummyFpga():
    """
    Emulates a ROACH connection. Is used for debugging purposes for the rest
    of the code.
    """
    def __init__(self, settings):
        self.settings = settings
        self.generator = DummyGenerator(1.0/(2*self.settings.bw*1e6))
        self.regs = []

        # add registers from config file
        for reg in settings.set_regs:
            self.regs.append({'name' : reg['name'], 'val' : 0})
        for reg in settings.reset_regs:
            self.regs.append({'name' : reg, 'val' : 0})

        # add snapshots
        try:
            self.snapshots = self.settings.snapshots
        except:
            pass

        # add spectrometers brams
        if isinstance(self.settings.spec_info['bram_names'], str):
            self.spec_brams = self.settings.spec_info['bram_names']
        elif isinstance(self.settings.spec_info['bram_names'], list):
            self.spec_brams = list(chain.from_iterable(self.settings.spec_info['bram_names'])) # flatten list
        else:
            self.spec_brams = []

    def is_connected(self):
        """
        Emulates ROACH connection test. Always True.
        """
        return True

    def upload_bof(self, boffile, port, force_upload=False):
        """
        Emulates the uploading of the model to the ROACH. Does nothing.
        """
        pass
    
    def progdev(self, boffile):
        """
        Emulates the programming of the FPGA. Does nothing.
        """
        pass

    def est_brd_clk(self):
        """
        Emulates FPGA clock estimation.
        """
        return 2*self.settings.bw

    def write_int(self, reg_name, val):
        """
        Writes an int value into the Dummy ROACH.
        """
        try:
            write_reg = [reg for reg in self.regs if reg['name'] == reg_name][0]
        except:
            raise Exception('No register found with name ' + reg_name)
        write_reg['val'] = val

    def listbof(self):
        """
        List nothing
        """
        return []

    def listdev(self):
        """
        List dummy registers.
        """
        return self.regs + self.snapshots + self.spec_brams

    def read_uint(self, reg_name):
        """
        Reads the int value from the Dummy ROACH.
        """
        try:
            return [reg['val'] for reg in self.regs if reg['name'] == reg_name][0]
        except:
            raise Exception('No register found with name ' + reg_name)
    
    def get_generator_signal(self, nsamples, delay=None):
        """
        Get the generator signal, clipped to simulate ADC saturation, and casted to the
        corresponding type to simulate ADC bitwidth.
        """
        if delay is None:
            signal = np.clip(self.generator.get_signal(nsamples), -128, 127)
        else:
            signal = np.clip(self.generator.get_signal(nsamples, phase=0), -128, 127)
            signal = np.roll(signal, delay)
        return signal.astype('>i1')

    def snapshot_get(self, snapshot, man_trig=True, man_valid=True, arm=True):
        """
        Returns snapshot signal given by generator.
        """
        if snapshot in self.snapshots:
            snap_data = self.get_generator_signal(self.settings.snap_samples)
        else:
            raise Exception("Snapshot not defined in config file.")
        
        return {'data' : snap_data}

    def read(self, bram, nbytes, offset=0):
        """
        Returns the proper simulated bram data given the bram name.
        """
        if bram in self.spec_brams:
            # Returns spectra of generator signal accumulated acc_len times.
            acc_len = self.read_uint('acc_len')
            spec_len = get_ndata(nbytes, self.settings.spec_info['data_type'])
            spec_dtype = self.settings.spec_info['data_type']
            spec = np.zeros(spec_len, dtype=spec_dtype)

            for _ in range(acc_len):
                signal = self.get_generator_signal(2*spec_len)
                spec += np.square(np.abs(np.fft.rfft(signal)[:spec_len])).astype(spec_dtype)

            return spec.tobytes()

        # Raise exception if the bram is not declared in the config file
        else: 
            raise Exception("BRAM " + bram + " not defined in config file.")

def get_ndata(nbytes, data_type):
    """
    Computes the number of data values given the total number of
    bytes in the data array, and the expected data type of the bram.
    """
    return nbytes / np.dtype(data_type).alignment
