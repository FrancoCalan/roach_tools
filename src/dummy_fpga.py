import struct
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
        self.snapshots = []
        try:
            for snap_data in self.settings.snapshots:
                self.snapshots += snap_data['names']
        except:
            pass
        # add snapshots register
        for snapshot in self.snapshots:
            self.regs.append({'name' : snapshot+'_ctrl', 'val' : 0})
            print self.regs

        # add spectrometers brams
        try:
            self.spec_brams = list(chain.from_iterable(self.settings.spec_info['bram_list2d'])) # flatten list
        except:
            self.spec_brams = []

        # add conv_info brams
        try:
            self.conv_info_chnl_brams = self.settings.conv_info_chnl['bram_list']
        except:
            self.conv_info_chnl_brams = []
        try:
            self.conv_info_max_brams = [self.settings.conv_info_max['bram_name']]
        except:
            self.conv_info_max_brams = []
        try:
            self.conv_info_mean_brams = [self.settings.conv_info_mean['bram_name']]
        except:
            self.conv_info_mean_brams = []

        # add stability brams
        try:
            self.stab_brams = list(chain.from_iterable(self.settings.inst_chnl_info['bram_list2d'])) # flatten list
        except:
            self.stab_brams = []
            
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
        return self.regs + self.snapshots + self.spec + self.conv_info_chnl_brams +\
            self.conv_info_max_brams + self.conv_info_mean_brams + self.stab_brams

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
        if arm:
            if snapshot == "adcsnap0":
                snap_data = self.get_generator_signal(self.settings.snap_samples, delay=0) # hardcode delay to test adc_sync
            elif snapshot == "adcsnap1":
                snap_data = self.get_generator_signal(self.settings.snap_samples, delay=30) # hardcode delay to test adc_sync
            else:
                raise Exception("Snapshot not defined in config file.")
        elif snapshot in self.snapshots:
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
            spec_len = get_n_data(nbytes, self.settings.spec_info['data_width'])
            spec = np.zeros(spec_len)
            for _ in range(acc_len):
                signal = self.get_generator_signal(2*spec_len)
                spec += np.abs(np.fft.rfft(signal)[:spec_len])
            spec = spec / acc_len
            return struct.pack('>'+str(spec_len)+self.settings.spec_info['data_type'], *spec)

        # Returns dummy convergence signal
        elif bram in self.conv_info_chnl_brams:
            return gen_exp_decay_signal(nbytes, self.settings.conv_info_chnl)
        elif bram in self.conv_info_max_brams:
            return gen_exp_decay_signal(nbytes, self.settings.conv_info_max)
        elif bram in self.conv_info_mean_brams:
            return gen_exp_decay_signal(nbytes, self.settings.conv_info_mean)

        # Returns dummy stability signal
        elif bram in self.stab_brams:
            n_data = get_n_data(nbytes, self.settings.inst_chnl_info['data_width'])
            inst_chnl_data = 10 * (np.random.random(n_data)+1)
            return struct.pack('>'+str(n_data)+self.settings.inst_chnl_info['data_type'], *inst_chnl_data)
        
        # Raise exception if the bram is not declared in the config file
        else: 
            raise Exception("BRAM " + bram + " not defined in config file.")

def gen_exp_decay_signal(nbytes, bram_info):
    """
    Generates an exponential decay signal for convergence dummy data.
    Uses unformation from bram_bram to get the signal size and data type.
    """
    n_data = get_n_data(nbytes, bram_info['data_width'])
    # conv data a + exp(b*x)
    a = 10
    b = -(100.0/n_data)*np.random.random()
    exp_signal = np.exp(a*np.exp((b*np.arange(n_data)))) + np.random.random(n_data)

    return struct.pack('>'+str(n_data)+bram_info['data_type'], *exp_signal)

def get_n_data(nbytes, data_width):
    """
    Computes the number of data values given the total number of
    bytes in the data array, and data width in bits.
    """
    return 8 * nbytes / data_width
