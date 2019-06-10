import numpy as np
import matplotlib.pyplot as plt
from .. axes.calanaxis import CalanAxis

class CalPhasorAxis(CalanAxis):
    """
    Class for plotting calibration phasors near
    the unit circle.
    """
    def __init__(self, ax, legends, title=""):
        CalanAxis.__init__(self, ax, title)
        
        # axis propeties
        self.ax.set_xlim([-1.5,1.5])
        self.ax.set_ylim([-1.5,1.5])
        self.ax.grid()
        self.ax.set_axisbelow(True)
        self.ax.set_aspect('equal')
        
        # draw unit circle
        self.ax.add_artist(plt.Circle((0,0), 1, color='g', fill=False))

        # draw x at (1,0)
        self.ax.scatter([1], [0], color='k', marker='x', s=50)

        # get arrow colors
        self.colors = plt.rcParams['axes.prop_cycle'].by_key()['color'][:len(legends)]
        
        # make legend
        rects = [plt.Rectangle((0,0),1,1,color=color,ec="k") for color in self.colors]
        plt.legend(rects, legends)

    def plot(self, phasors):
        """
        Plot phasors and label phasors. The label correspond to the index
        of the phasor list. Phasor from diferent color (named in the legend)
        must be put in different sublists, 
        e.g. [[uncalibrated phasors], [calibrated phasors]].
        :param phasors:
        """
        for color, phasor_list in zip(self.colors, phasors):
            for i, phasor in enumerate(phasor_list):
                phr = np.real(phasor)
                phi = np.imag(phasor)
                arrow = plt.Arrow(0, 0, phr, phi, width=0.05, color=color)
                text = plt.Text(phr, phi, 'a'+str(i), color=color)
                self.ax.add_artist(arrow)
                self.ax.add_artist(text)
