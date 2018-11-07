import numpy as np
import Tkinter as Tk
from spectra_animator import SpectraAnimator
from convergence_plotter import ConvergencePlotter
from stability_plotter import StabilityPlotter

class KestfiltAnimator(SpectraAnimator):
    """
    Class responsable for drawing spectra plots in a Kestfilt implementation.
    """
    def __init__(self, calanfpga):
        SpectraAnimator.__init__(self, calanfpga)

    def add_figure_widgets(self):
        """
        add widgets for kestfilt figure.
        """
        SpectraAnimator.add_figure_widgets(self)
        
        # filter_on button
        self.filter_on_button = Tk.Button(self.button_frame, command=self.toggle_filter)
        self.filter_on_button.pack(side=Tk.LEFT)
        if self.fpga.read_reg('filter_on') == 0:
            self.filter_on_button.config(relief=Tk.RAISED)
            self.filter_on_button.config(text="RFI Filter Off")
        else:
            self.filter_on_button.config(relief=Tk.SUNKEN)
            self.filter_on_button.config(text="RFI Filter On")

        # plot conv button
        self.plot_conv_button = Tk.Button(self.button_frame, text='Plot conv', command=self.plot_convergence)
        self.plot_conv_button.pack(side=Tk.LEFT)

        # plot stab button
        self.plot_stab_button = Tk.Button(self.button_frame, text='Plot stab', command=self.plot_stability)
        self.plot_stab_button.pack(side=Tk.LEFT)
       
        # filter_gain entry
        self.add_reg_entry('filter_gain')

        # filter_acc entry
        self.add_reg_entry('filter_acc')

        # channel entry
        self.add_channel_entry('channel')

    def get_save_data(self):
        """
        Get kestfilt data for saving.
        :return: kestfilt data id dictionary format.
        """
        save_data = SpectraAnimator.get_save_data(self)
        save_data['filter_gain'] = self.fpga.read_reg('filter_gain')
        save_data['filter_acc'] = self.fpga.read_reg('filter_acc')

        return save_data

    def toggle_filter(self):
        """
        Activate and deactivate kesteven filter at button press.
        """
        if self.fpga.read_reg('filter_on') == 1:
            self.filter_on_button.config(relief=Tk.RAISED)
            self.filter_on_button.config(text="RFI Filter Off")
            self.fpga.set_reg('filter_on', 0)
            print('Filter is off')
        else:
            self.filter_on_button.config(relief=Tk.SUNKEN)
            self.filter_on_button.config(text="RFI Filter On")
            self.fpga.set_reg('filter_on', 1)
            print('Filter is on')

    def add_channel_entry(self, chnl_reg):
        """
        Add the channel reg entry with the extra label indicating the
        corresponding frequency for that channel.
        """
        frame = SpectraAnimator.add_reg_entry(self, chnl_reg)
        chnl_entry = self.entries[-1]
        chnl_value = self.fpga.read_reg(chnl_reg)
        chnl_freq = self.get_freq_from_channel(chnl_value, self.settings.spec_info)
        freq_label = Tk.Label(frame, text= str(chnl_freq) + " MHz")
        freq_label.pack(side=Tk.LEFT)
        chnl_entry.bind('<Return>', lambda x: self.set_channel_reg(chnl_reg, chnl_entry, freq_label))

    def set_channel_reg(self, chnl_reg, chnl_entry, freq_label):
        """
        Set the channel register and update the channel frequency label.
        """
        SpectraAnimator.set_reg_from_entry(self, chnl_reg, chnl_entry)
        chnl_value = self.fpga.read_reg(chnl_reg)
        chnl_freq = self.get_freq_from_channel(chnl_value)
        freq_label['text'] = str(chnl_freq) + " MHz" 
        

    def plot_convergence(self):
        ConvergencePlotter(self.fpga).show_plot()

    def plot_stability(self):
        StabilityPlotter(self.fpga).show_plot()
