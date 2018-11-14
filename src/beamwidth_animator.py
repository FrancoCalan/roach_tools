import os, json
import numpy as np
import Tkinter as Tk
from kestfilt_animator import KestfiltAnimator
from axes.kestfilt_beamwidth_axis import KestfiltBeamwidthAxis

class BeamwidthAnimator(KestfiltAnimator):
    """
    Class responsable for drawing spectra plots in a beamwidth implementation.
    """
    def __init__(self, calanfpga):
        KestfiltAnimator.__init__(self, calanfpga)
        
        # add beamwidth axis
        self.figure.create_axis(3, KestfiltBeamwidthAxis, [], 'Beamwidth')

    def add_figure_widgets(self):
        """
        Add widgets to beamwidth figure.
        """
        KestfiltAnimator.add_figure_widgets(self)

        # beamwidth button
        self.bw_button = Tk.Button (self.button_frame, text='bw', command=self.plot_bw)
        self.bw_button.pack(side=Tk.LEFT)

        # bw lims entry
        bwlims_label = Tk.Label(self.button_frame, text="BW lims:")
        bwlims_label.pack(side=Tk.LEFT)
        self.bwlims_entry = Tk.Entry(self.button_frame)
        self.bwlims_entry.insert(Tk.END, '100 2000')
        self.bwlims_entry.pack(side=Tk.LEFT)

        # change save default text
        self.save_entry.delete(0, Tk.END)
        self.save_entry.insert(Tk.END, 'offset_-15_0')

    def save_data(self):
        """
        Save the beamwidth figure, update the beamwith plot with the new data, 
        and change the save text for the next offset measurement.
        """
        KestfiltAnimator.save_data(self)
        self.plot_bw()

        # change save text to next offset
        entry_text = self.save_entry.get()
        offset = get_offset(entry_text)
        self.save_entry.delete(0, Tk.END)
        self.save_entry.insert(Tk.END, 'offset_'+str(offset+1)+'_0')

    def plot_bw(self):
        """
        plot beamwidth from saved data in .json files in the root directory.
        Uses info in bwlims entry to define the frequency limits to compute
        the total power.
        """
        # get .json filenames with offset info
        filenames = os.listdir('.')
        def is_offset(filename):
            return filename[:7] == 'offset_'
        offset_filenames = filter(is_offset, filenames)

        # sort filenames using the offset in the name
        offsets = [get_offset(offset_filename) for offset_filename in offset_filenames]
        offset_filenames = sorted(offset_filenames, key=get_offset)

        # get data arrays
        dataarr = []
        for datafile in offset_filenames:
            jsondata = json.load(open(datafile))
            dataarr.append(jsondata)
        
        # get added power data
        prim_power = []
        filt_power = []
        bw_lims = np.array(self.bwlims_entry.get().split(), dtype=np.int64)
        for data in dataarr:
            prim_powers = 10**(np.array(data['primary_signal_power_dbfs'])/10)
            filt_powers = 10**(np.array(data['filter_output_power_dbfs'])/10)
            prim_power.append(10*np.log10(np.sum(prim_powers[bw_lims[0]:bw_lims[1]])))
            filt_power.append(10*np.log10(np.sum(filt_powers[bw_lims[0]:bw_lims[1]])))

        # plot data
        offsets = [get_offset(offset_filename) for offset_filename in offset_filenames]
        self.figure.axes[3].plot(offsets, [np.array(prim_power), np.array(filt_power)])
        self.figure.axes[3].ax.set_xlim((min(offsets), max(offsets)))
        self.figure.axes[3].ax.set_ylim((min(prim_power+filt_power), max(prim_power+ filt_power)))

def get_offset(filename):
    return int(filename[7:filename.index('_', 7)])
