import os, sys
import matplotlib.animation as animation
import Tkinter as Tk
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

def animate(_, self):
    """
    It's call on every frame of the animation. Updates the data.
    """
    self.plot_axes()

    return []
