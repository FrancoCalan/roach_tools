import adc5g
import datetime
import numpy as np
import matplotlib.pyplot as plt
from experiment import Experiment, linear_to_dBFS
from calanfigure import CalanFigure
from axes.snapshot_cal_axis import SnapshotCalAxis
from axes.spectrum_cal_axis import SpectrumCalAxis

class Adc5gCalibrator(Experiment):
    """
    Class used to calibrate ROACH2's ADC5G ADCs.
    This is usually done before another experiment.
    The implmented calibrations are:
    - Mixed Mode Clock Manager (MMCM) calibration,
        using Rurik Primiani implmentation: https://github.com/sma-wideband/adc_tests
    - TODO Offset, Gain, Phase (OGP) calibration,
        borrowing scripts from NRAO's repo: https://github.com/nrao/adc5g_devel
    - TODO Integral Non-Linearity (INL) calibration,
        borrowing scripts from NRAO's repo: https://github.com/nrao/adc5g_devel
    """
    def __init__(self, calanfpga):
        Experiment.__init__(self, calanfpga)
        self.snapshots = self.settings.snapshots
        self.nbins = len(self.fpga.get_snapshots()[0]) / 2
        self.now = datetime.datetime.now()

        # figures
        self.snapfigure = CalanFigure(n_plots=len(self.snapshots), create_gui=False)
        self.specfigure = CalanFigure(n_plots=len(self.snapshots), create_gui=False)

        # figure axes
        for i in range(len(self.snapshots)):
            self.snapfigure.create_axis(i, SnapshotCalAxis, self.settings.snap_samples, self.snapshots[i])
            self.specfigure.create_axis(i, SpectrumCalAxis, self.nbins, self.settings.bw, self.snapshots[i] + str(" spec"))
            

    def perform_calibrations(self):
        """
        Perform MMCM, OGP or/and INL calibrations as indicated in the
        config file.
        """
        # pre calibrations snapshot plots
        if self.settings.plot_snapshots:
            uncal_snaps = self.fpga.get_snapshots(self.settings.snap_samples)
            for axis, uncal_snap in zip(self.snapfigure.axes, uncal_snaps):
                axis.plot([uncal_snap])
        
        # pre calibration spectrum plots
        if self.settings.plot_spectra:
            dummy_spec_info = {'bram_name' : 'bram', 'addr_width' : int(np.log2(self.nbins))} # used for linear_to_dBFS funct
            uncal_snaps_full = self.fpga.get_snapshots()
            for axis, uncal_snap in zip(self.specfigure.axes, uncal_snaps_full):
                uncal_spec = np.square(np.abs(np.fft.rfft(uncal_snap)[:-1]))
                uncal_spec = linear_to_dBFS(uncal_spec, dummy_spec_info)
                axis.plot([uncal_spec])

        plt.pause(1)

        if self.settings.do_mmcm:
            self.perform_mmcm_calibration()
        if self.settings.do_ogp:
            self.perform_ogp_calibration()
        if self.settings.do_inl:
            self.perform_inl_calibration()
        #if self.settings.load_ogp:
        #    self.load_ogp_calibration()
        #if self.settings.load_inl:
        #    self.load_inl_calibration()

        # post calibrations snaspshots plot
        if self.settings.plot_snapshots:
            cal_snaps = self.fpga.get_snapshots(self.settings.snap_samples)
            for axis, uncal_snap, cal_snap in zip(self.snapfigure.axes, uncal_snaps, cal_snaps):
                axis.plot([uncal_snap, cal_snap])

        # post calibration spectrum plots
        if self.settings.plot_spectra:
            cal_snaps_full = self.fpga.get_snapshots()
            for axis, uncal_snap, cal_snap in zip(self.specfigure.axes, uncal_snaps_full, cal_snaps_full):
                uncal_spec = np.square(np.abs(np.fft.rfft(uncal_snap)[:-1]))
                uncal_spec = linear_to_dBFS(uncal_spec, dummy_spec_info)
                cal_spec = np.square(np.abs(np.fft.rfft(cal_snap)[:-1]))
                cal_spec = linear_to_dBFS(cal_spec, dummy_spec_info)
                axis.plot([uncal_spec, cal_spec])
        
        print("Done with all calibrations. Close plots to finish.")
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
        from adc5g_devel.AdcSnapshot import AdcSnapshot
        from adc5g_devel.SPI import SPI
        from adc5g_devel.OGP import OGP

        for zdok_info in self.settings.snapshots_info:
            adcsnapshot = AdcSnapshot(self.fpga.fpga, zdok_info['zdok'], zdok_info['names'][0],
                clockrate=self.settings.bw)
            spi = SPI(zdok_info['zdok'], self.fpga.fpga)
            ogp = OGP(zdok_info['zdok'], self.settings.caldir, None, spi, adcsnapshot, self.now, 
                clockrate=self.settings.bw)
            
            ogp.do_ogp(zdok_info['zdok'], self.settings.test_freq, 10)

    def perform_inl_calibration(self):
        """
        Perform INL calibration using scraped code from adc5g_devel
        (https://github.com/nrao/adc5g_devel).
        """
        from adc5g_devel.SPI import SPI
        from adc5g_devel.INL import INL

        for zdok_info in self.settings.snapshots_info:
            spi = SPI(zdok_info['zdok'], self.fpga.fpga)
            inl = INL(zdok_info['zdok'], self.settings.caldir, spi, self.now) 

            inl.do_inl(zdok_info['zdok'])
