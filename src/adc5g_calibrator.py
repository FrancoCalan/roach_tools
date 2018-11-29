import adc5g
from experiment import Experiment

class Adc5gCalibrator(Experiment):
    """
    Class used to calibrate ROACH2's ADC5G ADCs.
    This is usually done before another experiment.
    The implmented calibrations are:
    - Mixed Mode Clock Manager (MMCM) calibration,
        using Jack Hickish implmentation: https://github.com/jack-h/adc_tests/tree/disentangle
    - TODO Offset, Gain, Phase (OGP) calibration,
        borrowing scripts from NRAO's repo: https://github.com/nrao/adc5g_devel
    - TODO Integral Non-Linearity (INL) calibration,
        borrowing scripts from NRAO's repo: https://github.com/nrao/adc5g_devel
    """
    def __init__(self, calanfpga):
        Experiment.__init__(self, calanfpga)

    def perform_calibrations(self):
        """
        Perform MMCM, OGP or/and INL calibrations as indicated in the
        config file.
        """
        if self.settings.do_mmcm:
            self.perform_mmcm_calibration()
        #if self.settings.do_ogp:
        #    self.perform_ogp_calibration()
        #if self.settings.do_inl:
        #    self.perform_inl_calibration()

    def perform_mmcm_calibration(self):
        """
        Perform MMCM calibration using the info from the
        config file.
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

