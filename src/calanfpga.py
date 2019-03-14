import sys, os, importlib, time
import numpy as np
from itertools import chain
import corr
from dummies.dummy_fpga import DummyFpga

class CalanFpga():
    """
    Wrapper around corr's FpgaClient in order to add common functions used in 
    Calan Lab (Millimeter Wave Laboratory, Univerity of Chile). Examples of the
    funtions added are: roach initialization, regiter setting/reseting, easy data
    grab from multiple snapshots, bram arrays, interleave bram arrays, etc.
    """
    def __init__(self):
        """
        Initialize the CalanFpga object. You must specify the config file as the
        second argument in the command-line arguments.
        """
        if len(sys.argv) <= 1:
            print("Please provide a config file as a command line argument: " + os.path.basename(sys.argv[0]) + " [config file]")  
            exit()
        config_file = os.path.splitext(sys.argv[1])[0]
        self.settings = importlib.import_module(config_file)
        
        if len(sys.argv) > 2:
            self.parse_commandline_args(sys.argv[2:])

        if self.settings.simulated:
            self.fpga = DummyFpga(self.settings)
        else:
            self.fpga = corr.katcp_wrapper.FpgaClient(self.settings.roach_ip, self.settings.roach_port)
            time.sleep(1)
    
    def parse_commandline_args(self, arg_list):
        """
        Parse aditional command line arguments given when excecuting
        a roach_tools script. The arguments are added as attributes to
        the self.settings variable. It should only be used to override 
        parameters given in the configuration file.
        :param arg_list: list with the command line arguments. The number
            of elements in the list should be even, with the even positioned
            elements being the attributes to be modified in self.settings,
            with the following element being the new value of said attribute. 
            For example: "spectra_animator.py spectra_config.py --boffile newmodel.bof.gz"
        """
        if len(arg_list) % 2 == 1:
            print("Error. The number of additional command line arguments must be even.")
            exit()

        for attrname, attrval in zip(arg_list[0::2], arg_list[1::2]):
            if attrname[0:2] != "--":
                print("Error in command line " + attrname + 
                    ". Use double dash '--' at the begining of attributes names in command line")
                exit()
                
            # try to evaluate attribute value, if fails keep the value as a string.
            try:
                attrval = eval(attrval)
            except NameError:
                pass
            
            setattr(self.settings, attrname[2:], attrval)

    def initialize(self):
        """
        Performs a standard ROACH initialization: Check connection,
        upload and program bof if requested, estimate clock, and
        set and reset the inital state of register listed in the 
        configuration file.
        """
        self.connect_to_roach()
        if self.settings.upload and self.settings.program:
            self.upload_program_fpga()
        elif self.settings.program:
            self.program_fpga()
        self.estimate_clock()
        self.set_reset_regs()

    def connect_to_roach(self):
        """
        Verify communication with ROACH.
        """
        print 'Connecting to ROACH server ' + self.settings.roach_ip + \
            ' on port ' + str(self.settings.roach_port) + '... ' 
        if self.fpga.is_connected():
            print 'ok'
        else:
            print('Unable to connect to ROACH.')
            exit()

    def program_fpga(self):
        """
        Program the .bof/.bof.gz model specified in the config file (boffile) to the FPGA.
        """
        print 'Programming FPGA with ' + self.settings.boffile + '...'
        self.fpga.progdev(os.path.basename(self.settings.boffile))
        time.sleep(1)
        print 'done'

    def upload_program_fpga(self):
        """
        Upload the .bof/.bof.gz model specified in the config file (boffile) to ROACH 
        memory and program FPGA with this model. Note: this don't work in ROACH1.
        """
        print 'Uploading and programming FPGA with ' + self.settings.boffile + '...'
        self.fpga.upload_program_bof(self.settings.boffile, 3000)
        time.sleep(1)
        print 'done'

    def estimate_clock(self):
        """
        Estimate FPGA clock.
        """
        print 'Estimating FPGA clock: ' + str(self.fpga.est_brd_clk()) + '[MHz]'

    def set_reset_regs(self):
        """
        Set registers to a given value and reset registers (->1->0). The register lists
        to set (set_regs) and to reset (reset_regs) are read from the config file.
        """
        print 'Setting registers:'
        for reg in self.settings.set_regs:
            self.set_reg(reg['name'], reg['val'])
            
        print 'Resetting registers:'
        for reg in self.settings.reset_regs:
            self.reset_reg(reg)

        print 'Done setting and reseting registers'

    def set_reg(self, reg, val, verbose=True):
        """
        Set a register.
        :param reg: register name in the FPGA model.
        :param val: value to set the register.
        """
        if verbose:
            print '\tSetting %s to %i... ' %(reg, val)
        self.fpga.write_int(reg, val)
        time.sleep(0.1)
        if verbose:
            print '\tdone'

    def reset_reg(self, reg):
        """
        Reset a register (->1->0).
        :param reg: register name in the FPGA model.
        """
        print '\tResetting %s... ' %reg
        self.fpga.write_int(reg, 1)
        time.sleep(0.1)
        self.fpga.write_int(reg, 0)
        time.sleep(0.1)
        print '\tdone'

    def listbof(self):
        """
        List .bof files availables in ROACH memory.
        """
        print "BOF files:"
        print self.fpga.listbof()

    def listdev(self):
        """
        List FPGA available registers and brams.
        """
        print "Registers and brams:"
        print self.fpga.listdev()

    def read_reg(self, reg):
        """
        Read a register.
        :param reg: register name in the FPGA model.
        :return: value of the register read in unsigned 32 bit format.
        """
        reg_val = self.fpga.read_uint(reg)
        return reg_val

    def get_reg_list_data(self, reg_name_list):
        """
        Get the register value of a list of register names.
        :param reg_name_list: list of register names.
        :return: list of register values in unsigned 32 bit format.
        """
        reg_val_list = []
        for reg_name in reg_name_list:
            reg_val_list.append(self.read_reg(reg_name))

        return np.array(reg_val_list)

    def get_snapshots(self, nsamples=None):
        """
        Get snapshot data from all snapshot blocks specified in the config 
        file (snapshots).
        :param nsamples: number of samples of the snapshot to return. Usually used
            to get the desired number of samples for a nice plot.
        :return: list of data arrays in the same order as the snapshot list. Note: the
            data type is fixed to 8 bits as all of our ADC work at that size. 
        """
        snap_data_arr = []
        for snapshot in self.settings.snapshots:
            snap_data = np.fromstring(self.fpga.snapshot_get(snapshot, man_trig=True, 
                man_valid=True)['data'], dtype='>i1')
            snap_data = snap_data[:nsamples]
            snap_data_arr.append(snap_data)
        
        return snap_data_arr

    def get_snapshots_sync(self, nsamples=None):
        """
        Same as get_snapshots() but it uses a 'snapshot trigger' register to sync
        the snapshot recording, i.e., all snapshot start recording at the same clock cycle.
        :return: list of data arrays in the same order as the snapshot list.
        """
        # reset snapshot trigger form initial state 
        self.fpga.write_int('snap_trig', 0)
        
        # activate snapshots to get data
        for snapshot in self.settings.snapshots:
            self.fpga.write_int(snapshot + '_ctrl', 0)
            self.fpga.write_int(snapshot + '_ctrl', 1)
        
        # activate the trigger to start recording in all snapshots at the same time 
        self.fpga.write_int('snap_trig', 1)
        
        # get data without activating a new recording (arm=False)
        snap_data_arr = []
        for snapshot in self.settings.snapshots:
            snap_data = np.fromstring(self.fpga.snapshot_get(snapshot, arm=False)['data'], dtype='>i1')
            snap_data = snap_data[:nsamples]
            snap_data_arr.append(snap_data)
        
        return snap_data_arr

    def get_bram_data(self, bram_info):
        """
        Receive and unpack data from FPGA using data information from bram_info.
        :param bram_info: dictionary with the info from the bram.
            The bram_info dictionary format is:
            {'addr_width'  : width of bram address in bits.
             'word_width'  : width of bram word in bits.
             'data_type'   : Numpy datatype object or string of the of the resulting data.
                 See https://docs.scipy.org/doc/numpy/reference/arrays.dtypes.html
             'bram_names'  : bram name of bram names in the model
            }
        :return: numpy array with the bram data (if single bram name), 
            or list of numpy arrays following the same structure as the 'bram_names' list.
        """
        brams = bram_info['bram_names']

        if isinstance(brams, str): # case single bram 
            width = bram_info['word_width']
            depth = 2**bram_info['addr_width']
            dtype = bram_info['data_type'] 
            
            return np.frombuffer(self.fpga.read(brams, depth*width/8, 0), dtype=dtype)
        
        elif isinstance(brams, list): # case bram list
            bram_data_list = []
            for bram_name in bram_info['bram_names']:
                new_bram_info = bram_info.copy()
                new_bram_info['bram_names'] = bram_name
                new_bram_data = self.get_bram_data(new_bram_info)
                bram_data_list.append(new_bram_data)

            return bram_data_list

    def get_bram_data_interleave(self, bram_info):
        """
        Uses get_bram_data to acquire data from bram FPGA, and
        also handles data that is interleaved or denterleaved in
        the brams, combinding it, or separating it accordingly. 
        The interleaved nature of the data is obtained from the bram_info 
        (checking the 'interleave' and 'deinterleaved_by' keys).
        :param bram_info: dictionary with the info from the bram. Same as
            the get_bram_data param.
        :return: numpy array or list of numpy arrays with the 
            interleaved/deinterleaved data.
        """
        bram_data = self.get_bram_data(bram_info)

        # manage interleave/deinterleave data
        if 'interleave' in bram_info and bram_info['interleave']==True:
            bram_data = interleave_array_list(bram_data, bram_info['data_type'])
        elif 'deinterleave_by' in bram_info:
            bram_data = deinterleave_array_list(bram_data, bram_info['deinterleave_by'])
            bram_data = list(chain.from_iterable(bram_data)) # flatten list

        return bram_data

    def get_bram_data_sync(self, bram_info):
        """
        Get bram data by issuing a request to FPGA and waiting for the data
        to be ready to read. Useful when need to get spectral data with an
        specific input condition controlled by a script.
        :param bram_info: dictionary with the info of the brams. 
            The dictionary format must be the same as for get_bram_data_interleave,
            with the additional keys 'req_reg and 'read_count_reg' with the name
            of the register that control the synchronization of data: 
                - req_reg: register used for data request.
                    is set 0->1 to request new data.
                    is set 1->0 to inform that data read finished.
                - read_count_reg: register is increased by 1 by the FPGA when the data 
                is ready to read.
        :return: data on FPGA brams.
        """
        # read the current value of the count reg to check later
        count_val = self.read_reg(bram_info['read_count_reg'])

        # request data
        self.set_reg(bram_info['req_reg'], 0, verbose=False)
        self.set_reg(bram_info['req_reg'], 1, verbose=False)

        # wait until data if ready to read
        while True:
            # np.uint32 is to deal with overfolw in 32-bit registers
            if np.uint32(self.read_reg(bram_info['read_count_reg']) - count_val) == 1: 
                break

        return self.get_bram_data_interleave(bram_info)

    def write_bram_data(self, bram_info, data):
        """
        Write and array of data into the FPGA using data information from bram_info.
        :param bram_info: dictionary with the info from the bram. The dictionary format is the
            same as for get_bram_data().
        :param data: array to write on the bram.
        """
        brams = bram_info['bram_names']
        
        if isinstance(brams, str): # case single bram
            width = bram_info['word_width']
            depth = 2**bram_info['addr_width']
            dtype = bram_info['data_type'] 
            # check for bram-data datatype compatibility
            if dtype != data.dtype:
                print "WARNING! data types between write bram and data don't match."
                print "bram dtype: " + str(dtype)
                print "data dtype: " + str(data.dtype)
                print "Attempting to write in bram anyway."

            # check for bytesize compatibility
            bram_bytes = width * depth / 8
            data_bytes = len(data) * data.dtype.alignment
            if bram_bytes != data_bytes:
                print "WARNING! number of bytes between write bram and data don't match."
                print "bram bytes: " + str(bram_bytes)
                print "data bytes: " + str(data_byes)
                print "Attempting to write in bram anyway."
            
            self.fpga.write(bram, data.tobytes())
            return

        elif isinstance(brams, list): # case bram list
            for bram_name, data_item in zip(bram_info['bram_names'], data):
                new_bram_info = bram_info.copy()
                new_bram_info['bram_names'] = bram_name
                self.write_bram_data(new_bram_info, data_item)

    def get_dram_data(self, dram_info):
        """
        Retreive and unpack data from ROACH's DRAM using data information form dram_info.
        :param dram_info: dictionary with the info from the dram.
            The dram_info dictionary format is:
            {'addr_width'  : width of dram address in bits.
             'word_width'  : width of dram word in bits.
             'data_type'   : Numpy datatype object or string of the of the resulting data.
                 See https://docs.scipy.org/doc/numpy/reference/arrays.dtypes.html
            }
        :return: numpy array with the dram data.
        """
        width = dram_info['word_width']
        depth = 2**dram_info['addr_width']
        dtype = dram_info['data_type'] 
        
        # read dram data in blocks of 2**18 words (2**22 bytes) to avoid read timeouts
        block_bytes = 2**22
        dram_bytes = depth*width/8
        n_blocks = int(np.ceil(float(dram_bytes) / block_bytes))
        dram_data = np.array([])
        print "Reading DRAM data..."
        for i in range(n_blocks):
            curr_block_bytes = min(block_bytes, dram_bytes-i*block_bytes)
            block_data = np.frombuffer(self.fpga.read_dram(curr_block_bytes, i*block_bytes), dtype=dtype)
            dram_data = np.hstack((dram_data, block_data))
        print "done"

        return dram_data

