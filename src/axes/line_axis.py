from calanaxis import CalanAxis, format_key

class LineAxis(CalanAxis):
    """
    Class for plotting line or lines.
    """
    def __init__(self, ax, xdata, title=""):
        CalanAxis.__init__(self, ax, title)
        self.ax.grid()
        self.xdata = xdata

    def gen_xdata_dict(self):
        """
        Generates dict with xdata of the axis. The key assigned to the
        data is 'xlabel'.
        """
        key = format_key(self.ax.get_xlabel())
        return {key : self.xdata.tolist()}
