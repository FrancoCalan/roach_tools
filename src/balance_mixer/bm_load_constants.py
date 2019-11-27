import numpy as np
from ..experiment import Experiment, get_nchannels
from ..digital_sideband_separation.dss_calibrator import float2fixed

class BmLoadConstants(Experiment):
    """
    Load a set of constants to the balance mixer
    model, that can be either all the same for
    all frequencies (e.g. ideal constants 1+0j),
    of calibration constats from measurements.
    """

    def __init__(self, calanfpga):
        Experiment.__init__(self, calanfpga)
        self.nchannels = get_nchannels(self.settings.synth_info)

        # const dtype info
        self.consts_nbits = np.dtype(self.settings.const_brams_info['data_type']).alignment * 8
        self.consts_bin_pt = self.settings.const_bin_pt
        
    def load_constants(self):
        """
        Load the damn constants.
        """
        # get the constants
        if hasattr(self.settings, 'ideal'):
            consts = self.settings.ideal * np.ones(self.nchannels, dtype=np.complex)

        elif hasattr(self.settings, 'file'):
            consts = -1 * np.load(self.settings.file)['ab_ratios']

        if hasattr(self.settings, 'negate'):
            consts = -1 * consts

        # load the constants
        print("Loading constants...")
        consts_real = float2fixed(self.consts_nbits, self.consts_bin_pt, np.real(consts))
        consts_imag = float2fixed(self.consts_nbits, self.consts_bin_pt, np.imag(consts))
        self.fpga.write_bram_data(self.settings.const_brams_info, [consts_real, consts_imag])
        print("done")
