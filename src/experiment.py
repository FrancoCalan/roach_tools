import visa
import numpy as np
from instruments.generator import create_generator

class Experiment():
    """
    Most generic class. Repesents a generic experiment in roach with any model.
    It only initialize the most generic attributes for an experiment: configuration 
    settings, and model.
    """
    def __init__(self, calanfpga):
        self.fpga = calanfpga
        self.settings = self.fpga.settings
        self.rm = visa.ResourceManager('@py')

    def create_instrument(self, instr_info):
        """
        Create an instrument communication object using the
        experiment Visa resource manager.
        :param instr_info: dictionary with information of the 
            instrument to communcate with.
        :return: instrunet object.
        """
        return create_generator(self.rm, instr_info)

def linear_to_dBFS(data, bram_info, nbits=8):
    """
    Turn data in linear scale to dBFS scale.
    :param data: data to convert to dBFS.
    Formula used: dBFS = 6.02*Nbits + 1.76 + 10*log10(FFTSize/2)
    :param bram_info: bram info data from the spectrometer
        to get the number of channels.
    :param nbits: number of bits of the original digitized signal.
    :return: data in dBFS.
    """
    nchannels = get_nchannels(bram_info)
    dBFS = 6.02*nbits + 1.76 + 10*np.log10(nchannels)
    return 10*np.log10(data+1) - dBFS

def get_nchannels(bram_info):
    """
    Compute the number of channels of an spetrum from a bram_info dict.
    :param bram_info: dictionary with information of a group of
        brams used to save spectral data.
    :return: number of channels of the spectral data.
    """
    n_brams = len(bram_info['bram_list2d'][0])
    return n_brams * 2**bram_info['addr_width']
