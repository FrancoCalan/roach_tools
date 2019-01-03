import adc5g
import datetime, os
import numpy as np
import matplotlib.pyplot as plt
from experiment import Experiment, linear_to_dBFS
from calanfigure import CalanFigure
from instruments.generator import create_generator
from axes.snapshot_cal_axis import SnapshotCalAxis
from axes.spectrum_cal_axis import SpectrumCalAxis
from adc5g_devel.ADCCalibrate import ADCCalibrate

class Adc5gCalibrator(Experiment):
    """
    Class used to calibrate ROACH2's ADC5G ADCs.
    This is usually done before another experiment.
    The implmented calibrations are:
    - Mixed Mode Clock Manager (MMCM) calibration,
        using Rurik Primiani implmentation: https://github.com/sma-wideband/adc_tests
    - Offset, Gain, Phase (OGP) calibration,
        borrowing scripts from NRAO's repo: https://github.com/nrao/adc5g_devel
    - Integral Non-Linearity (INL) calibration,
        borrowing scripts from NRAO's repo: https://github.com/nrao/adc5g_devel
    """
    def __init__(self, calanfpga):
        Experiment.__init__(self, calanfpga)
        self.snapshots = self.settings.snapshots
        self.nbins = len(self.fpga.get_snapshots()[0]) / 2
        self.now = datetime.datetime.now()
        self.caldir = self.settings.caldir + '_' + self.now.strftime('%Y-%m-%d %H:%M:%S')

        # figures
        self.snapfigure = CalanFigure(n_plots=len(self.snapshots), create_gui=False)
        self.specfigure = CalanFigure(n_plots=len(self.snapshots), create_gui=False)

        # figure axes
        for i in range(len(self.snapshots)):
            self.snapfigure.create_axis(i, SnapshotCalAxis, self.settings.snap_samples, self.snapshots[i])
            self.specfigure.create_axis(i, SpectrumCalAxis, self.nbins, self.settings.bw, self.snapshots[i] + str(" spec"))

        # calibration source
        self.source = create_generator(self.settings.cal_source)
        self.test_freq = self.settings.cal_source['def_freq']

    def perform_calibrations(self):
        """
        Perform MMCM, OGP or/and INL calibrations as indicated in the
        config file.
        """

        # if doing ogp or inl calibrations...
        if self.settings.do_ogp or self.settings.do_inl:
            # create directory for calibration data
            os.mkdir(self.caldir)
            
            # turn source on and set default freq and power
            self.source.set_freq_mhz()
            self.source.set_power_dbm()
            self.source.turn_output_on()

        # pre calibrations snapshot plots
        if self.settings.plot_snapshots:
            uncal_snaps = self.fpga.get_snapshots(self.settings.snap_samples)
            for axis, uncal_snap in zip(self.snapfigure.axes, uncal_snaps):
                axis.plot([uncal_snap])
            plt.pause(1)
        
        # pre calibration spectrum plots
        if self.settings.plot_spectra:
            dummy_spec_info = {'bram_name' : 'bram', 'addr_width' : int(np.log2(self.nbins))} # used for linear_to_dBFS funct
            uncal_snaps_full = self.fpga.get_snapshots()
            for axis, uncal_snap in zip(self.specfigure.axes, uncal_snaps_full):
                uncal_spec = np.square(np.abs(np.fft.rfft(uncal_snap)[:-1] / np.sqrt(self.nbins))) # the sqrt(nbins) is a workaround for nice plots
                uncal_spec = linear_to_dBFS(uncal_spec, dummy_spec_info)
                axis.plot([uncal_spec])
            plt.pause(1)

        # perform calibrations indicated in configuration file
        if self.settings.do_mmcm:
            self.perform_mmcm_calibration()
        if self.settings.do_ogp:
            self.perform_ogp_calibration()
        if self.settings.do_inl:
            self.perform_inl_calibration()

        # load calibrations, not necessary if you already calibrated
        if not self.settings.do_ogp and not self.settings.do_inl:
            if self.settings.load_ogp:
                print "Loading OGP calibrations..."
                self.load_ogp_calibration()
                print "done"
            if self.settings.load_inl:
                print "Loading INL calibrations..."
                self.load_inl_calibration()
                print "done"

        # post calibrations snapshots plot
        if self.settings.plot_snapshots:
            cal_snaps = self.fpga.get_snapshots(self.settings.snap_samples)
            for axis, uncal_snap, cal_snap in zip(self.snapfigure.axes, uncal_snaps, cal_snaps):
                axis.plot([uncal_snap, cal_snap])
            plt.pause(1)

        # post calibration spectrum plots
        if self.settings.plot_spectra:
            cal_snaps_full = self.fpga.get_snapshots()
            for axis, uncal_snap, cal_snap in zip(self.specfigure.axes, uncal_snaps_full, cal_snaps_full):
                uncal_spec = np.square(np.abs(np.fft.rfft(uncal_snap)[:-1] / np.sqrt(self.nbins))) # the sqrt(nbins) is a workaround for nice plots
                uncal_spec = linear_to_dBFS(uncal_spec, dummy_spec_info)
                cal_spec = np.square(np.abs(np.fft.rfft(cal_snap)[:-1] / np.sqrt(self.nbins))) # the sqrt(nbins) is a workaround for nice plots
                cal_spec = linear_to_dBFS(cal_spec, dummy_spec_info)
                axis.plot([uncal_spec, cal_spec])
            plt.pause(1)
        
        # if doing ogp or inl calibrations...
        if self.settings.do_ogp or self.settings.do_inl:
            self.source.turn_output_off()
        
        print("Done with all calibrations.") 
        
        if self.settings.plot_snapshots or self.settings.plot_spectra:
            print("Close plots to finish.")
            plt.show()

    def perform_mmcm_calibration(self):
        """
        Perform MMCM calibration using Primiani's adc5g package.
        """
        for snap_data in self.settings.snapshots_info:
            adc5g.set_test_mode(self.fpga.fpga, snap_data['zdok'])
        adc5g.sync_adc(self.fpga.fpga)

        for snap_data in self.settings.snapshots_info:
            print "Calibrating ADC5G ZDOK" + str(snap_data['zdok']) + "..."
            opt, glitches = adc5g.calibrate_mmcm_phase(self.fpga.fpga, \
                snap_data['zdok'], snap_data['names'])

            adc5g.unset_test_mode(self.fpga.fpga, snap_data['zdok'])
            print "done"

    def perform_ogp_calibration(self):
        """
        Perform OGP calibration using scraped code from adc5g_devel
        (https://github.com/nrao/adc5g_devel).
        """
        for zdok_info in self.settings.snapshots_info:
            adccal = self.create_adccalibrate_object(zdok_info['zdok'], zdok_info['names'][0])
            adccal.do_ogp(zdok_info['zdok'], self.test_freq, 10)

    def perform_inl_calibration(self):
        """
        Perform INL calibration using scraped code from adc5g_devel
        (https://github.com/nrao/adc5g_devel).
        """
        for zdok_info in self.settings.snapshots_info:
            adccal = self.create_adccalibrate_object(zdok_info['zdok'], zdok_info['names'][0])
            adccal.do_inl(zdok_info['zdok'])

    def load_ogp_calibration(self):
        """
        Load previously saved OGP calibration to ADC.
        """
        for zdok_info in self.settings.snapshots_info:
            adccal = self.create_adccalibrate_object(zdok_info['zdok'], zdok_info['names'][0])
            adccal.load_calibrations(self.settings.loaddir, zdok_info['zdok'], ['ogp'])

    def load_inl_calibration(self):
        """
        Load previously saved INL calibration to ADC.
        """
        for zdok_info in self.settings.snapshots_info:
            adccal = self.create_adccalibrate_object(zdok_info['zdok'], zdok_info['names'][0])
            adccal.load_calibrations(self.settings.loaddir, zdok_info['zdok'], ['inl'])

    def create_adccalibrate_object(self, zdok, snapshot):
        """
        Create the appropate ADCCalibrate object with the parameters from 
        the config file, and personal deafaults to perform calibration 
        and data loading.
        :param zdok: ZDOK port number of the ADC (0 or 1).
        :param snapshot: snapshot block name from where extraxt the data.
        :return: adc5g_devel ADCCalibrate object.
        """
        adccal = ADCCalibrate(roach=self.fpga.fpga, roach_name="", zdok=zdok, 
            snapshot=snapshot, dir=self.caldir, now=self.now, clockrate=self.settings.bw)
        return adccal

