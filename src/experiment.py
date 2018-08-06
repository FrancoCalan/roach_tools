import numpy as np

class Experiment():
    """
    Most generic class. Repesents a generic experiment in roach with any model.
    It only initialize the most generic attributes for an experiment: configuration 
    settings, and model.
    """
    def __init__(self, calanfpga):
        self.fpga = calanfpga
        self.settings = self.fpga.settings

    def linear_to_dBFS(self, data):
        """
        Turn data in linear scale to dBFS scale. It uses the dBFS_const value
        from the configuration file to adjust the zero in the dBFS scale.
        """
        return 10*np.log10(data+1) - self.settings.dBFS_const

    def get_nchannels(self, bram_info):
        """
        Compute the number of channels of an spetrum from a bram_info dict
        """
        n_brams = len(bram_info['bram_list2d'][0])
        return n_brams * 2**bram_info['addr_width']

