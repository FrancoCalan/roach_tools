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
        self.axes = []

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
        self.fig.set_tight_layout(True)
        self.create_window()
        self.plot_axes() 
        Tk.mainloop()

    def create_window(self, create_gui=True):
        """
        Create a Tkinter window with all of the components (plots, toolbar, widgets).
        """
        # plots
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.show()
        self.canvas.get_tk_widget().pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)
        
        if create_gui:
            # navigation bar
            toolbar = NavigationToolbar2TkAgg(self.canvas, self.root)
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
            save_label = Tk.Label(save_frame, text="Save filename:")
            save_label.pack(side=Tk.LEFT)
            self.save_entry = Tk.Entry(save_frame)
            self.save_entry.insert(Tk.END, self.config_file)
            self.save_entry.pack(side=Tk.LEFT)

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
            json_data = self.data2dict()
            with open(self.save_entry.get()+'.json', 'w') as jsonfile:
                json.dump(json_data, jsonfile,  indent=4)
            print "Data saved."

        except AttributeError as e:
            print "This plot doesn't have save option."

    def get_nchannels(self):
        """
        Compute the number of channels of an spetrum given the spec_info
        """
        n_brams = len(self.settings.spec_info['bram_list2d'][0])
        return n_brams * 2**self.settings.spec_info['addr_width']

    def get_freq_from_channel(self, channel):
        """
        Compute the frequency of channel using the bandwidth information.
        """
        return self.settings.bw * channel / self.get_nchannels()

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

