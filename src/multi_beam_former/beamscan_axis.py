from ..axes.matrix_axis import MatrixAxis

class BeamscanAxis(MatrixAxis):
    """
    Class for plotting beamscan as a matrix.
    """
    def __init__(self, ax, az_lims, el_lims, fig, title=""):
        MatrixAxis.__init__(self, ax, fig, title)
        self.az_lims = az_lims
        self.el_lims = el_lims

        self.ax.set_xlabel('Azimuth [°]')
        self.ax.set_ylabel('Elevation [°]')

    def plot(self, beamscan_data):
        """
        Plot beamscan using imshow.
        """
        MatrixAxis.plot(self, beamscan_data, origin='upper', 
            aspect='equal', inpterpolation='none',
            extent=[self.az_lims[0]-0.5, self.az_lims[1]+0.5
                    self.el_lims[0]-0.5, self.az_lims[1]+0.5], # the -+0.5 is to correct for ticks borders 
            cbar_label='Power [dB]')
