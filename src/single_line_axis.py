from calanaxis import CalanAxis

class SingleLineAxis(CalanAxis):
    """
    Class representing an axis from a plot with a single line plot.
    """
    def __init__(self, ax, xdata):
        CalanAxis.__init__(self, ax, xdata)
        self.line = self.ax.plot([], [], lw=2)[0]

    def plot(self, ydata):
        """
        Plot y data in axis.
        """
        self.line.set_data(self.xdata, ydata)
