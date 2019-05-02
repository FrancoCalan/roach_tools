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

    def ploty(self, ydata_list):
        """
        Plot y-data in axis using the default x-data.
        :param ydata_list: list of arrays with data to plot.
        """
        self.plotxy(self.xdata, ydata_list)

    def plotxy(self, xdata, ydata_list):
        """
        plot y-data using the given x-data array.
        :param xdata: data for the x-axis.
        :param ydata_list: list of arrays with the data to plot.
        """
        for line, ydata in zip(self.lines[:len(ydata_list)], ydata_list):
            line.set_data(xdata, ydata)

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
