import matplotlib.pyplot as plt

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
        self.ax.imshow(plot_data, origin='lower')
