from calanaxis import CalanAxis

class MultiLineAxis(CalanAxis):
    """
    Class representing an axis from a plot with multiple lines plot.
    """
    def __init__(self, ax, xdata, legends):
        CalanAxis.__init__(self, ax, xdata)
        self.lines = []
        self.legends = legends
        for legend in self.legends:
            self.lines.append(self.ax.plot([], [], lw=2, label=legend)[0])

    def plot(self, ydata_arr):
        """
        Plot y data in axis.
        """
        for line, ydata in zip(self.lines, ydata_arr):
            line.set_data(self.xdata, ydata)
