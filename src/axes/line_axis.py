from calanaxis import CalanAxis, format_key

class LineAxis(CalanAxis):
    """
    Class for plotting line or lines.
    """
    def __init__(self, ax, xdata, title=""):
        CalanAxis.__init__(self, ax, title)
        self.ax.grid()
        self.xdata = xdata

    def gen_data_dict(self):
        """
        Generates dict with the data of the axis. 
        By default only the data of the x-axis is used.
        The key assigned to the data is 'xlabel'.
        :return: dictionary with axis data.
        """
        key = format_key(self.ax.get_xlabel())
        return {key : self.xdata.tolist()}
