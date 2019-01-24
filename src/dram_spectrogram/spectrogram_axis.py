from ..axes.matrix_axis import MatrixAxis

class SpectrogramAxis(MatrixAxis):
    """
    Class for plotting spectrograms as matrices.
    """
    def __init__(self, ax, n_channels, bw, title=""):
        MatrixAxis.__init__(self, ax, title)
        self.n_channels = n_channels
        self.bw = bw
        self.spec_time = 1/(2*self.bw) * self.n_channels / 1000 # ms

        self.ax.set_xlabel('Time [ms]')
        self.ax.set_ylabel('Frequency [MHz]')

    def plot(self, specgram_data):
        """
        Plot spectrogram using imshow. Uses
        """
        MatrixAxis.plot(specgram_data, 
            extent=[0, self.spec_time*specgram_data.shape[1], 0, self.bw])