def interleave_array_list(array_list, dtype):
    """
    Receivers a list of unknown depth with the final elements
    being numpy arrays. Interleave the arrays in the inner most
    lists. It assumes that all the sub lists are of the same depth.
    Useful to combine spectral data separated in diferent brams.
    Examples (parenthesis signifies numpy array):

    - [(1,2,3,4),(10,20,30,40)] -> (1,10,2,20,3,30,4,40)
    
    - [[(1,2,3,4),(5,6,7,8)] , [(10,20,30,40),(50,60,70,80)]]
        -> [(1,5,2,6,3,7,4,8), (10,50,20,60,30,70,40,80)]

    :param array_list: list to interleave.
    :param dtype: numpy data type of arrays.
    :return: new list with with inner most list interleaved.
    """
    if isinstance(array_list[0], np.ndarray): # case list of arrays
        return np.fromiter(chain(*zip(*array_list)), dtype=dtype)
    
    elif isinstance(array_list[0], list): # case deeper list
        interleaved_list = []
        for inner_list in array_list:
            interleaved_inner_list = interleave_array_list(inner_list, dtype)
            interleaved_list.append(interleaved_inner_list)
        return interleaved_list

def deinterleave_array_list(array_list, ifactor):
    """
    Receivers a list of unknown depth with the final elements
    being numpy arrays. For every array, separate the array in a
    list of ifactor arrays so that the original array is the interleaved 
    version of the produced arrays. This is the inverse function of
    interleave_array_list(). Useful when independent spectral data is
    saved in the same bram in an interleaved manner.
    :param array_list: array or list to deinterleave.
    :param ifactor: interleave factor, number of arrays in which to separate
        the original array.
    :return: list with the deinterleaved arrays.
    """
    if isinstance(array_list, np.ndarray): # case array
        deinterleaved_list = np.reshape(array_list, (len(array_list)/ifactor, ifactor))
        deinterleaved_list = np.transpose(deinterleaved_list)
        deinterleaved_list = list(deinterleaved_list)
        return deinterleaved_list

    if isinstance(array_list, list): # case list
        deinterleaved_list = []
        for inner_list in array_list:
            deinterleaved_inner_list = deinterleave_array_list(inner_list, ifactor)
            deinterleaved_list.append(deinterleaved_inner_list)
        return deinterleaved_list
