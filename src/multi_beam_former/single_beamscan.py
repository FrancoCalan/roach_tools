import itertools
import numpy as np
import pyplot.matplotlib as plt
from ..experiment import Experiment
from ..calanfigure import CalanFigure
from beamscan_axis import BeamscanAxis
from mbf_spectrometer import write_phasor_reg

class SingleBeamscan(Experiment):
    """
    This class uses a single beam from the multi beam former
    to to perform a square 2-dimensional with a 4x4 antenna
    array.
    """
    Experiment.__init__(self, calanfpga)
    
    # beam scan parameters
    self.beamformer = [0,0]
    self.freq_chnl = self.settings.freq_chnl
    self.az_angs = self.settings.az_angs 
    self.el_angs = self.settings.el_angs 

    self.scan_mat = np.zeros((len(az_angs), len(el_angs)))

    # figure and axis
    self.figure = CalanFigure(n_plots=1, create_gui=False)
    self.figure.create_axis(0, BeamscanAxis, 
        (az_angs[0], az_angs[-1]), (el_angs[0], el_angs[-1]), self.figure.fig)

    def make_single_beam_scan(self):
        """
        Make the beam scan.
        """
        # steering the beam through all positions and get single channel power
        print "Start beamscan..."
        for i, el in enumerate(self.el_angs):
            print "\tSteering though elevation " + str(el) + ", index: " + str(i)
            for j, az in enumerate(self.az_angs):
                self.steer_beam((az, el))
                spec_data = self.fpga.get_bram_data_sync(self.settings.spec_info)
                self.scan_mat[i, j] = spec_data(self.freq_chnl)
        print "Beamscan ended."

        # produce plot
        self.figure.plot(self.scan_mat)
        plt.pause(0.1)
        raw_input()

    def ster_beam(self, point_dir):
        """
        Given a phase array antenna that outputs into the ROACH,
        set the appropiate phasor constants so that the array points
        to a given direction (in azimuth and elevation angles). The exact 
        phasors are computed using the dir2phasors() functions and the 
        array_info parameter from the config script.
        :param point_dir: touple with the azimuth and elevation angles to
            point the beam.
        """
        phasor_list = dir2phasors(self.settings.array_info, point_dir)

        for i, phasor in enumerate(phasor_list):
            addrs = self.beamformer + [i]
            write_phasor_reg(self.fpga, phasor, addrs, self.settings.bf_phase_bank)
        
def dir2phasors(array_info, point_dir): 
    """
    Comuptes the phasor constants for every element of
    a phase array antennta in order to make it point to
    point_dir. All the necesary information on the phase 
    array to compute the constants should contained in the 
    array_info dictionary. Notice that the pointing direction
    depends of the definitions in array_info (the definition of
    the origin point for example).
    :param array_info: dictionary with all the information 
        of the phase array.
    :param point_dir: touple with the azimuth and elevation angles to
        point the array.
    :return: phase constants for every element in the array to
        set in order to properly point the array to point_dir.
    """
    pass
