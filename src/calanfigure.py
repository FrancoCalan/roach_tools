import os, sys, importlib, json
import numpy as np
import matplotlib.pyplot as plt
import Tkinter as Tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

class CalanFigure():
    """
    Class representing a figure for a generic experiment with roach.
    """
    def __init__(self, n_plots, create_gui):
        self.n_plots = n_plots
        self.plot_map = {1: [1,1], 2: [1,2], 3: [2,2], 4: [2,2], 16: [4,4]}
        self.axes = []
        # Figure() needed in order for Tkinter GUI elements to work properly
        if create_gui:
            self.fig = plt.Figure()
        # figure() needed to use pyplot default backend and for fine-tunning plots updates
        else:
            self.fig = plt.figure()
        self.fig.set_tight_layout(True)

    def create_axis(self, n_axis, calanaxis_class, *axis_args):
        """
        Create a calanaxis by adding a subplot to the figure and appending the 
        calanaxis to the axis array.
        :param n_axis: axis number in the plot map.
        :param calanaxis_class: calanaxis class to be created (spectrum_axis, 
            snapshot_axis, etc.)
        :param axis_args: arguments for the calanaxis instansiation.
        """
        nrows, ncols = self.plot_map[self.n_plots]
        matplotlib_axis = self.fig.add_subplot(nrows, ncols, n_axis+1)
        calanaxis = calanaxis_class(matplotlib_axis, *axis_args)
        self.axes.append(calanaxis)

    def create_window(self):
        """
        Create a Tkinter window with all of the components (plots, toolbar, widgets).
        """
        # tkinter window
        self.root = Tk.Tk()

        # plot canvas
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)

        # navigation bar
        toolbar = NavigationToolbar2Tk(self.canvas, self.root)
        toolbar.update()
        self.canvas._tkcanvas.pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)        

    def plot_axes(self, data_arr):
        """
        Plot the data in every axes of the figure.
        :param data_arr: Array containing the data elements for
            every axes. the exact structure of the data elements
            depends on the type of axis.
        """
        for axis, data in zip(self.axes, data_arr):
            axis.plot(data)

    def get_save_data(self):
        """
        Get a dictionary of the data in the figure axes. Used to
        save the plotted data in text format (e.g. JSON).
        NOTE: depending on the axes implementation of gen_data_dict(),
        different axes can produce dictionaries with the same key, 
        in this case the data gets overwritten. This could be good to
        avoid data duplication for figures with the same data (for example,
        parallel spectrometers with the same frequency axis), but 
        but the developer should be careful in the implementation
        of the specific gen_data_dict() to avoid data loss.
        :return: dictionary with the data from every axes.
        """
        data_dict = {}
        for axis in self.axes:
            axis_data_dict = axis.gen_data_dict()
            data_dict.update(axis_data_dict)

        return data_dict
