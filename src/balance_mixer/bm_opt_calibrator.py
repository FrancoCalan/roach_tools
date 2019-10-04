import time, json, datetime
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize
from ..calanfigure import CalanFigure
from ..experiment import Experiment, get_nchannels
from ..digital_sideband_separation.dss_calibrator import float2fixed
from ..axes.spectrum_axis import SpectrumAxis
from ..pocket_correlator.mag_ratio_axis import MagRatioAxis
from ..pocket_correlator.angle_diff_axis import AngleDiffAxis

class BmOptCalibrator(Experiment):
    """
    Class to calibrate balance mixer using broadband
    noise input and optimization method.
    """
    def __init__(self, calanfpga):
        Experiment.__init__(self, calanfpga)
        self.bw = self.settings.bw
        self.nchannels = get_nchannels(self.settings.synth_info)
        self.freqs = np.linspace(0, self.bw, self.nchannels, endpoint=False)

        # const dtype info
        self.consts_nbits = np.dtype(self.settings.const_brams_info['data_type']).alignment * 8
        self.consts_bin_pt = self.settings.const_bin_pt

        # figures
        self.calfigure  = CalanFigure(n_plots=4, create_gui=False)

        # axes on figures
        self.calfigure.create_axis(0, SpectrumAxis, self.freqs, 'ZDOK0 spec')
        self.calfigure.create_axis(1, SpectrumAxis, self.freqs, 'ZDOK1 spec')
        self.calfigure.create_axis(2, MagRatioAxis, self.freqs, ['ZDOK0/ZDOK1'], 'Magnitude Ratio')
        self.calfigure.create_axis(3, AngleDiffAxis, self.freqs, ['ZDOK0-ZDOK1'], 'Angle Difference')

    def run_bm_opt_test(self):
        """
        Run test for balance mixer with optimization method.
        """
        sleep_time = 5
        initial_time = time.time()
        # first get calibration constants
        print "\tCompute calibration data cold..."; step_time = time.time()
        time.sleep(sleep_time)
        [a2_cold, b2_cold, ab_cold] = self.compute_calibration()
        print "\tdone (" + str(time.time() - step_time) + "[s])"

        raw_input("Now set the noise source to hot and press start...")
        print "\tCompute calibration data hot..."; step_time = time.time()
        time.sleep(sleep_time)
        [a2_hot, b2_hot, ab_hot] = self.compute_calibration()
        print "\tdone (" + str(time.time() - step_time) + "[s])"

        #print "Saving data..."
        #datetime_now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        #np.savez('bm_data ' + datetime_now, a2_cold=a2_cold, b2_cold=b2_cold, ab_cold=ab_cold,
        #    a2_hot=a2_hot, b2_hot=b2_hot, ab_hot=ab_hot)
        #print "done"
        
        # try to optimize
        success_arr = []
        consts_arr =  []
        start_time = time.time()
        for i in range(self.nchannels):
            v1c = a2_cold[i]; v2c = b2_cold[i]; v1v2c = ab_cold[i]
            v1h = a2_hot[i];  v2h = b2_hot[i];  v1v2h = ab_hot[i]
            vvec = [v1c, v2c, v1v2c, v1h, v2h, v1v2h]
            success, cal_const = optimize_bm(vvec)
            success_arr.append(success); consts_arr.append(cal_const)
        print "Total time: " + str(time.time()-start_time) + "[s]"
        print "Success rate: " + str(sum(success_arr)) + "/" + str(len(success_arr))
        # correct data that is offscale
        consts_arr = [1+0j if abs(const)>8 else const for const in consts_arr]
        consts_arr = np.array(consts_arr)

        # Computing LNR
        print "### Computing parameters for cold source ###"
        print "Loading ideal constants RF (1) and getting data..."; step_time = time.time()
        consts = 1*np.ones(self.nchannels, dtype=np.complex)
        self.load_constants(consts)
        time.sleep(sleep_time)
        rf_hot_ideal = self.fpga.get_bram_data(self.settings.synth_info)
        print "\tdone (" + str(time.time() - step_time) + "[s])"

        print "Loading ideal constants LO (-1) and getting data..."; step_time = time.time()
        consts = -1*np.ones(self.nchannels, dtype=np.complex)
        self.load_constants(consts)
        time.sleep(sleep_time)
        lo_hot_ideal = self.fpga.get_bram_data(self.settings.synth_info)
        print "\tdone (" + str(time.time() - step_time) + "[s])"

        print "Loading calibrated constants RF and getting data..."; step_time = time.time()
        consts = consts_arr
        self.load_constants(consts)
        time.sleep(sleep_time)
        rf_hot_cal = self.fpga.get_bram_data(self.settings.synth_info)
        print "\tdone (" + str(time.time() - step_time) + "[s])"

        print "Loading calibrated constants LO and getting data..."; step_time = time.time()
        consts = -1*consts_arr
        self.load_constants(consts)
        time.sleep(sleep_time)
        lo_hot_cal = self.fpga.get_bram_data(self.settings.synth_info)
        print "\tdone (" + str(time.time() - step_time) + "[s])"

        raw_input("Set the noise source to cold and press start...")
        print "Loading ideal constants RF (1) and getting data..."; step_time = time.time()
        consts = 1*np.ones(self.nchannels, dtype=np.complex)
        self.load_constants(consts)
        time.sleep(sleep_time)
        rf_cold_ideal = self.fpga.get_bram_data(self.settings.synth_info)
        print "\tdone (" + str(time.time() - step_time) + "[s])"

        print "Loading ideal constants LO (-1) and getting data..."; step_time = time.time()
        consts = -1*np.ones(self.nchannels, dtype=np.complex)
        self.load_constants(consts)
        time.sleep(sleep_time)
        lo_cold_ideal = self.fpga.get_bram_data(self.settings.synth_info)
        print "\tdone (" + str(time.time() - step_time) + "[s])"

        print "Loading calibrated constants RF and getting data..."; step_time = time.time()
        consts = consts_arr
        self.load_constants(consts)
        time.sleep(sleep_time)
        rf_cold_cal = self.fpga.get_bram_data(self.settings.synth_info)
        print "\tdone (" + str(time.time() - step_time) + "[s])"

        print "Loading calibrated constants LO and getting data..."; step_time = time.time()
        consts = -1*consts_arr
        self.load_constants(consts)
        time.sleep(sleep_time)
        lo_cold_cal = self.fpga.get_bram_data(self.settings.synth_info)
        print "\tdone (" + str(time.time() - step_time) + "[s])"

        print "Saving data..."
        data = {}
        data['freqs']         = self.freqs.tolist()
        data['a2_cold']       = a2_cold.tolist()
        data['b2_cold']       = b2_cold.tolist()
        data['ab_re_cold']    = np.real(ab_cold).tolist()
        data['ab_im_cold']    = np.imag(ab_cold).tolist()
        data['a2_hot']        = a2_hot.tolist()
        data['b2_hot']        = b2_hot.tolist()
        data['ab_re_hot']     = np.real(ab_hot).tolist()
        data['ab_im_hot']     = np.imag(ab_hot).tolist()
        data['success']       = success_arr
        data['rf_cold_ideal'] = rf_cold_ideal.tolist()
        data['rf_hot_ideal']  = rf_hot_ideal.tolist()
        data['lo_cold_ideal'] = lo_cold_ideal.tolist()
        data['lo_hot_ideal']  = lo_hot_ideal.tolist()
        data['rf_cold_cal']   = rf_cold_cal.tolist()
        data['rf_hot_cal']    = rf_hot_cal.tolist()
        data['lo_cold_cal']   = lo_cold_cal.tolist()
        data['lo_hot_cal']    = lo_hot_cal.tolist()
        data['cal_acc_len']   = self.fpga.read_reg(self.settings.spec_info['acc_len_reg'])
        data['syn_acc_len']   = self.fpga.read_reg(self.settings.synth_info['acc_len_reg'])

        datetime_now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open('bm_data ' + datetime_now + '.json', 'w') as jsonfile:
                json.dump(data, jsonfile,  indent=4)
        print "\tdone (" + str(time.time() - step_time) + "[s])"
        print "Total time: " + str(time.time() - initial_time) + "[s]"

    def compute_calibration(self):
        """
        Compute calibration constants with broadband noise signal.
        :return: calibration constants.
        """
        # get power-crosspower data
        cal_a2, cal_b2 = self.fpga.get_bram_data(self.settings.spec_info)
        cal_ab_re, cal_ab_im = self.fpga.get_bram_data(self.settings.crosspow_info)    

        # compute ratio
        cal_ab = cal_ab_re + 1j*cal_ab_im
        ab_ratios = cal_ab / cal_b2 # ab* / bb* = a/b

        # plot spec data
        [cal_a2_plot, cal_b2_plot] = \
            self.scale_dbfs_spec_data([cal_a2, cal_b2], self.settings.spec_info)
        self.calfigure.axes[0].plot(cal_a2_plot)
        self.calfigure.axes[1].plot(cal_b2_plot)

        # plot the magnitude ratio and phase difference
        self.calfigure.axes[2].plot([np.abs(ab_ratios)])
        self.calfigure.axes[3].plot([np.angle(ab_ratios, deg=True)])
        plt.pause(0.1)

        return cal_a2, cal_b2, cal_ab

    def load_constants(self, consts):
        consts_real = float2fixed(self.consts_nbits, self.consts_bin_pt, np.real(consts))
        consts_imag = float2fixed(self.consts_nbits, self.consts_bin_pt, np.imag(consts))
        self.fpga.write_bram_data(self.settings.const_brams_info, [consts_real, consts_imag])

def optimize_bm(vvec):
    lnr_chnl_neg = lambda z : -1*lnr(vvec, z)
    sol = minimize(lambda z : lnr_chnl_neg(z[0] + 1j*z[1]), x0=[1,0])
    return sol.success, sol.x[0] + 1j*sol.x[1]

def lnr(vvec, z):
    [v1c, v2c, v1v2c, v1h, v2h, v1v2h] = vvec
    lnr = (powr(v1h, v2h, v1v2h,  z) - powr(v1c, v2c, v1v2c,  z)) / \
          (powr(v1h, v2h, v1v2h, -z) - powr(v1c, v2c, v1v2c, -z)) + 1
    
    # check that imaginary part is clode to zero
    #print np.imag(lnr)
    #assert(abs(np.imag(lnr)) <= 0.0001)

    return np.real(lnr)
    
def powr(a2, b2, ab, z):
    return a2 + z*ab + z*np.conj(ab) + abs(z)**2 * b2
