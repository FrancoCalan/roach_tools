import numpy as np
from ..animator import Animator
from ..calanfigure import CalanFigure
from ..axes.spectrum_axis import SpectrumAxis
from ..pocket_correlator.mag_ratio_axis import MagRatioAxis
from ..pocket_correlator.angle_diff_axis import AngleDiffAxis
from ..experiment import get_nchannels

class BmNoiseCorrelator(Animator):
    def __init__(self, calanfpga):
        Animator.__init__(self, calanfpga)
        self.bw = self.settings.bw
        self.nchannels = get_nchannels(self.settings.spec_info)
        self.freqs = np.linspace(0, self.bw, self.nchannels, endpoint=False)
        
        self.figure = CalanFigure(n_plots=4, create_gui=True)
        self.figure.create_axis(0, SpectrumAxis, self.freqs, 'ZDOK0')
        self.figure.create_axis(1, SpectrumAxis, self.freqs, 'ZDOK1')
        self.figure.create_axis(2, MagRatioAxis, self.freqs, ['ZDOK0/ZDOK1'], 'Mag Ratio')
        self.figure.create_axis(3, AngleDiffAxis, self.freqs, ['ZDOK0/ZDOK1'], 'Angle Diff')
        
    def get_data(self):
        # get spec data
        spec_data = self.fpga.get_bram_data(self.settings.spec_info)
        spec_data_plot = self.scale_dbfs_spec_data(spec_data, self.settings.spec_info)

        # get crosspow data
        cross_re, cross_im = self.fpga.get_bram_data(self.settings.crosspow_info)
        crosspow = cross_re + 1j*cross_im
        div_ab = crosspow / spec_data[1] # ab* / bb* = a/b

        # group data
        data = [spec_data_plot[0]] + [spec_data_plot[1]] +\
            [[np.abs(div_ab)]] + [[np.angle(div_ab, deg=True)]]            

        return data
