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

def interleave_array_list(array_list, dtype):
    """
    Receivers a list of unknown depth with the final elements
    being numpy arrays. Interleave the arrays in the inner most
    lists. It assumes that all the sub lists are of the same depth.
    Useful to combine spectral data separated in diferent brams.
    Examples (parenthesis signifies numpy array):

    - [(1,2,3,4),(10,20,30,40)] -> (1,10,2,20,3,30,4,40)
    
    - [[(1,2,3,4),(5,6,7,8)] , [(10,20,30,40),(50,60,70,80)]]
        -> [(1,5,2,6,3,7,4,8), (10,50,20,60,30,70,40,80)]

    :param array_list: list to interleave.
    :param dtype: numpy data type of arrays.
    :return: new list with with inner most list interleaved.
    """

    if isinstance(array_list[0], np.ndarray): # case list of arrays
        return np.fromiter(chain(*zip(*array_list)), dtype=dtype)
    
    elif isinstance(array_list[0], list): # case deeper list
        interleaved_list = []
        for inner_list in array_list:
            interleaved_inner_list = interleave_array_list(inner_list, dtype)
            interleaved_list.append(interleaved_inner_list)
        return interleaved_list

def deinterleave_array_list(array_list, ifactor):
    """
    Receivers a list of unknown depth with the final elements
    being numpy arrays. For every array, separate the array in a
    list of ifactor arrays so that the original array is the interleaved 
    version of the produced arrays. This is the inverse function of
    interleave_array_list(). Useful when independent spectral data is
    saved in the same bram in an interleaved manner.
    :param array_list: array or list to deinterleave.
    :param ifactor: interleave factor, number of arrays in which to separate
        the original array.
    :return: list with the deinterleaved arrays.
    """

    if isinstance(array_list, np.ndarray): # case array
        deinterleaved_list = np.reshape(array_list, (len(array_list)/ifactor, ifactor))
        deinterleaved_list = np.transpose(deinterleaved_list)
        deinterleaved_list = list(deinterleaved_list)
        return deinterleaved_list

    if isinstance(array_list, list): # case list
        deinterleaved_list = []
        for inner_list in array_list:
            deinterleaved_inner_list = deinterleave_array_list(inner_list, ifactor)
            deinterleaved_list.append(deinterleaved_inner_list)
        return deinterleaved_list

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
    if isinstance(bram_info['bram_names'], str): # case one bram spectrometer
        n_brams = 1
    elif isinstance(bram_info['bram_names'][0], str): # case multi-bram spectrometer
        n_brams = len(bram_info['bram_names']) 
    elif isinstance(bram_info['bram_names'][0][0], str): # case multiple spectrometer in single model
        n_brams = len(bram_info['bram_names'][0]) # assumes all spectrometers have the same number of brams 

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
