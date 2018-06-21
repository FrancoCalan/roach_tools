class CalanAxis():
    """
    Generic axis class for plotting.
    """
    def __init__(self, ax, xdata):
        self.ax = ax
        self.ax.grid()
        self.xdata = xdata
