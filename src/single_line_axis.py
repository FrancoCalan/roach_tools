from calanaxis import CalanAxis

class SingleLineAxis(CalanAxis):
    """
    Class representing an axis from a plot with a single line plot.
    """
    def __init__(self, ax, xdata, title=""):
        CalanAxis.__init__(self, ax, xdata, title)
        self.line = self.ax.plot([], [], lw=2)[0]

    def plot(self, ydata, xdata=None):
        """
        Plot y data in axis.
        """
        if xdata is None:
            self.line.set_data(self.xdata, ydata)
        else:
            self.line.set_data(xdata, ydata)

    def gen_ydata_dict(self):
        """
        Generates a dictionary with the plotted data in the axis. The 
        key assigned to the data is 'axis title' + 'ylabel'.
        """
        key = self.format_key(self.ax.get_title() + ' ' + self.ax.get_ylabel())
        return {key : self.line.get_ydata().tolist()}
