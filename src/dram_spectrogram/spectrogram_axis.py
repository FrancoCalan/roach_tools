from ..axes.matrix_axis import MatrixAxis

class SpectrogramAxis(MatrixAxis):
    """
    Class for plotting spectrograms as matrices.
    """
    def __init__(self, ax, title=""):
        MatrixAxis.__init__(self, ax, title)
