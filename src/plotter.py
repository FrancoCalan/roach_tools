import os, sys, importlib, json
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
import Tkinter as Tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from experiment import Experiment, get_nchannels

class Plotter(Experiment):
    """
    Generic plotter class.
    """
    def __init__(self, calanfpga):
        Experiment.__init__(self, calanfpga)
        # Workaround to Tk.mainloop not clsing properly for plt.figure()
        if not hasattr(self, 'create_gui') or self.create_gui==True:
            self.create_gui = True
            self.fig = plt.Figure()
        else:
            self.fig = plt.figure()
        self.plot_map = {1:'11', 2:'12', 3:'22', 4:'22'}
        self.config_file = os.path.splitext(sys.argv[1])[0]
        self.axes = []
        self.data_dict = {}

    def create_axes(self):
        """
        Return an array of Matplotlib Axes given the number of plots in the plotter.
        """
        axes = []
        for i in range(self.nplots):
            axes.append(self.fig.add_subplot(self.plot_map[self.nplots]+str(i+1)))

        return axes

    def show_plot(self):
        """
        Show plot window.
        """
        self.create_window()
        self.plot_axes() 
        Tk.mainloop()

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

            # button frame
            self.button_frame = Tk.Frame(master=self.root)
            self.button_frame.pack(side=Tk.TOP, anchor="w")

            # save button
            self.save_button = Tk.Button(self.button_frame, text='Save', command=self.save_data)
            self.save_button.pack(side=Tk.LEFT)
            
            # save entry
            save_frame = Tk.Frame(master=self.root)
            save_frame.pack(side = Tk.TOP, anchor="w")
            save_label = Tk.Label(save_frame, text="Save/Print filename:")
            save_label.pack(side=Tk.LEFT)
            self.save_entry = Tk.Entry(save_frame)
            self.save_entry.insert(Tk.END, self.config_file)
            self.save_entry.pack(side=Tk.LEFT)

            # save datetime checkbox
            self.datetime_check = Tk.IntVar()
            self.save_datetime_checkbox = Tk.Checkbutton(save_frame, text="add datetime", variable=self.datetime_check)
            self.save_datetime_checkbox.pack(side=Tk.LEFT)

            # print button
            self.print_button = Tk.Button(self.button_frame, text='Print', command=self.save_fig)
            self.print_button.pack(side=Tk.LEFT)

        else:
            self.fig.show()

    def plot_axes(self):
        """
        Draw plot for every axes in canvas.
        """
        data_arr = self.get_data()
        for axis, ydata in zip(self.axes, data_arr):
            axis.plot(ydata)

    def save_data(self):
        """
        Save plot data if data2dict is implemented.
        """
        try:
            self.data2dict()
            json_filename = self.save_entry.get()
            if self.datetime_check.get():
                json_filename += ' ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            with open(json_filename+'.json', 'w') as jsonfile:
                json.dump(self.data_dict, jsonfile,  indent=4)
            print "Data saved."
        except AttributeError as e:
            print "This plot doesn't have save option."

    def get_ydata_to_dict(self):
        """
        Get the data from axes, and save the to the data dict. 
        """
        for axis in self.axes:
            axis_data_dict = axis.gen_ydata_dict()
            self.data_dict.update(axis_data_dict)

    def save_fig(self):
        """
        Save current plot as a .pdf figure.
        """
        fig_filename = self.save_entry.get()
        if self.datetime_check.get():
            fig_filename += ' ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.fig.savefig(fig_filename + '.pdf')
        print "Plot saved."

    def get_freq_from_channel(self, channel, bram_info):
        """
        Compute the frequency of channel using the bandwidth information.
        """
        return self.settings.bw * channel / get_nchannels(bram_info)

    def get_spec_time_arr(self, n_specs):
        """
        Compute a time array with timestamps for 'n_specs' spetra, starting at 0.
        Used as x-axis for time related plots. In [us].
        """
        n_brams = len(self.settings.spec_info['bram_list2d'][0])
        n_channels = n_brams * 2**self.settings.spec_info['addr_width']
        x_time = np.arange(0, n_specs) * (1.0/self.settings.bw) * n_channels # [us]
        return x_time
