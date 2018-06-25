from animator import Animator
from single_line_axis import SingleLineAxis

class SnapshotAnimator(Animator):
    """
    Class responsable for drawing snapshot plots.
    """
    def __init__(self, calanfpga):
        Animator.__init__(self, calanfpga)
        self.snapshots = self.fpga.get_snapshot_names()
        self.nplots = len(self.settings.snapshots)
        mpl_axes = self.create_axes()
        
        self.set_axes_parameters(mpl_axes)

    def set_axes_parameters(self, mpl_axes):
        """
        Set axes paramters for snapshot plots.
        """
        xdata = range(self.settings.snap_samples)
        for i, ax in enumerate(mpl_axes):
            ax.set_title(self.snapshots[i])
            ax.set_xlim(0, self.settings.snap_samples)
            ax.set_ylim((-140, 140)) # Hardcoded 8-bit ADC
            ax.set_xlabel('Sample')
            ax.set_ylabel('Amplitude [a.u.]')
            self.axes.append(SingleLineAxis(ax, xdata))
        
    def get_data(self):
        """
        Gets the snapshot data form fpga.
        """
        snapshots = self.fpga.get_snapshots()
        sliced_snapshots = [snapshot[:self.settings.snap_samples] for snapshot in snapshots]
        return sliced_snapshots
