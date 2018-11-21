import numexpr
import numpy as np
import Tkinter as Tk
from plotter import Plotter
from calanfigure import CalanFigure
from experiment import linear_to_dBFS, get_nchannels
from axes.spectrum_axis import SpectrumAxis

class SpectraAnimator(Plotter):
    """
    Class responsable for drawing spectra plots.
    """
    def __init__(self, calanfpga):
        Plotter.__init__(self, calanfpga)
        self.figure = CalanFigure(n_plots=len(self.settings.plot_titles), create_gui=True)
        self.nchannels = get_nchannels(self.settings.spec_info)
        
        for i in range(self.figure.n_plots):
            self.figure.create_axis(i, SpectrumAxis, 
                self.nchannels, self.settings.bw, self.settings.plot_titles[i])

        self.entries = []
        
    def add_figure_widgets(self):
        """
        Add widgets to spectrometer figure.
        """
        self.add_save_widgets("spec_data")

        # reset button
        self.reset_button = Tk.Button(self.button_frame, text='Reset', command=self.reset_spec)
        self.reset_button.pack(side=Tk.LEFT)

        # acc_len entry
        self.add_reg_entry(self.settings.spec_info['acc_len_reg'])

    def get_save_data(self):
        """
        Get spectra data for saving.
        :return: spectra data in dictionary format.
        """
        save_data = Plotter.get_save_data(self)
        save_data.update(self.figure.axes[0].gen_xdata_dict())
        save_data['acc_len'] = self.fpga.read_reg('acc_len')

        return save_data

    def add_reg_entry(self, reg):
        """
        Add a text entry for modifying regiters in FPGA.
        """
        frame = Tk.Frame(master=self.figure.root)
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
        Reset spectra counters and accumulators.
        """
        self.fpga.reset_reg('cnt_rst')

    def get_data(self):
        """
        Gets the spectra data from the spectrometer model.
        :return: spectral data.
        """
        return get_spec_data(self.fpga, self.settings.spec_info)

def get_spec_data(fpga, spec_info):
    """
    Gets spectra data given a CalanFpga object and spec_info dict.
    :param fpga: CalanFpga object.
    :param spec_info: dictionary with info of the spectra memory in the FPGA.
    :return: spectral data in dBFS.
    """
    spec_data_arr = fpga.get_bram_list_interleaved_data(spec_info)
    spec_plot_arr = scale_spec_data_arr(fpga, spec_data_arr, spec_info)

    return spec_plot_arr
    
def scale_spec_data(fpga, spec_data, spec_info):
    """
    Scale spectral data by the accumulation length given by the
    accumulation reg in the spec_info dictionary, and convert
    the data to dBFS. Used for plotting spectra.
    :param fpga: CalanFpga object.
    :param spec_data: spectral data in linear scale, as read with CalanFpga's
        get_bram_data() (or equivalent).
    :param spec_info: dictionary with info of the spectra memory in the FPGA.
        Used to read the accumulation register.
    :return: spectral data in dBFS.
    """
    spec_data = spec_data / float(fpga.read_reg(spec_info['acc_len_reg'])) # divide by accumulation
    spec_data = linear_to_dBFS(spec_data, spec_info)
    return spec_data

def scale_spec_data_arr(fpga, spec_data_arr, spec_info):
    """
    Same as scale_spec_data() but for an array of spectral data.
    """
    scaled_spec_data = [scale_spec_data(fpga, spec_data, spec_info) for spec_data in spec_data_arr]
    return scaled_spec_data


