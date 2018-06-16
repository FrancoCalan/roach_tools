import os, sys
import matplotlib.animation as animation
import Tkinter as Tk
import multiprocessing as mp
from plotter import Plotter

class Animator(Plotter):
    """
    Generic animator class.
    """
    def __init__(self, calanfpga):
        Plotter.__init__(self, calanfpga)

    def start_animation(self):
        """
        Add the basic parameters to the plot and starts the animation.
        """
        self.fig.set_tight_layout(True)
        self.create_window()
        anim = animation.FuncAnimation(self.fig, animate, fargs=(self,), blit=True)
        Tk.mainloop()

    def start_nonblocking_animation(self):
        """
        Like start_animation() but it does not block the flow of the program. 
        Useful for doing tests that involve taking multiple controlling 
        equipment, taking multiple snapshots, etc. It does not uses Tk, instead uses
        matplotlib default display window, hence it does not uses widgets.
        """
        anim_process = mp.Process(target=self.start_animation)
        anim_process.start()

def animate(_, self):
    """
    It's call on every frame of the animation. Updates the data.
    """
    self.plot_axes()

    return []
