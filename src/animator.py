import matplotlib.animation as animation
import Tkinter as Tk
from experiment import Experiment

class Animator(Experiment):
    """
    Generic animator class.
    """
    def __init__(self, calanfpga):
        Experiment.__init__(self, calanfpga)

    def start_animation(self):
        """
        Add the basic parameters to the plot and starts the animation.
        """
        self.figure.create_window()
        anim = animation.FuncAnimation(self.figure.fig, animate, fargs=(self,), blit=True)
        Tk.mainloop()

def animate(_, self):
    """
    It's call on every frame of the animation. Updates the data.
    """
    animation_data = self.get_data()
    self.figure.plot_axes(animation_data)

    return []
