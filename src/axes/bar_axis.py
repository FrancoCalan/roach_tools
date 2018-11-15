from calanaxis import CalanAxis

class BarAxis(CalanAxis):
    """
    Class representing an axis from a plot with a bar plot.
    """
    def __init__(self, ax, xdata, title=""):
        CalanAxis.__init__(self, ax, xdata, title)
        self.rects = self.ax.bar(xdata, len(self.xdata)*[0], align='center', width=1)

        self.ax.set_xlim((xdata[0], xdata[-1]))
        self.ax.set_ylim((0, 0.035)) # Hardcoded 8-bit ADC
        self.ax.set_xlabel('Code')
        self.ax.set_ylabel('Normalized Frequency')

    def plot(self, ydata):
        """
        Plot y data in axis.
        """
        for rect, ydata_point in zip(self.rects, ydata):
            rect.set_height(ydata_point)
