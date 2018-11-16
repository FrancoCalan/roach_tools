class TransferFunction(Experiment):
    """
    Class to perform a transfer function experiment, that is,
    compute the gain v/s frequency of a device under test.
    """
    def __init__(self, calanfpga):
        Experiment.__init__(self, calanfpga)

        self.nchannels = get_nchannels(self.settings.synth_info)
        self.freqs = np.linspace(0, self.settings.bw, self.nchannels, endpoint=False)

        self.source = self.create_instrument(self.settings.source)
        self.test_channels = range(1, self.nchannels, self.settings.chnl_step)

        self.figure = CalanFigure(n_plots=1, create_gui=False)
        self.figure.create_axis(0, SpectrumAxis, self.nchannels, self.settings.bw, "Transfer Function")

    def run_transfer_function_test(self):
        """
        Performs a transfer funcion test. Sweeps tone in the input and computes
        the power at the output.
        """
        for i, chnl in enumerate(self.test_channels):
            pass
