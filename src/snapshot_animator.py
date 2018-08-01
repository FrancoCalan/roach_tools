from animator import Animator
from snapshot_axis import SnapshotAxis

class SnapshotAnimator(Animator):
    """
    Class responsable for drawing snapshot plots.
    """
    def __init__(self, calanfpga):
        Animator.__init__(self, calanfpga)
        self.snapshots = self.fpga.get_snapshot_names()
        self.nplots = len(self.settings.snapshots)
        mpl_axes = self.create_axes()
        
        for i, ax in enumerate(mpl_axes):
            self.axes.append(SnapshotAxis(ax, self.settings.snap_samples, 
                self.snapshots[i]))
        
    def get_data(self):
        """
        Gets the snapshot data form fpga.
        """
        snapshots = self.fpga.get_snapshots()
        sliced_snapshots = [snapshot[:self.settings.snap_samples] for snapshot in snapshots]
        return sliced_snapshots
