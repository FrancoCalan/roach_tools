from ..axes.matrix_axis import MatrixAxis

class BeamscanAxis(MatrixAxis):
    """
    Class for plotting beamscan as a matrix.
    """
    def __init__(self, ax, az_lims, el_lims, az_step, el_step, fig, title=""):
        MatrixAxis.__init__(self, ax, fig, title)
        self.az_lims = az_lims
        self.el_lims = el_lims
        self.az_step = az_step
        self.el_step = el_step

        self.ax.set_xlabel('Azimuth [deg]')
        self.ax.set_ylabel('Elevation [deg]')

    def plot(self, beamscan_data):
        """
        Plot beamscan using imshow.
        """
        MatrixAxis.plot(self, beamscan_data, origin='upper', 
            aspect='equal', interpolation='none',
            extent=[self.az_lims[0]-self.az_step/2.0, self.az_lims[1]+self.az_step/2.0,
                    self.el_lims[0]-self.el_step/2.0, self.az_lims[1]+self.el_step/2.0], # the +-az/el_step is to correct for ticks borders 
            cbar_label='Power [dB]')
