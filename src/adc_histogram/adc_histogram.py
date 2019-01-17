import numpy as np
from ..animator import Animator
from ..snapshot_animator import get_snapshot_data
from ..calanfigure import CalanFigure
from ..axes.snapshot_axis import SnapshotAxis
from histogram_axis import HistogramAxis

class AdcHistogram(Animator):
    """
    Class responsible of making histogram from ADC snapshot data.
    Useful to find 'missing codes' and debug the ADC.
    """
    def __init__(self, calanfpga):
        Animator.__init__(self, calanfpga)
        self.figure = CalanFigure(n_plots=2*len(self.settings.snapshots), create_gui=True)
        
        for i in range(self.figure.n_plots/2):
            self.figure.create_axis(i, SnapshotAxis, 
                self.settings.snap_samples, self.settings.snapshots[i])

        for i in range(self.figure.n_plots/2, self.figure.n_plots):
            self.figure.create_axis(i, HistogramAxis,
                range(-2**7, 2**7), self.settings.snapshots[(i-1)/2]) # Hardcoded 8-bit ADC

        self.n_hists = self.figure.n_plots / 2
        self.abs_hists = self.n_hists * [np.zeros(2**8)] # Hardcoded 8-bit ADC

    def get_data(self):
        """
        Get snapshot data and generate histogram data to plot.
        """
        snapshots = get_snapshot_data(self.fpga, self.settings.snap_samples)
        norm_hists = []
        for i, snapshot in enumerate(snapshots):
            new_hist, _ = np.histogram(snapshot, bins=range(-2**7, 2**7+1)) # Hardcoded 8-bit ADC
            self.abs_hists[i] += new_hist
            norm_hists.append(self.abs_hists[i] / np.sum(self.abs_hists[i]))

        return snapshots + norm_hists
