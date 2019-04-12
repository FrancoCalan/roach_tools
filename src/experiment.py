import numpy as np
from itertools import chain

class Experiment():
    """
    Most generic class. Repesents a generic experiment in roach with any model.
    It only initialize the most generic attributes for an experiment: configuration 
    settings, and model.
    """
    def __init__(self, calanfpga):
        self.fpga = calanfpga
        self.settings = self.fpga.settings

    def scale_dbfs_spec_data(self, spec_data, spec_info):
        """
        Scales spectral data by the accumulation length given by the
        accumulation reg in the spec_info dictionary, and converts
        the data to dBFS. Used for plotting spectra.
        :param spec_data: spectral data in linear scale, as read with CalanFpga's
            get_bram_data(). Can be a numpy array or a list (with possible more 
            inner lists) of numpy arrays.
        :param spec_info: dictionary with info of the memory with 
            the spectral data in the FPGA.
        :return: spectral data in dBFS.
        """
        if isinstance(spec_data, np.ndarray): 
            spec_data = spec_data / float(self.fpga.read_reg(spec_info['acc_len_reg'])) # divide by accumulation
            spec_data = linear_to_dBFS(spec_data, spec_info)
            return spec_data
            
        else: # spec_data is list
            spec_data = [self.scale_dbfs_spec_data(spec_data_item, spec_info) for spec_data_item in spec_data]
            return spec_data

def linear_to_dBFS(data, bram_info, nbits=8):
    """
    Turn data in linear scale to dBFS scale.
    Formula used: dBFS = 6.02*Nbits + 1.76 + 10*log10(FFTSize/2)
    :param data: data to convert to dBFS.
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
    data_per_word =  bram_info['word_width']/8 / np.dtype(bram_info['data_type']).alignment
    n_channels = 2**bram_info['addr_width'] * data_per_word
    
    # correct for interleaved data
    if 'deinterleave_by' in bram_info:
        n_channels = n_channels / bram_info['deinterleave_by']

    # correct for deinterleaved data
    if 'interleave' in bram_info and bram_info['interleave']==True:
        # hacky function to get the number of deinterleaved brams
        def get_nbrams(bram_names):
            if isinstance(bram_names[0], str):
                return len(bram_names)
            else: # bram_names = list
                return get_nbrams(bram_names[0])

        n_deinterleaved_brams = get_nbrams(bram_info['bram_names'])
        n_channels = n_channels * n_deinterleaved_brams

    return n_channels

def get_freq_from_channel(init_freq, bw, channel, bram_info):
    """
    Compute the center frequency of a channel, given the spectrometer
    bandwidth and the bram info data.
    :param init_freq: initial frequency of the frequency band.
    :param bw: bandwith of the spectrometer.
    :param channel: the channel position used to compute the frequency
        (note that channel 0 is always 0Hz).
    :param bram_info: dictionary with the information of the group of 
        brams used to save the spectral data. Needed to compute the number
        of channels of the spectrometer.
    :return: center frequency of the spectral bin. Note that the measurement unit 
        is the same as for the bw parameter.
    """
    return init_freq + (bw * channel / get_nchannels(bram_info))

def get_channel_from_freq(init_freq, bw, freq, bram_info):
    """
    Compute the closest channel to a fixed frequency, given the spectrometer
    bandwidth and bram_info data.
    :param init_freq: initial frequency of the frequency band.
    :param bw: bandwith of the spectrometer.
    :param freq: frequency to compute the channel position.
        Must be in the same units as bw (note that channel 0 is always 0Hz).
    :param bram_info: dictionary with the information of the group of 
        brams used to save the spectral data. Needed to compute the number
        of channels of the spectrometer.
    :return: Closest channel to the frequency freq.
    """
    return int(round((freq - init_freq) / (bw / get_nchannels(bram_info))))

def get_spec_time_arr(bw, n_specs, bram_info):
    """
    Compute a time array with timestamps for a number of consecutive spectra
    from an spectrometer model, where the first spectrum occurs at time 0.
    :param bw: bandwith of the spectrometer.
    :param n_specs: number of spectrum to consider for the time array.
    :param bram_info: dictionary with the information of the group of 
        brams used to save the spectral data. Needed to compute the number
        of channels of the spectrometer.
    :return: time array of length n_specs with the timestamp of the spectra.
        Note that if bw is in [MHz] the time array will be in [us].
    """
    n_channels = get_nchannels(bram_info)
    return np.arange(0, n_specs) * (1.0/bw) * n_channels
