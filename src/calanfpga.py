import sys, os, importlib, time
import numpy as np
from itertools import chain
import corr
from dummies.dummy_fpga import DummyFpga
import qdr

class CalanFpga():
    """
    Wrapper around corr's FpgaClient in order to add common functions used in 
    Calan Lab (Millimeter Wave Laboratory, Univerity of Chile). Examples of the
    funtions added are: roach initialization, regiter setting/reseting, easy 
    data grab from multiple snapshots, bram arrays, interleave bram arrays, 
    etc.
    """
    def __init__(self):
        """
        Initialize the CalanFpga object. You must specify the config file as
        the second argument in the command-line arguments.
        """
        if len(sys.argv) <= 1:
            print("Please provide a config file as a command line argument: " +
                os.path.basename(sys.argv[0]) + " [config file]")  
            exit()
        config_file = os.path.splitext(sys.argv[1])[0]
        try:
            self.settings = importlib.import_module(config_file)
        except ImportError:
            print("Error: No config file named " + config_file)
            exit()
        
        if len(sys.argv) > 2:
            self.parse_commandline_args(sys.argv[2:])

        if self.settings.simulated:
            self.fpga = DummyFpga(self.settings)
        else:
            self.fpga = corr.katcp_wrapper.FpgaClient(self.settings.roach_ip, 
                self.settings.roach_port)
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
            For example: 
            "spectra_animator.py spectra_config.py --boffile newmodel.bof.gz"
        """
        if len(arg_list) % 2 == 1:
            print("Error. The number of additional command line arguments" \
                "must be even.")
            exit()

        for attrname, attrval in zip(arg_list[0::2], arg_list[1::2]):
            if attrname[0:2] != "--":
                print("Error in command line " + attrname + 
                    ". Use double dash '--' at the begining of attributes" \
                    "names in command line")
                exit()
                
            # try to evaluate attribute value, 
            #if fails keep the value as a string.
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
        elif self.settings.upload:
            print "Upload bof without programming it is not supported."
            exit()

        # check if qdr is used
        if hasattr(self.settings, 'qdr'):
            self.calibrate_qdr(self.settings.qdr)

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
        Program the .bof/.bof.gz model specified in the config file (boffile)
        to the FPGA.
        """
        print 'Programming FPGA with ' + self.settings.boffile + '...'
        self.fpga.progdev(os.path.basename(self.settings.boffile))
        time.sleep(1)
        print 'done'

    def upload_program_fpga(self):
        """
        Upload the .bof/.bof.gz model specified in the config file (boffile)
        to ROACH memory and program FPGA with this model. 
        Note: this don't work in ROACH1.
        """
        print 'Uploading and programming FPGA with ' + \
            self.settings.boffile + '...'
        self.fpga.upload_program_bof(self.settings.boffile, 3000)
        time.sleep(1)
        print 'done'

    def estimate_clock(self):
        """
        Estimate FPGA clock.
        """
        print 'Estimating FPGA clock:'
        try:
            clock = self.fpga.est_brd_clk()
        except RuntimeError:
            print "Unable to get ROACH clock."
            print "Did you forget to program the FPGA with a .bof file?"
            exit()
        print str(clock) + '[MHz]'

    def set_reset_regs(self):
        """
        Set registers to a given value and reset registers (->1->0). The 
        register lists to set (set_regs) and to reset (reset_regs) are read 
        from the config file.
        """
        print 'Setting registers:'
        for reg in self.settings.set_regs:
            self.set_reg(reg['name'], reg['val'])
            
        print 'Resetting registers:'
        self.reset_regs(self.settings.reset_regs)
        print 'Done setting and reseting registers'

    def set_reg(self, reg, val, verbose=True):
        """
        Set a register.
        :param reg: register name in the FPGA model.
        :param val: value to set the register.
        :param verbose: True: be verbose.
        """
        if verbose:
            print '\tSetting %s to %i... ' %(reg, val)
        self.fpga.write_int(reg, val)
        if verbose:
            print '\tdone'
    
    def reset_regs(self, regs, verbose=True):
        """
        Reset a list of registers.
        :param: register list.
        :param: verbose: True: be verbose.
        """
        for reg in regs:
            self.reset_reg(reg, verbose)

    def reset_reg(self, reg, verbose=True):
        """
        Reset a register (->1->0).
        :param reg: register name in the FPGA model.
        :param verbose: True: be verbose.
        """
        if verbose:
            print '\tResetting %s... ' %reg
        self.fpga.write_int(reg, 1)
        self.fpga.write_int(reg, 0)
        if verbose:
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
        :param nsamples: number of samples of the snapshot to return. 
            Usually used to get the desired number of samples for a nice plot.
        :return: list of data arrays in the same order as the snapshot list. 
            Note: the data type is fixed to 8 bits as all of our ADC work at 
            that size. 
        """
        snap_data_arr = []
        for snapshot in self.settings.snapshots:
            snap_data = np.fromstring(self.fpga.snapshot_get(snapshot, 
            man_trig=True, man_valid=True)['data'], dtype='>i1')
            snap_data = snap_data[:nsamples]
            snap_data_arr.append(snap_data)
        
        return snap_data_arr

    def get_snapshots_sync(self, nsamples=None):
        """
        Same as get_snapshots() but it uses a 'snapshot trigger' register 
        to sync the snapshot recording, i.e., all snapshot start recording at 
        the same clock cycle.
        :return: list of data arrays in the same order as the snapshot list.
        """
        # reset snapshot trigger form initial state 
        self.fpga.write_int('snap_trig', 0)
        
        # activate snapshots to get data
        for snapshot in self.settings.snapshots:
            self.reset_reg(snapshot + '_ctrl', verbose=False)
        
        # activate the trigger to start recording in all snapshots 
        # at the same time 
        self.fpga.write_int('snap_trig', 1)
        
        # get data without activating a new recording (arm=False)
        snap_data_arr = []
        for snapshot in self.settings.snapshots:
            snap_data = np.fromstring(
                self.fpga.snapshot_get(snapshot, arm=False)['data'], 
                dtype='>i1')
            snap_data = snap_data[:nsamples]
            snap_data_arr.append(snap_data)
        
        return snap_data_arr

    def get_bram_data_raw(self, bram_info):
        """
        Receive and unpack data from FPGA using data information 
        from bram_info.
        :param bram_info: dictionary with the info from the bram.
            The bram_info dictionary format is:
            {'addr_width'  : width of bram address in bits.
             'word_width'  : width of bram word in bits.
             'data_type'   : Numpy datatype object or string of the of the 
                 resulting data.
                 See https://docs.scipy.org/doc/numpy/reference/arrays.dtypes.html
             'bram_names'  : bram name of bram names in the model
            }
        :return: numpy array with the bram data (if single bram name), 
            or list of numpy arrays following the same structure as the 
            'bram_names' list.
        """
        brams = bram_info['bram_names']

        if isinstance(brams, str): # case single bram 
            width = bram_info['word_width']
            depth = 2**bram_info['addr_width']
            dtype = bram_info['data_type'] 
            
            return np.frombuffer(self.fpga.read(brams, depth*width/8, 0), 
                dtype=dtype)
        
        elif isinstance(brams, list): # case bram list
            bram_data_list = []
            for bram_name in bram_info['bram_names']:
                new_bram_info = bram_info.copy()
                new_bram_info['bram_names'] = bram_name
                new_bram_data = self.get_bram_data_raw(new_bram_info)
                bram_data_list.append(new_bram_data)

            return bram_data_list

    def get_bram_data(self, bram_info):
        """
        Uses get_bram_data to acquire data from bram FPGA, and
        also handles data that is interleaved, denterleaved or divided in
        the brams, combinding it, or separating it accordingly. 
        The interleaved nature of the data is obtained from the bram_info 
        (checking the 'interleave', 'deinterleaved_by' and 'divided_by' keys).
        :param bram_info: dictionary with the info from the bram. Same as
            the get_bram_data param.
        :return: numpy array or list of numpy arrays with the 
            interleaved/deinterleaved data.
        """
        bram_data = self.get_bram_data_raw(bram_info)

        # manage interleave/deinterleave data
        if 'interleave' in bram_info and bram_info['interleave']==True:
            bram_data = interleave_array(bram_data)
        
        elif 'deinterleave_by' in bram_info:
            bram_data = deinterleave_array(bram_data, bram_info['deinterleave_by'])
            bram_data = list(chain.from_iterable(bram_data)) # flatten list

        elif 'divide_by' in bram_info:
            bram_data = divide_array(bram_data, bram_info['divide_by'])
            bram_data = list(chain.from_iterable(bram_data)) # flatten list

        return bram_data

    def get_bram_data_sync(self, bram_info):
        """
        Get bram data by issuing a request to FPGA and waiting for the data
        to be ready to read. Useful when need to get spectral data with an
        specific input condition controlled by a script.
        :param bram_info: dictionary with the info of the brams. 
            The dictionary format must be the same as for 
            get_bram_data, with the additional keys 'req_reg and 
            'read_count_reg' with the name
            of the register that control the synchronization of data: 
                - req_reg: register used for data request.
                    is set 0->1 to request new data.
                    is set 1->0 to inform that data read finished.
                - read_count_reg: register is increased by 1 by the FPGA 
                when the data is ready to read.
        :return: data on FPGA brams.
        """
        # read the current value of the count reg to check later
        count_val = self.read_reg(bram_info['read_count_reg'])

        # request data
        self.reset_reg(bram_info['req_reg'], verbose=False)

        # wait until data if ready to read
        while True:
            # np.uint32 is to deal with overfolw in 32-bit registers
            if np.uint32(self.read_reg(bram_info['read_count_reg']) - count_val) == 1: 
                break

        return self.get_bram_data(bram_info)

    def write_bram_data_raw(self, bram_info, data):
        """
        Write and array of data into the FPGA using data information 
        from bram_info.
        :param bram_info: dictionary with the info from the bram. 
        The dictionary format is the same as for get_bram_data().
        :param data: array to write on the bram.
        """
        brams = bram_info['bram_names']
        check_brams_data_sizes(brams, data)
        
        if isinstance(brams, str): # case single bram
            width = bram_info['word_width']
            depth = 2**bram_info['addr_width']
            dtype = np.dtype(bram_info['data_type'])

            # check for bytesize compatibility
            bram_bytes = width * depth / 8
            data_bytes = len(data) * data.dtype.alignment
            if bram_bytes != data_bytes:
                print "WARNING! number of bytes between write bram and data don't match."
                print "bram bytes: " + str(bram_bytes)
                print "data bytes: " + str(data_bytes)
                print "Attempting to write in bram anyway."
            
            # change the data to the correct data type
            data = data.astype(dtype)

            self.fpga.write(brams, data.tobytes())
            return

        elif isinstance(brams, list): # case bram list
            for bram_name, data_item in zip(bram_info['bram_names'], data):
                new_bram_info = bram_info.copy()
                new_bram_info['bram_names'] = bram_name
                self.write_bram_data_raw(new_bram_info, data_item)

    def write_bram_data(self, bram_info, data):
        """
        Interleaves or deinterleaves data and then writes it to
        the FPGA using write_bram_data_raw.
        The interleaved nature of the data is obtained from the bram_info 
        (checking the 'interleave' and 'deinterleaved_by' keys).
        :param bram_info: dictionary with the info from the bram. Same as
            the get_bram_data param.
        :param data: numpy array or list of numpy arrays with the 
            interleaved/deinterleaved data.
        """
        # manage interleave/deinterleave data
        if 'interleave' in bram_info and bram_info['interleave']==True:
            data = interleave_array(data, bram_info['data_type'])
        elif 'deinterleave_by' in bram_info:
            data = deinterleave_array(data, bram_info['deinterleave_by'])

        self.write_bram_data_raw(bram_info, data)

    def write_dram_data(self, dram_info):
        """
        Retreive and unpack data from ROACH's DRAM using data information 
        from dram_info.
        :param dram_info: dictionary with the info from the dram.
            The dram_info dictionary format is:
            {'addr_width'  : width of dram address in bits.
             'word_width'  : width of dram word in bits.
             'data_type'   : Numpy datatype object or string of the of the 
                 resulting data.
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
            block_data = np.frombuffer(self.fpga.read_dram(curr_block_bytes, 
                i*block_bytes), dtype=dtype)
            dram_data = np.hstack((dram_data, block_data))
        print "done"

        return dram_data

    def calibrate_qdr(self, qdr_name):
        """
        Calibrate QDR with the CASPER script.
        :param qdr_name: string name of the qdr to calibrate.
        """
        print "Calibrating QDR..."
        my_qdr = qdr.Qdr(self.fpga, qdr_name)
        my_qdr.qdr_cal(fail_hard=True, verbosity=1)
        time.sleep(0.1)
        print "done"
        

def interleave_array(a):
    """
    Receives an array of unknown depth. Interleave the array inner most
    dimension. The result is an array of one less dimension.
    Useful to combine spectral data separated in diferent brams.
    Examples:
    - ((1,2,3,4),(10,20,30,40)) -> (1,10,2,20,3,30,4,40)
    
    - (((1,2,3,4),(5,6,7,8)) , ((10,20,30,40),(50,60,70,80)))
        -> ((1,5,2,6,3,7,4,8), (10,50,20,60,30,70,40,80))

    :param a: array to interleave (can be a list).
    :return: new array with with inner most dimension interleaved.
    """
    a = np.array(a)
    newshape = a.shape[:-2] + (a.shape[-2]*a.shape[-1],)
    return np.reshape(a, newshape, order='F')

def deinterleave_array(a, i):
    """
    Receives an array of unknown depth. Separate the inner most dimension 
    of the array so that it produces a new dimension of i arrays where the 
    original dimension was the interleaved version of the new ones. 
    This is the inverse function of interleave_array(). Useful when independent
    spectral data is saved in the same bram in an interleaved manner.
    :param a: array to deinterleave (can be a list).
    :param i: interleave factor, number of arrays in which to separate
        the array last dimension.
    :return: array with the deinterleaved data.
    """
    a = np.array(a)
    newshape = a.shape[:-1] + (a.shape[-1]/i,i)
    a = np.reshape(a, newshape)
    axes = range(len(a.shape))
    newaxes = axes[:-2] + [axes[-1]] + [axes[-2]]
    return np.transpose(a, newaxes)

def divide_array(a, i):
    """
    Receives an array of unknown depth. Separate the inner most dimension 
    of the array so that it produces a new dimension of i arrays where the 
    where the ne simension is the direct separation of the original dimension.
    Useful when independent spectral data is produces secuentially and saved in
    the same memory.
    Examples:
    - (1,2,3,4,10,20,30,40) -> ((1,2,3,4), (10,20,30,40))
    
    - ((1,2,3,4,5,6,7,8) , (10,20,30,40,50,60,70,80))
        -> (((1,2,3,4),(5,6,7,8)), ((10,20,30,40),(50,60,70,80)))

    :param array_list: array or list to divide.
    :param dfactor: divide factor, number of arrays in which to separate
        the original array.
    :return: list with the divided arrays.
    """
    a = np.array(a)
    newshape = a.shape[:-1] + (i,a.shape[-1]/i)
    return np.reshape(a, newshape)

def check_brams_data_sizes(brams, data):
    """
    Check that the dimensions of the data and the dimensions
    of the list of bram names match. If they don't match, close
    the script.
    :param brams: multidimensial list with bram names to write.
    :param data: multidimensional array of data to write.
    """
    brams_arr = np.array(brams)
    if brams_arr.shape != data.shape[:-1]:
        print "ERROR: mismatch between dimensions of brams list and data array"
        print "bram list  dimensions: " + str(brams_arr.shape)
        print "data array dimensions: " + str(data.shape[:-1])
        exit()
