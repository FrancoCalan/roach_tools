from line_axis import LineAxis
from calanaxis import format_key

class SingleLineAxis(LineAxis):
    """
    Class representing an axis from a plot with a single line plot.
    """
    def __init__(self, ax, xdata, title=""):
        LineAxis.__init__(self, ax, xdata, title)
        self.line = self.ax.plot([], [], lw=2)[0]

    def ploty(self, ydata):
        """
        Plot y-data in axis using the default x-data.
        :param ydata: array with data to plot.
        """
        self.plotxy(self.xdata, ydata)

    def plotxy(self, xdata, ydata):
        """
        plot y-data using the given x-data array.
        :param xdata: data for the x-axis.
        :param ydata: array with the data to plot.
        """
        self.line.set_data(xdata, ydata)

    def gen_data_dict(self):
        """
        Generates a dictionary with the data of the axis. The 
        key assigned for the y-data is 'axis title' + 'ylabel'.
        :return: dictionary with axis data.
        """
        data_dict = LineAxis.gen_data_dict(self)

        key = format_key(self.ax.get_title() + ' ' + self.ax.get_ylabel())
        data_dict[key] = self.line.get_ydata().tolist()
        
        return data_dict
