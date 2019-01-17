class DramSpectrogramPlotter(Plotter):
    """
    Class to plot an spectrogram (consecutive spectra) saved
    in ROACH's DRAM.
    """
    def __init__(self, calanfpga):
        Plotter.__init__(self, calanfpga)
        self.figure = CalanFigure(n_plots=1, create_gui=False)
        self.figure.create_axis(0, SpectrogramAxis, self.nchannels, self.bw, 'DRAM Spectrogram')

        def get_data(self):
            """
            Get spectrogam data from ROACH's dram.
            :return: spectrogram data
            """
            
