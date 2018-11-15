from spectra_animator import SpectraAnimator

class VMFreqAnimator(SpectraAnimator):
    """
    Class responsible to act as a vector multimeter, that is,
    compute de power ratio and angle difference between two sinewave
    input signal. In is done by transforming the signals to the frequency
    domain and then computing the complex division of the higher power
    channel of the spectra.
    """
    def __init__(self, calanfpga):
        SpectraAnimator.__init__(self, calanfpga)
        self.figure = CalanFigure(n_plots=4, create_gui=True)

        self.figure.create_axis(0, SpectrumAxis, 
            self.nchannels, self.settings.bw, self.settings.plot_titles[0])
        self.figure.create_axis(1, SpectrumAxis, 
            self.nchannels, self.settings.bw, self.settings.plot_titles[1])
        self.figure.create_axis(2, MagRatioAxis, 
            self.nchannels, self.settings.bw, 'Magnitude Ratio')
        self.figure.create_axis(3, AngleDiffAxis, 
            self.nchannels, self.settings.bw, 'Angle Difference')

            
