from calanaxis import CalanAxis

class MatrixAxis(CalanAxis):
    """
    Class for plotting matrices (using imshow).
    """
    def __init__(self, ax, fig, title=""):
        CalanAxis.__init__(self, ax, title)
        self.fig = fig # needed to set colorbar
        self.colorbar = None

    def plot(self, plot_data, origin, aspect, interpolation, extent=None, cbar_label=''):
        """
        Plot matrix data using imshow.
        """
        cax = self.ax.imshow(plot_data, origin=origin, aspect=aspect,
            interpolation=interpolation, extent=extent)
        
        # create colorbar or update if already created
        if self.colorbar == None:
            self.colorbar = self.fig.colorbar(cax)
            self.colorbar.set_label(cbar_label)
        else:
            self.colorbar.update_bruteforce(cax)
            #self.colorbar.update_normal(cax)
