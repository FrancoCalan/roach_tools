from calanaxis import CalanAxis

class MatrixAxis(CalanAxis):
    """
    Class for plotting matrices (using imshow).
    """
    def __init__(self, ax, fig, title=""):
        CalanAxis.__init__(self, ax, title)
        self.fig = fig # needed to set colorbar

    def plot(self, plot_data, extent=None, cbar_label=''):
        """
        Plot matrix data using imshow.
        """
        cax = self.ax.imshow(plot_data, origin='lower', aspect='auto',
            interpolation='gaussian', extent=extent)
        cbar = self.fig.colorbar(cax)
        cbar.set_label(cbar_label)

