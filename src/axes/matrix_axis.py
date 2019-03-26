import numpy as np
from calanaxis import CalanAxis

class MatrixAxis(CalanAxis):
    """
    Class for plotting matrices (using imshow).
    """
    def __init__(self, ax, fig, origin, aspect, interpolation, extent=None, cbar_label="", title=""):
        CalanAxis.__init__(self, ax, title)
        self.fig = fig # needed to set colorbar

        self.img = self.ax.imshow([[0,0],[0,0]], origin=origin, aspect=aspect,
            interpolation=interpolation, extent=extent)
        self.colorbar = self.fig.colorbar(self.img)
        self.colorbar.set_label(cbar_label)
        self.contour = contour

    def plot(self, plot_data):
        """
        Plot matrix data using imshow.
        """
        self.img.set_data(plot_data)
        self.img.set_clim(vmin=np.min(plot_data), vmax=np.max(plot_data))
        self.colorbar.update_normal(self.img)
