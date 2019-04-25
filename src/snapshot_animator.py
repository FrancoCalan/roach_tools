from animator import Animator
from calanfigure import CalanFigure
from axes.snapshot_axis import SnapshotAxis

class SnapshotAnimator(Animator):
    """
    Class responsable for drawing snapshot plots.
    """
    def __init__(self, calanfpga):
        Animator.__init__(self, calanfpga)
        self.snapshots = self.settings.snapshots

        self.n_inputs = len(self.snapshots)
        self.figure = CalanFigure(n_plots=self.n_inputs, create_gui=True)
        for i, snapshot in enumerate(self.snapshots):
            self.figure.create_axis(i, SnapshotAxis, 
                self.settings.snap_samples, snapshot)
        
    def get_data(self):
        """
        Gets the snapshot data from fpga.
        :return: snapshot data.
        """
        return self.fpga.get_snapshots(self.settings.snap_samples)
