import os, sys, importlib, json
import numpy as np
import matplotlib.pyplot as plt
import Tkinter as Tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

class CalanFigure():
    """
    Class representing a figure for a generic experiment with roach.
    """
    def __init__(self, n_plots, create_gui, figure_name='Figure'):
        self.figure_name = figure_name
        self.n_plots = n_plots
        # Workaround to Tk.mainloop not closing properly for plt.figure()
        self.create_gui = create_gui
        if self.create_gui:
            self.fig = plt.Figure()
        else:
            self.fig = plt.figure()
        self.plot_map = {1:'11', 2:'12', 3:'22', 4:'22'}
        self.axes = []

    def create_axis(self, n_axis, calanaxis_class, *axis_args):
        """
        Create a calanaxis by adding a subplot to the figure and appending the 
        calanaxis to the axis array.
        :param n_axis: axis number in the plot map.
        :param calanaxis_class: calanaxis class to be created (spectrum_axis, 
            snapshot_axis, etc.)
        :param axis_args: arguments for the calanaxis instansiation.
        """
        matplotlib_axis = self.fig.add_subplot(self.plot_map[self.n_plots]+str(n_axis+1))
        calanaxis = calanaxis_class(matplotlib_axis, *axis_args)
        self.axes.append(calanaxis)

    def create_window(self):
        """
        Create a Tkinter window with all of the components (plots, toolbar, widgets).
        """
        self.fig.set_tight_layout(True)

        if self.create_gui:
            # tkinter window
            self.root = Tk.Tk()

            # plot canvas
            self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
            self.canvas.get_tk_widget().pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)

            # navigation bar
            toolbar = NavigationToolbar2Tk(self.canvas, self.root)
            toolbar.update()
            self.canvas._tkcanvas.pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)        

        else:
            self.fig.show()

    def plot_axes(self, data_arr):
        """
        Plot the data in every axes of the figure.
        :param data_arr: Array containing the data elements for
            every axes. the exact structure of the data elements
            depends on the type of axis.
        """
        for axis, data in zip(self.axes, data_arr):
            axis.plot(data)

    def get_ydata(self):
        """
        Get the y-data from axes.
        :return: dictionary with the y-data from every axes.
        """
        data_dict = {}
        for axis in self.axes:
            axis_data_dict = axis.gen_ydata_dict()
            data_dict.update(axis_data_dict)

        return data_dict
