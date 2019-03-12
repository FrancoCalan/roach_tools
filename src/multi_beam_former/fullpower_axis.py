import numpy as np
from ..axes.bar_axis import BarAxis

class FullpowerAxis(BarAxis):
    """
    Class representing an axis from a plot of the full power
    read by multiple ADCs.
    """
    def __init__(self, ax, pow_names, title=""):
        BarAxis.__init__(self, ax, pow_names, title)
        xdata = range(len(pow_names))

        self.ax.grid()
        self.ax.set_xlim((xdata[0], xdata[-1]))
        self.ax.set_ylim((5, -80)) # Hardcoded 8-bit ADC
        self.ax.set_ylabel('Full Bandwidth Power [dBFS]')
        
        # rotate ticks labels for readability
        for tick in self.ax.get_xticklabels():
            tick.set_rotation(90)
