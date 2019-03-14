from calanaxis import CalanAxis

class MatrixAxis(CalanAxis):
    """
    Class for plotting matrices (using imshow).
    """
    def __init__(self, ax, fig, title=""):
        CalanAxis.__init__(self, ax, title)
        self.fig = fig # needed to set colorbar

    def plot(self, plot_data, origin, aspect, interpolation, extent=None, cbar_label=''):
        """
        Plot matrix data using imshow.
        """
        cax = self.ax.imshow(plot_data, origin=origin, aspect=aspect,
            interpolation=inpterpolation, extent=extent)
        cbar = self.fig.colorbar(cax)
        cbar.set_label(cbar_label)

