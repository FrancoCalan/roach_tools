from calanaxis import CalanAxis

class MatrixAxis(CalanAxis):
    """
    Class for plotting matrices (using imshow).
    """
    def __init__(self, ax, title=""):
        self.CalanAxis.__init__(ax, title)

    def plot(self, plot_data, extent=None):
        """
        Plot matrix data using imshow.
        """
        self.ax.imshow(plot_data, origin='lower', aspect='auto',
            interpolation='gaussian', extent=extent)
