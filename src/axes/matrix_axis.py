class MatrixAxis():
    """
    Class for plotting matrices (using imshow).
    """
    def __init__(self, ax, title=""):
        self.ax = ax
        self.ax.set_title(title)

    def plot(self, plot_data):
        """
        Plot matrix data using imshow.
        """
        ax.imshow(plot_data)
