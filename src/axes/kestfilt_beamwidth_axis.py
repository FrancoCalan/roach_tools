from multi_line_axis import MultiLineAxis

class KestfiltBeamwidthAxis(MultiLineAxis):
    """
    Class representing an axis from a beamwidth experiment using
    the kestfilt model. Compares the measurement of a beamwidth 
    with and without the filter.
    """
    def __init__(self, ax, offset_arr, title=""):
        legends = ['Primary signal', 'Filter output']
        MultiLineAxis.__init__(self, ax, offset_arr, legends, title)

        self.ax.set_xlabel('Offset [deg]')
        self.ax.set_ylabel('Power [dBFS]')
