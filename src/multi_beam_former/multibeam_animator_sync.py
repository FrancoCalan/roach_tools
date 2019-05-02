import time
import numpy as np
from  itertools import chain
from ..animator import Animator
from ..calanfigure import CalanFigure
from beamscan_axis import BeamscanAxis
from single_beamscan import SingleBeamscan
from mbf_spectrometer import write_phasor_reg_list

class MultibeamAnimatorSync(Animator, SingleBeamscan):
    """
    This class plots a square image of the parallel data
    of multiple beams generated by the beamformer at the
    same time.
    """
    def __init__(self, calanfpga):
        Animator.__init__(self, calanfpga)
        self.start_draw_time = 0

        self.bf_spec_info = self.settings.bf_spec_info
        self.bf_phase_info = self.settings.bf_phase_info
        self.array_info = self.settings.array_info

        self.nports = len(list(chain.from_iterable(self.array_info['el_pos']))) # flatten list
        if self.settings.ideal_phase_consts:
            write_phasor_reg_list(self.fpga, self.nports*[1], range(self.nports), self.settings.cal_phase_info)

        # beam forming parameters
        self.freq_chnl = self.settings.freq_chnl
        azr = self.settings.az_ang_range
        elr = self.settings.el_ang_range
        self.az_angs = range(azr[0], azr[1]+azr[2], azr[2])
        self.el_angs = range(elr[0], elr[1]+elr[2], elr[2])

        # figure and axis
        self.figure = CalanFigure(n_plots=1, create_gui=True)
        self.figure.create_axis(0, BeamscanAxis, (self.az_angs[0], self.az_angs[-1]), 
            (self.el_angs[0], self.el_angs[-1]), azr[2], elr[2], self.figure.fig, self.settings.interpolation)

        print "Steering the beams for every beamformer..."
        for i, el in enumerate(self.el_angs):
            for j, az in enumerate(self.az_angs):
                addrs = [[j,i,port] for port in range(self.nports)]
                SingleBeamscan.steer_beam(self, addrs, az, el)
        print "done"

    def get_data(self):
        """
        Get the power data from all the beamformers.
        """
        #checkpoint_time = time.time()
        #print "draw time: " + str(checkpoint_time - self.start_draw_time)

        #checkpoint_time = time.time()
        spec_data = self.fpga.get_bram_data_sync(self.bf_spec_info)
        #print "get_data time: " + str(time.time() - checkpoint_time)
        
        #checkpoint_time = time.time()
        spec_data = self.scale_dbfs_spec_data(spec_data, self.bf_spec_info)
        #print "scale_dbfs time: " + str(time.time() - checkpoint_time)

        #checkpoint_time = time.time()
        mbf_data = np.reshape(np.array(spec_data)[:, self.freq_chnl], (len(self.az_angs), len(self.el_angs)))
        #print "reshape time: " + str(time.time() - checkpoint_time)

        #self.start_draw_time = time.time()
        return mbf_data
