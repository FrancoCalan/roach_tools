from calanaxis import CalanAxis

class BarAxis(CalanAxis):
    """
    Class representing an axis from a plot with a bar plot.
    """
    def __init__(self, ax, xdata):
        CalanAxis.__init__(self, ax, xdata)
        self.rects = self.ax.bar(xdata, len(self.xdata)*[0], align='center', width=1)

    def plot(self, ydata):
        """
        Plot y data in axis.
        """
        for rect, ydata_point in zip(self.rects, ydata):
            rect.set_height(ydata_point)
