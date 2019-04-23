import time, datetime
import numpy as np
import matplotlib.pyplot as plt
from  itertools import chain
from ..experiment import Experiment
from ..calanfigure import CalanFigure
from beamscan_axis import BeamscanAxis
from mbf_spectrometer import write_phasor_reg_list
from ..digital_sideband_separation.dss_calibrator import check_overflow

class SingleBeamscan(Experiment):
    """
    This class uses a single beam from the multi beam former
    to perform a square 2-dimensional with a 4x4 antenna
    array.
    """
    def __init__(self, calanfpga):
        Experiment.__init__(self, calanfpga)

        self.bf_spec_info = self.settings.bf_spec_info
        self.bf_phase_info = self.settings.bf_phase_info
        self.array_info = self.settings.array_info

        self.nports = len(list(chain.from_iterable(self.array_info['el_pos']))) # flatten list
        if self.settings.ideal_phase_consts:
            write_phasor_reg_list(self.fpga, self.nports*[1], range(self.nports), self.settings.cal_phase_info)

        # beam scan parameters
        self.beamformer = [0,0]
        self.freq_chnl = self.settings.freq_chnl
        azr = self.settings.az_ang_range
        elr = self.settings.el_ang_range
        self.az_angs = range(azr[0], azr[1]+azr[2], azr[2])
        self.el_angs = range(elr[0], elr[1]+elr[2], elr[2])
        self.n_angs = len(self.az_angs) * len(self.el_angs)

        # figure and axis
        self.figure = CalanFigure(n_plots=1, create_gui=False)
        self.figure.create_axis(0, BeamscanAxis, (self.az_angs[0], self.az_angs[-1]), 
            (self.el_angs[0], self.el_angs[-1]), azr[2], elr[2], self.figure.fig)

        # fix apriori beamformer address in order to speed the process
        self.fpga.set_reg(self.bf_phase_info['addr_regs'][0], self.beamformer[0])
        self.fpga.set_reg(self.bf_phase_info['addr_regs'][1], self.beamformer[1])
        self.bf_phase_info['addr_regs'] = self.bf_phase_info['addr_regs'][2]
        self.addrs = range(self.nports)

    def perform_single_beamscan(self):
        """
        Perform the beam scan.
        """
        # steering the beam through all positions and get single channel power
        print "Making beamscan..."
        start_time = time.time()
        scan_data = []

        for el in self.el_angs:
            for az in self.az_angs:
                self.steer_beam(self.addrs, az, el)

                spec_data = self.fpga.get_bram_data_sync(self.bf_spec_info)[0] # data only from first beamformer
                spec_data = self.scale_dbfs_spec_data(spec_data, self.bf_spec_info)
                scan_data.append(spec_data[self.freq_chnl])

                scan_mat = np.pad(scan_data, (0,self.n_angs-len(scan_data)), 'minimum') # pad the data with the minimum value
                                                                                        # (for proper imshow plotting)
                scan_mat = np.reshape(scan_mat, (len(self.az_angs), len(self.el_angs))) # turn the data into a matrix
                
                # update plot
                self.figure.plot_axes(scan_mat)
                plt.pause(0.00001)
        
        print("Beamscan ended. Time beamscanning: " + str(time.time() - start_time))
        self.print_beamscan_plot(scan_mat, self.figure.axes[0].img.get_extent())

    def steer_beam(self, addrs, az, el):
        """
        Given a phase array antenna that outputs into the ROACH,
        set the appropiate phasor constants so that the array points
        to a given direction (in azimuth and elevation angles). The exact 
        phasors are computed using the dir2phasors() functions and the 
        array_info parameter from the config script.
        :param addrs: list of addresses from the phase bank where to set the constants.
        :param az: azimuth angle to point the beam in degrees.
        :param el: elevation angle to point the beam in degrees.
        """
        phasor_list = angs2phasors(self.array_info, el, az)
        
        # harcoded fix_18_17 assumed from model
        phasor_list = saturate_fixed_comp(18, 17, phasor_list)
        check_overflow(18, 17, np.real(phasor_list))
        check_overflow(18, 17, np.imag(phasor_list))
        
        write_phasor_reg_list(self.fpga, phasor_list, addrs, self.bf_phase_info, verbose=False)

    def print_beamscan_plot(self, scan_mat, extent):
        """
        Print the beamscan plot with different options
        from the live plot.
        :param scan_mat: matrix with the plot data.
        :param extent: limits of the plots. Take them from the
            live plot.
        """
        fig = plt.figure()
        plt.imshow(scan_mat, origin='lower', aspect='equal', interpolation='none',
            extent=extent)
        plt.xlabel('Azimuth ($\phi$) [$^\circ$]')
        plt.ylabel('Elevation ($\\theta$) [$^\circ$]')
        cbar = plt.colorbar()
        cbar.set_label('Power [dB]')

        plt.savefig('single_beamscan ' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '.pdf')

def angs2phasors(array_info, theta, phi): 
    """
    Computes the phasor constants for every element of
    a 2D phase array antenna in order to make it point to the
    direction given by the theta (elevation) and phi (azimuth) 
    angles. All the necesary information on the phase 
    array to compute the constants should contained in the 
    array_info dictionary. Notice that the pointing direction
    depends of the definitions in array_info (the definition of
    the origin point for example).
    :param array_info: dictionary with all the information 
        of the phase array.
    :param theta: elevation angle to point the beam in degrees.
    :param phi: azimuth angle to point the beam in degrees.
    :return: phase constants for every element in the array to
        set in order to properly point the array to the desired direction.
    """
    wavelength = array_info['speed'] / array_info['freq']

    # get array element positions in meters
    el_pos = wavelength * array_info['el_sep'] * np.array(array_info['el_pos'])

    # convert angles into standard ISO shperical coordinates
    # (instead of (0,0) being the array perpendicular direction)
    theta = 90 - theta 
    phi = 90 - phi

    # convert angles into radians
    theta = np.radians(theta)
    phi = np.radians(phi)

    a = np.array([-np.sin(theta) * np.cos(phi), -np.sin(theta) * np.sin(phi), -np.cos(theta)])  # direction of arrival
    k = 2 * np.pi / wavelength * a  # wave-number vector

    # Calculate array manifold vector
    v = np.exp(-1j * np.dot(el_pos, k))

    return list(np.conj(v).flatten())

def saturate_fixed_comp(nbits, bin_pt, data):
    """
    Receives a complex number and saturates its real
    and imaginary part, in order that naither of them
    surpass the upper and lower limits given by a fixed
    representation of nbits bits and binary point bin_pt.
    In case of saturation both the real and imaginary part
    are scaled in order to conserve the angle of the 
    original data.
    :param nbits: bitwidth of the signed fixed point representation.
    :param bin_pt: binary point of the signed fixed point representation.
    :param data: complex number or data list to check.
    :return: number or list with the saturated data.
    """
    if isinstance(data, complex): # case single data
        max_val = (2.0**(nbits-1)-1) / (2**bin_pt)
        min_val = (-2.0**(nbits-1))  / (2**bin_pt)

        data_real = np.real(data)
        data_imag = np.imag(data)

        # case upper saturation
        if data_real > max_val or data_imag > max_val:
            data = data / ((max([data_real, data_imag]) / max_val) + 0.0001)
        # case lower saturation
        if data_real < min_val or data_imag < min_val:
            data = data / ((min([data_real, data_imag]) / min_val) + 0.001)
        return data

    else: # case list of data
        return [saturate_fixed_comp(nbits, bin_pt, data_el) for data_el in data]
        
