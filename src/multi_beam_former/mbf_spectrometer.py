import time
import numpy as np
from ..spectra_animator import SpectraAnimator, scale_dbfs_spec_data
from ..digital_sideband_separation.dss_calibrator import float2fixed

class MBFSpectrometer(SpectraAnimator):
    """
    Class used to plot spectral data in the particular 
    case of the multi beam former models (it requires 
    some constant loading first).
    """

    def __init__(self, calanfpga):
        SpectraAnimator.__init__(self, calanfpga)

        # set the cal constants to 1 in startup.
        # Note: no calibration is done here, this is
        # just to test the model with a direct tone in all inputs
        nspecs =len(self.settings.plot_titles)
        write_phasor_reg_list(self.fpga, nspecs*[1], range(nspecs), self.settings.cal_phase_info)
        addrs = [[0,0] + [i] for i in range(nspecs)]        
        write_phasor_reg_list(self.fpga, nspecs*[1], addrs, self.settings.bf_phase_info)

    def get_data(self):
        """
        Gets the spectra data from the mbf model. As per model design all data is synced.
        :return: spectral data.
        """
        spec_data = self.fpga.get_bram_data_sync(self.settings.spec_info)
        spec_data = scale_dbfs_spec_data(self.fpga, spec_data, self.settings.spec_info)
        
        return spec_data

def write_phasor_reg(fpga, phasor, addrs, phase_bank_info, verbose=True):
    """
    Writes a phasor (complex) constant into a register from a register bank
    in the FPGA. The method to write the phasor is:

        1. Write the complex value into software registers, one for the real and other
            for the imaginary part.
        2. Write the appropate value(s) into the address register(s). This/these value(s)
            select the register in the register bank. In some cases it also select the
            the appropate bank if you have more than ohe register bank.
        3. Create a positive edge (0->1) in  the we (write enable register). This register
            is reseted to 0 before anything else in order to avoid tampering with the
            rest of the bank.

    :param fpga: CalanFpga object.
    :param phasor: complex constant to write in the register bank.
    :param addrs: address (integer) or list of addresses to set in the address registers
        to properly select the register in the register bank. The number of addresses must
        coincide with the number of address registers.
    :param phase_bank_info: dictionary with the info of the phase bank.
        The phase_bank_info dictionary format is:
        {'const_bin_pt' : constant binary point in the model for the fixed 
                          point representation.
         'phasor_regs'  : list of two registers for the real and imaginary part 
                         of the phasor constant. E.g.: ['real_reg', 'imag_reg'].
         'addr_regs'    : register or list of registers for the address(es) in the bank.
         'we_reg'       : write enable register.
        }
    :param verbose: True: be verbose when writing registers.
    """
    # 1. write phasor registers
    nbits = phase_bank_info['const_nbits']
    bin_pt = phase_bank_info['const_bin_pt']
    phasor_re = float2fixed(nbits, bin_pt, np.real([phasor])) # Assuming 32-bit registers
    phasor_im = float2fixed(nbits, bin_pt, np.imag([phasor])) # Assuming 32-bit registers
    fpga.set_reg(phase_bank_info['phasor_regs'][0], phasor_re, verbose)
    fpga.set_reg(phase_bank_info['phasor_regs'][1], phasor_im, verbose)

    # 2. write address register(s)
    if isinstance(phase_bank_info['addr_regs'], str): # case one register
        fpga.set_reg(phase_bank_info['addr_regs'], addrs, verbose)
    
    else: # case multiple registers
        for addr_reg, addr in zip(phase_bank_info['addr_regs'], addrs):
            fpga.set_reg(addr_reg, addr, verbose)
            
    # 3. posedge in we register
    #time.sleep(0.0)
    fpga.set_reg(phase_bank_info['we_reg'], 1, verbose)
    fpga.set_reg(phase_bank_info['we_reg'], 0, verbose)

def write_phasor_reg_list(fpga, phasor_list, addr_list, phase_bank_info, verbose=True):
    """
    Write multiple phasors in a register bank using write_phasor_reg().
    :param fpga: CalanFpga object.
    :param phasor_list: list of phasors to write.
    :param addr_list: list of addresses to write into.
    :param phase_bank_info: dictionary with the info of the phase bank.
        The dictionary format is the same as for write_phasor_reg_list.
    :param verbose: True: be verbose when start wirting phasors.
    """
    if verbose:
        print("Writing phasor registers...")
    for phasor, addr in zip(phasor_list, addr_list):
        write_phasor_reg(fpga, phasor, addr, phase_bank_info, verbose=False)
    if verbose:
        print("done")
