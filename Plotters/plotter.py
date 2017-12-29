###############################################################################
#                                                                             #
#   Millimeter-wave Laboratory, Department of Astronomy, University of Chile  #
#   http://www.das.uchile.cl/lab_mwl                                          #
#   Copyright (C) 2017 Franco Curotto                                         #
#                                                                             #
#   This program is free software; you can redistribute it and/or modify      #
#   it under the terms of the GNU General Public License as published by      #
#   the Free Software Foundation; either version 3 of the License, or         #
#   (at your option) any later version.                                       #
#                                                                             #
#   This program is distributed in the hope that it will be useful,           #
#   but WITHOUT ANY WARRANTY; without even the implied warranty of            #
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the             #
#   GNU General Public License for more details.                              #
#                                                                             #
#   You should have received a copy of the GNU General Public License along   #
#   with this program; if not, write to the Free Software Foundation, Inc.,   #
#   51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.               #
#                                                                             #
###############################################################################

import os, sys, importlib, pickle
import numpy as np
import matplotlib.pyplot as plt
import Tkinter as Tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg


class Plotter():
    """
    Generic plotter class.
    """
    def __init__(self):
        self.root = Tk.Tk()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.plot_map = {1:'11', 2:'12', 3:'22', 4:'22'}
        self.config_file = os.path.splitext(sys.argv[1])[0]
        self.settings = importlib.import_module(self.config_file)
        self.line_arr = []
        self.model = self.get_model(self.settings)
        self.fig = plt.Figure()

    def add_plot_parameters(self):
        """
        Add the basic parameters to the plot.
        """
        for i, title in enumerate(self.titles):
            ax = self.fig.add_subplot(self.plot_map[len(self.titles)]+str(i+1))
            ax.set_xlim(self.xlim)
            ax.set_ylim(self.ylim)
            ax.set_xlabel(self.xlabel)
            ax.set_ylabel(self.ylabel)
            ax.set_title(title)
            ax.grid(True)
            self.line_arr.append(ax.plot([], [], lw=2, animated=True)[0])

        self.fig.set_tight_layout(True)
        self.create_window()
    
    def draw_plot_lines(self):
        """
        Draw plot lines in canvas.
        """
        data_arr = self.get_data()
        for i, ydata in enumerate(data_arr):
            self.line_arr[i].set_data(self.xdata, ydata)
 
    def plot(self):
        """
        Show plot window.
        """
        self.add_plot_parameters()
        self.draw_plot_lines() 
        Tk.mainloop()

    def create_window(self):
        """
        Create a Tkinter window with all of the components (plots, toolbar, widgets).
        """
        # plots
        canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        canvas.show()
        canvas.get_tk_widget().pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)

        # navigation bar
        toolbar = NavigationToolbar2TkAgg(canvas, self.root)
        toolbar.update()
        canvas._tkcanvas.pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)        
        
        # button frame
        self.button_frame = Tk.Frame(master=self.root)
        self.button_frame.pack(side=Tk.TOP, anchor="w")

        # save button
        self.save_button = Tk.Button(self.button_frame, text='Save', command=self.save_plot)
        self.save_button.pack(side=Tk.LEFT)
        
        # save entry
        save_frame = Tk.Frame(master=self.root)
        save_frame.pack(side = Tk.TOP, anchor="w")
        save_label = Tk.Label(save_frame, text="Save filename:")
        save_label.pack(side=Tk.LEFT)
        self.save_entry = Tk.Entry(save_frame)
        self.save_entry.insert(Tk.END, self.config_file)
        self.save_entry.pack(side=Tk.LEFT)

    def on_closing(self):
        """
        Exit program when closing window.
        """
        self.root.destroy()
        exit()

    def save_plot(self):
        """
        Save plot using pickle format.
        """
        pickle.dump(self.fig, open(self.save_entry.get()+".pickle", 'wb'))
        print "Plot saved"

