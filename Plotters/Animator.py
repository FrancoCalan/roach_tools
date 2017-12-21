import os, sys, importlib
from matplotlib.figure import Figure

class Animator
    """
    Generic animator class.
    """
    def __init__(self):
        self.plot_map = {1:'11', 2:'12', 3:'22', 4:'22'}
        config_file = os.path.splitext(sys.argv[1])[0]
        self.settings = importlib.import_module(config_file)
        self.fig = Figure()
        self.data_arr = []
        
    def start_animation(self):
        for i, ax in enumerate(self.ax_arr):
            ax.set_xlim(self.xlim)
            ax.set_ylim(self.ylim)
            ax.set_xlabel(self.xlabel)
            ax.set_ylabel(self.ylabel)
            ax.set_title(self.titles[i])
            ax.grid(True)
            self.data_arr(ax.plot([], [], lw=2)[0])
