from itertools import chain
import numexpr
import numpy as np
import Tkinter as Tk
from animator import Animator
from experiment import linear_to_dBFS, get_nchannels
from axes.spectrum_axis import SpectrumAxis

class SpectraAnimator(Animator):
    """
    Class responsable for drawing spectra plots.
    """
    def __init__(self, calanfpga):
        Animator.__init__(self, calanfpga)
        self.nplots = len(self.settings.plot_titles)
        mpl_axes = self.create_axes()
        
        self.nchannels = get_nchannels(self.settings.spec_info)
        for i, ax in enumerate(mpl_axes):
            self.axes.append(SpectrumAxis(ax, self.nchannels,
                self.settings.bw, self.settings.plot_titles[i]))

        self.entries = []
        
        self.maxhold_on = False
        self.maxhold_data = self.nplots * [-np.inf*np.ones(self.nchannels)]
        
    def get_data(self):
        """
        Gets the spectra data form the spectrometer model.
        """
        spec_data_arr = self.fpga.get_bram_list_interleaved_data(self.settings.spec_info)
        spec_plot_arr = []
        for i, spec_data in enumerate(spec_data_arr):
            spec_data = spec_data / float(self.fpga.read_reg('acc_len')) # divide by accumulation
            spec_data = linear_to_dBFS(spec_data, self.settings.spec_info)
            if self.maxhold_on:
                self.maxhold_data[i] = np.maximum(self.maxhold_data[i], spec_data)
                spec_data = self.maxhold_data[i]
            spec_plot_arr.append(spec_data)

        return spec_plot_arr

    def create_window(self):
        """
        Create window and add widgets.
        """
        Animator.create_window(self)

        # reset button
        self.reset_button = Tk.Button(self.button_frame, text='Reset', command=self.reset_spec)
        self.reset_button.pack(side=Tk.LEFT)

        # max hold button
        self.maxhold_button = Tk.Button(self.button_frame, text='Max Hold Off', command=self.toggle_maxhold)
        self.maxhold_button.pack(side=Tk.LEFT)

        # acc_len entry
        self.add_reg_entry('acc_len')

    def data2dict(self):
        """
        Fills the data_dict dictuinary with spectrometer data for file saving.
        """
        self.get_ydata_to_dict()
        self.data_dict.update(self.axes[0].gen_xdata_dict())
        self.data_dict['acc_len'] = self.fpga.read_reg('acc_len')

    def add_reg_entry(self, reg):
        """
        Add a text entry for modifying regiters in FPGA."
        """
        frame = Tk.Frame(master=self.root)
        frame.pack(side = Tk.TOP, anchor="w")
        label = Tk.Label(frame, text=reg+":")
        label.pack(side=Tk.LEFT)
        entry = Tk.Entry(frame)
        entry.insert(Tk.END, self.fpga.read_reg(reg))
        entry.pack(side=Tk.LEFT)
        entry.bind('<Return>', lambda x: self.set_reg_from_entry(reg, entry))
        self.entries.append(entry)
        return frame

    def set_reg_from_entry(self, reg, entry):
        """
        Modify a FPGA register from the value of an entry.
        """
        string_val = entry.get()
        try:
            val = int(numexpr.evaluate(string_val))
        except:
            raise Exception('Unable to parse value in textbox: ' + string_val)
        self.fpga.set_reg(reg, val)

    def reset_spec(self):
        """
        Reset spectra counters, accumulators and software max hold.
        """
        self.fpga.reset_reg('cnt_rst')
        if self.maxhold_on:
            self.toggle_maxhold()

    def toggle_maxhold(self):
        """
        Activate and deactivate max hold of spectral data on button press.
        """
        if self.maxhold_on:
            self.maxhold_on = False
            self.maxhold_button.config(relief=Tk.RAISED)
            self.maxhold_button.config(text="Max Hold Off")
            self.maxhold_data = self.nplots * [-np.inf*np.ones(self.nchannels)]
            print "Max Hold off"
        else:
            self.maxhold_on = True
            self.maxhold_button.config(relief=Tk.SUNKEN)
            self.maxhold_button.config(text="Max Hold On")
            print "Max Hold on"
