from line_axis import LineAxis
from calanaxis import format_key

class SingleLineAxis(LineAxis):
    """
    Class representing an axis from a plot with a single line plot.
    """
    def __init__(self, ax, xdata, title=""):
        LineAxis.__init__(self, ax, xdata, title)
        self.line = self.ax.plot([], [], lw=2)[0]

    def plot(self, *args):
        """
        Plot y data in axis.
        If want to use the default xdata of axis, args[0] = ydata
        else args[0] = xdata, args[1] = ydata.
        """
        if len(args) == 1:
            ydata = args[0]
        else:
            self.xdata = args[0]
            ydata = args[1]

        self.line.set_data(self.xdata, ydata)

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
