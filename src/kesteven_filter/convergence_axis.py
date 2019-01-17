from ..axes.multi_line_axis import MultiLineAxis

class ConvergenceAxis(MultiLineAxis):
    """
    Class representing an axis from a convergence plot 
    in the kestfilt experiment.
    """
    def __init__(self, ax, xdata, title=""):
        legends = ['chnl', 'max', 'mean']
        MultiLineAxis.__init__(self, ax, xdata, legends, title)

        self.ax.set_xlim(0, self.xdata[-1])
        self.ax.set_ylim((-100, 10))
        self.ax.set_xlabel('Time [$\mu$s]')
        self.ax.set_ylabel('Power [dBFS]')
