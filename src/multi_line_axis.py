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
        self.ax.legend()

    def plot(self, ydata_arr):
        """
        Plot y data in axis.
        """
        for line, ydata in zip(self.lines, ydata_arr):
            line.set_data(self.xdata, ydata)

    def gen_ydata_dict(self):
        """
        Generate a dictionary with the plotted data in the axis. The
        key assigned to the data is 'axis label' + 'line legend'
        """
        axis_dict = {}
        for line, legend in zip(self.lines, self.legends):
            key = self.format_key(self.ax.get_title() + ' ' + legend)
            axis_dict[key] = line.get_ydata().tolist()

        return axis_dict
