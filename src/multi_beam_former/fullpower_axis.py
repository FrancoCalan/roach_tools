import numpy as np
from ..axes.baraxis import BarAxis

class FullpowerAxis(BarAxis):
    """
    Class representing an axis from a plot of the full power
    read by multiple ADCs.
    """
    def __init__(self, ax, pow_names, title=""):
        xdata = range(len(pow_names))
        BarAxis.__init__(self, ax, pow_names, title)

        self.ax.set_xlim((xdata[0], xdata[-1]))
        self.ax.set_ylim((0, -10*log10((2**(8-1))**2+1))) # Hardcoded 8-bit ADC
        self.ax.set_xlabel('ADC')
        self.ax.set_ylabel('Full Bandwidth Power [dBFS]')
