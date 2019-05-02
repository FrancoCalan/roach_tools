from ..spectra_animator import SpectraAnimator
from mbf_spectrometer import write_phasor_reg_list

class MBFSpectrometerSync(SpectraAnimator):
    """
    Class used to plot spectral data in the particular 
    case of the multi beam former models (it requires 
    some constant loading first).
    """

    def __init__(self, calanfpga):
        SpectraAnimator.__init__(self, calanfpga)

        if self.settings.ideal_phase_consts:
            nspecs =len(self.settings.spec_titles)
            write_phasor_reg_list(self.fpga, nspecs*[1], range(nspecs), self.settings.cal_phase_info)
        
    def get_data(self):
        """
        Gets the spectra data from the mbf model. As per model design all data is synced.
        :return: spectral data.
        """
        spec_data = self.fpga.get_bram_data_sync(self.settings.spec_info)
        spec_data = self.scale_dbfs_spec_data(spec_data, self.settings.spec_info)
        
        return spec_data
