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

import os, sys, importlib, json
import numpy as np
import matplotlib.pyplot as plt
import Tkinter as Tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from experiment import Experiment

class Plotter(Experiment):
    """
    Generic plotter class.
    """
    def __init__(self, calanfpga):
        Experiment.__init__(self, calanfpga)
        self.root = Tk.Tk()
        self.fig = plt.Figure()
        self.plot_map = {1:'11', 2:'12', 3:'22', 4:'22'}
        self.config_file = os.path.splitext(sys.argv[1])[0]
        self.line_arr = []

    def set_plot_parameters(self):
        """
        Add the basic parameters to the plot.
        """
        for i in range(self.nplots):
            ax = self.fig.add_subplot(self.plot_map[self.nplots]+str(i+1))
            ax.set_xlim(self.xlim)
            ax.set_ylim(self.ylims[i])
            ax.set_xlabel(self.xlabel)
            ax.set_ylabel(self.ylabels[i])
            ax.set_title(self.titles[i])
            ax.grid(True)
            # for multiline plot with legends
            if hasattr(self, 'legends'):
                for legend in self.legends:
                    self.line_arr.append(ax.plot([], [], lw=2, label=legend)[0])
                ax.legend()
            # for single line plots
            else:
                self.line_arr.append(ax.plot([], [], lw=2)[0])

        self.fig.set_tight_layout(True)

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
        self.set_plot_parameters()
        self.create_window()
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
        self.save_button = Tk.Button(self.button_frame, text='Save', command=self.save_data)
        self.save_button.pack(side=Tk.LEFT)
        
        # save entry
        save_frame = Tk.Frame(master=self.root)
        save_frame.pack(side = Tk.TOP, anchor="w")
        save_label = Tk.Label(save_frame, text="Save filename:")
        save_label.pack(side=Tk.LEFT)
        self.save_entry = Tk.Entry(save_frame)
        self.save_entry.insert(Tk.END, self.config_file)
        self.save_entry.pack(side=Tk.LEFT)

    def save_data(self):
        """
        Save plot data if data2dict is implemented.
        """
        try:
            json_data = self.data2dict()
            with open(self.save_entry.get()+'.json', 'w') as jsonfile:
                json.dump(json_data, jsonfile,  indent=4)
            print "Data saved."
    
        except AttributeError as e:
            print "This plot doesn't have save option."

    def linear_to_dBFS(self, data):
        """
        Turn data in linear scale to dBFS scale. It uses the dBFS_const value
        from the configuration file to adjust the zero in the dBFS scale.
        """
        return 10*np.log10(data+1) - self.settings.dBFS_const

    def get_spec_time_arr(self, n_specs):
        """
        Compute a time array with timestamps for 'n_specs' spetra, starting at 0.
        Used as x-axis for time related plots. In [us].
        """
        n_brams = len(self.settings.spec_info['bram_list2d'][0])
        n_channels = n_brams * 2**self.settings.spec_info['addr_width']
        x_time = np.arange(0, n_specs) * (1.0/self.settings.bw) * n_channels # [us]
        return x_time

