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
    if 'bram_name' in bram_info.keys(): # case one bram spectrometer
        n_brams = 1
    elif 'bram_list' in bram_info.keys(): # case multi-bram spectrometer
        n_brams = len(bram_info['bram_list']) 
    elif 'bram_list2d' in bram_info.keys(): # case multiple spectrometer in single model
        n_brams = len(bram_info['bram_list2d'][0]) # assumes all spectrometers have the same number of brams 

    data_per_word =  bram_info['word_width']/8 / np.dtype(bram_info['data_type']).alignment
    return n_brams * 2**bram_info['addr_width'] * data_per_word

def get_freq_from_channel(bw, channel, bram_info):
    """
    Compute the center frequency of a channel, given the spectrometer
    bandwidth and the bram info data.
    :param bw: bandwith of the spectrometer.
    :param channel: the channel position used to compute the frequency
        (note that channel 0 is always 0Hz).
    :param bram_info: dictionary with the information of the group of 
        brams used to save the spectral data. Needed to compute the number
        of channels of the spectrometer.
    :return: center frequency of the spectral bin. Note that the measurement unit 
        is the same as for the bw parameter.
    """
    return bw * channel / get_nchannels(bram_info)

def get_channel_from_freq(bw, freq, bram_info):
    """
    Compute the closest channel to a fixed frequency, given the spectrometer
    bandwidth and bram_info data.
    :param bw: bandwith of the spectrometer.
    :param freq: frequency to compute the channel position.
        Must be in the same units as bw (note that channel 0 is always 0Hz).
    :param bram_info: dictionary with the information of the group of 
        brams used to save the spectral data. Needed to compute the number
        of channels of the spectrometer.
    :return: Closest channel to the frequency freq.
    """
    return int(round(freq / (bw / get_nchannels(bram_info))))

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
