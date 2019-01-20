import numpy as np
from ..axes.calanaxis import CalanAxis

class FullpowerAxis(CalanAxis):
    """
    Class representing an axis from a plot with a bar plot.
    """
    def __init__(self, ax, xdata, title=""):
        CalanAxis.__init__(self, ax, pow_names, title)
        xdata = range(len(pow_names))
        self.rects = self.ax.bar(xdata, len(self.xdata)*[0], align='center', width=1)

        self.ax.set_xlim((xdata[0], xdata[-1]))
        self.ax.set_ylim((0, -10*log10((2**(8-1))**2+1))) # Hardcoded 8-bit ADC
        self.ax.set_xlabel('ADC')
        self.ax.set_ylabel('Full Bandwidth Power [dBFS]')

    def plot(self, ydata):
        """
        Plot y data in axis.
        """
        for rect, ydata_point in zip(self.rects, ydata):
            rect.set_height(ydata_point)
