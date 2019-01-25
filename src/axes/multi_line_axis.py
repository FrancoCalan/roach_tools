from line_axis import LineAxis
from calanaxis import format_key

class MultiLineAxis(LineAxis):
    """
    Class representing an axis from a plot with multiple lines plot.
    """
    def __init__(self, ax, xdata, legends, title=""):
        LineAxis.__init__(self, ax, xdata, title)
        self.lines = []
        self.legends = legends
        for legend in self.legends:
            self.lines.append(self.ax.plot([], [], lw=2, label=legend)[0])
        self.ax.legend()

    def plot(self, *args):
        """
        Plot y data in axis.
        If want to use the default xdata of axis, args[0] = ydata
        else args[0] = xdata, args[1] = ydata.
        """
        if len(args) == 1:
            ydata_arr = args[0]
        else:
            self.xdata = args[0]
            ydata_arr = args[1]
        for line, ydata in zip(self.lines[:len(ydata_arr)], ydata_arr):
            line.set_data(self.xdata, ydata)

    def gen_data_dict(self):
        """
        Generate a dictionary with the data of the axis. The
        key assigned to the y-data is 'axis label' + 'line legend'
        :return: dictionary with axis data.
        """
        data_dict = LineAxis.gen_data_dict(self)

        for line, legend in zip(self.lines, self.legends):
            key = format_key(self.ax.get_ylabel() + ' ' + legend)
            data_dict[key] = line.get_ydata().tolist()

        return data_dict
