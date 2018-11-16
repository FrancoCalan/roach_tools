from plotter import Plotter
from calanfigure import CalanFigure
from axes.snapshot_axis import SnapshotAxis

class SnapshotAnimator(Plotter):
    """
    Class responsable for drawing snapshot plots.
    """
    def __init__(self, calanfpga):
        Plotter.__init__(self, calanfpga)
        self.snapshots = self.fpga.get_snapshot_names()
        self.figure = CalanFigure(n_plots=len(self.settings.snapshots), create_gui=True)
        
        for i in range(self.figure.n_plots):
            self.figure.create_axis(i, SnapshotAxis, 
                self.settings.snap_samples, self.snapshots[i])
        
    def get_data(self):
        """
        Gets the snapshot data from fpga.
        :return: snapshot data.
        """
        return get_snapshot_data(self.fpga, self.settings.snap_samples)

def get_snapshot_data(fpga, snap_samples):
    """
    Gets snapshot data given a CalanFpga object and snapshot samples.
    :param fpga: CalanFpga object.
    :param snap_samples: number of samples to return. 
    :return: snapshot data.
    """
    snapshots = fpga.get_snapshots()
    sliced_snapshots = [snapshot[:snap_samples] for snapshot in snapshots]
    return sliced_snapshots

