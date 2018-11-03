from animator import Animator
from calanfigure import CalanFigure
from axes.snapshot_axis import SnapshotAxis

class SnapshotAnimator(Animator):
    """
    Class responsable for drawing snapshot plots.
    """
    def __init__(self, calanfpga):
        Animator.__init__(self, calanfpga)
        self.snapshots = self.fpga.get_snapshot_names()
        self.figure = CalanFigure(experiment=self, 
            n_plots=len(self.settings.snapshots),
            create_gui=True)
        
        for i in range(self.figure.n_plots):
            self.figure.create_axis(i, SnapshotAxis, 
                self.settings.snap_samples, self.snapshots[i])
        
    def get_data(self):
        """
        Gets the snapshot data from fpga.
        """
        snapshots = self.fpga.get_snapshots()
        sliced_snapshots = [snapshot[:self.settings.snap_samples] for snapshot in snapshots]
        return sliced_snapshots
