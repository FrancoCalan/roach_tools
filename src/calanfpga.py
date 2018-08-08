import sys, os, importlib, time
import numpy as np
from itertools import chain
import corr, adc5g
from dummies.dummy_fpga import DummyFpga

class CalanFpga():
    """
    Wrapper around corr's FpgaClient in order to add common functions used in 
    Calan Lab (Millimeter Wave Laboratory, Univerity of Chile). Examples of the
    funtions added are: roach initialization, regiter setting/reseting, easy data
    grab from multiple snapshots, bram arrays, interleaved bram arrays, etc.
    """
    def __init__(self):
        """
        Initialize the CalanFpga object. You must specify the config file as the
        second argument in the command-line arguments.
        """
        if len(sys.argv) <= 1:
            raise RuntimeError("Please provide a config file as a command line argument: " + os.path.basename(sys.argv[0]) + " [config file]")  
        config_file = os.path.splitext(sys.argv[1])[0]
        self.settings = importlib.import_module(config_file)
        if self.settings.simulated:
            self.fpga = DummyFpga(self.settings)
        else:
            self.fpga = corr.katcp_wrapper.FpgaClient(self.settings.roach_ip, self.settings.roach_port)
            time.sleep(1)

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
            raise Exception('Unable to connect to ROACH.')

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

    def set_reg(self, reg, val):
        """
        Set a register.
        :param reg: register name in the FPGA model.
        :param val: value to set the register.
        """
        print '\tSetting %s to %i... ' %(reg, val)
        self.fpga.write_int(reg, val)
        time.sleep(0.1)
        print 'done'

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
        print 'done'

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

    def calibrate_adcs(self):
        """
        Calibrate adcs using external calibration routines.
        """
        # Hardcoded ADC5G calibration
        for snap_data in self.settings.snapshots:
            adc5g.set_test_mode(self.fpga, snap_data['zdok'])
        adc5g.sync_adc(self.fpga)

        for snap_data in self.settings.snapshots:
            print "Calibrating ADC5G ZDOK" + str(snap_data['zdok']) + "..."
            opt, glitches = adc5g.calibrate_mmcm_phase(self.fpga, \
                snap_data['zdok'], snap_data['names'])

            print "done"
            adc5g.unset_test_mode(self.fpga, snap_data['zdok'])

    def get_snapshot_names(self):
        """
        Get snapshot names from snapshots setting format:
            {'zdok' : adc zdok input number,
             'names' : list of snapshots associated to that ADC.}
        """
        snapshots = []
        for snap_data in self.settings.snapshots:
            snapshots += snap_data['names']

        return snapshots

    def get_snapshots(self):
        """
        Get snapshot data from all snapshot blocks specified in the config 
        file (snapshots).
        :return: list of data arrays in the same order as the snapshot list. Note: the
        data type is fixed to 8 bits as all of our ADC work at that size. 
        """
        snap_data_arr = []
        for snapshot in self.get_snapshot_names():
            snap_data = np.fromstring(self.fpga.snapshot_get(snapshot, man_trig=True, 
                man_valid=True)['data'], dtype='>i1')
            snap_data_arr.append(snap_data)
        
        return snap_data_arr

    def get_snapshots_sync(self):
        """
        Same as get_snapshots() but it uses a 'snapshot trigger' register to sync
        the snapshot recording, i.e., all snapshot start recording at the same clock cycle.
        :return: list of data arrays in the same order as the snapshot list.
        """
        # reset snapshot trigger form initial state 
        self.fpga.write_int('snap_trig', 0)
        
        # activate snapshots to get data
        for snapshot in self.get_snapshot_names():
            self.fpga.write_int(snapshot + '_ctrl', 0)
            self.fpga.write_int(snapshot + '_ctrl', 1)
        
        # activate the trigger to start recording in all snapshots at the same time 
        self.fpga.write_int('snap_trig', 1)
        
        # get data without activating a new recording (arm=False)
        snap_data_arr = []
        for snapshot in self.get_snapshot_names():
            snap_data = np.fromstring(self.fpga.snapshot_get(snapshot, arm=False)['data'], dtype='>i1')
            snap_data_arr.append(snap_data)
        
        return snap_data_arr

    def get_bram_data(self, bram_info):
        """
        Receive and unpack data from FPGA using data information from bram_info.
        :param bram_info: dictionary with the info from the bram.
            The bram_info dictionary format is:
            {'addr_width'  : width of bram address in bits.
             'data_width'  : width of bram data (word) in bits.
             'sign_type'   : 'u' unsigned, 'i': signed
             'bram_name'   : bram name in the model
            }
        :return: numpy array with the bram data.
        """
        width = bram_info['data_width']
        depth = 2**bram_info['addr_width']
        sign  = bram_info['sign_type'] 
        bram  = bram_info['bram_name']

        bram_data = np.fromstring(self.fpga.read(bram, depth*width/8, 0), dtype='>'+sign+str(width/8))
        return bram_data

    def get_bram_list_data(self, bram_info):
        """
        Similar to get_bram_data but it gets the data from a list of bram with the 
        same parameters. In this case 'bram_name' is 'bram_list', a list of bram names.
        :param bram_info: dictionary with the info of the brams. 
            The bram_info dictionary format is:
            {'addr_width'  : width of brams addresses in bits.
             'data_width'  : width of brams data (word) in bits.
             'sign_type'   : 'u' unsigned, 'i': signed
             'bram_list'   : list of bram names in the model
            }
        :return: list of numpy arrays with the data of every bram in the same order.
        """
        bram_data_arr = []
        for bram in bram_info['bram_list']:
            # make a new bram info only with current bram
            current_bram_info = bram_info.copy()
            current_bram_info['bram_name'] = bram
            bram_data = self.get_bram_data(current_bram_info)
            bram_data_arr.append(bram_data)

        return bram_data_arr

    def get_bram_list2d_data(self, bram_info):
        """
        Similar to get_bram_list_data but it gets the data from a list of lists of brams.
        In this case 'bram_list' is 'bram_list2d', a 2d list of bram names.
        :param bram_info: dictionary with the info of the brams. 
            The bram_info dictionary format is:
            {'addr_width'  : width of brams addresses in bits.
             'data_width'  : width of brams data (word) in bits.
             'sign_type'   : 'u' unsigned, 'i': signed
             'bram_list2d' : list of lists of bram names in the model
            }
        :return: list of lists of numpy arrays with the data of every bram in the 
            same order.
        """
        bram_data_arr2d = []
        for bram_list in bram_info['bram_list2d']:
            # make a new bram info only with current bram_list
            current_bram_info = bram_info.copy()
            current_bram_info['bram_list'] = bram_list
            bram_data_arr = self.get_bram_list_data(current_bram_info)
            bram_data_arr2d.append(bram_data_arr)

        return bram_data_arr2d

    def get_bram_interleaved_data(self, bram_info):
        """
        Get data using get_bram_list_data and then interleave the data. Useful for easily 
        getting data from a spectrometer that uses multi-channel FFT.
        :param bram_info: dictionary with the info of the brams. The format is the same
            as for get_bram_list_data().
        :return: numpy array with the data of the brams interlieved using the order of the
            bram_list.
        """
        width = bram_info['data_width']
        bram_data_arr = self.get_bram_list_data(bram_info)
        interleaved_data = np.fromiter(chain(*zip(*bram_data_arr)), dtype='>'+bram_info['sign_type']+str(width/8))
        return interleaved_data

    def get_bram_list_interleaved_data(self, bram_info):
        """
        Get data using get_bram_list2d_data and then interleave the data from 
        the inner lists. Useful to easily get data from multiple spectrometers implemented
        in the same FPGA, and with the same data type.
        :param bram_info: dictionary with the info of the brams. The format is the same
            as for get_bram_list2d_data().
        :return: list of numpy arrays with the data of the brams of the inner lists
            interlieved.
        """
        interleaved_data_arr = []
        for bram_list in bram_info['bram_list2d']:
            # make a new bram info only with current bram_list
            current_bram_info = bram_info.copy()
            current_bram_info['bram_list'] = bram_list
            interleaved_data = self.get_bram_interleaved_data(current_bram_info)
            interleaved_data_arr.append(interleaved_data)

        return interleaved_data_arr

    def get_bram_sync_data(self, bram_info, read_funct, req_reg, readok_reg):
        """
        Get bram data but issuing a request to FPGA and waiting for the data
        to be ready to read. Useful when need to get spectral data with an
        specific input condition controlled by a script.
        :param bram_info: dictionary with the info of the brams. The bram format
            must be valid for the read_funct.
        :param read_funct: read function to read the data from brams (ex. get_bram_data,
            get_bram_list_data)
        :param req_reg: register used for data request.
            is set 0->1 to request new data.
            is set 1->0 to inform that data read finished.
        :param readok_reg: register is set by the FPGA when the data is ready to read.
            When 0 data not ready to read.
            When 1 data is ready to read.
            This register should be reset by the FPGA when req_reg 1->0.
        """
        if self.read_reg(req_reg) != 0:
            print "WARNING: attempt to sync read brams when request reg is not zero."
            print "Sync read failed."
            return

        # request new bram data
        print "WWW"
        print "readok: " + str(self.read_reg(readok_reg))
        self.set_reg(req_reg, 1)
        print "readok: " + str(self.read_reg(readok_reg))

        # wait for read ok register to report valid data to read
        while True:
            if self.read_reg(readok_reg) == 1:
                break
            print "AAA"

        print "XXX"
        # read data
        read_data = read_funct(bram_info)

        # inform read data finished
        self.set_reg(req_reg, 0)
        print "readok: " + str(self.read_reg(readok_reg))

        return read_data

    def write_bram_data(self, bram_info, data):
        """
        Write and array of data into the FPGA using data information from bram_info.
        :param bram_info: dictionary with the info from the bram. The dictionary format is the
            same as for get_bram_data().
        :param data: array to write on the bram.
        """
        bram  = bram_info['bram_name']
        bram_dtype = np.dtype('>'+bram_info['sign_type']+str(bram_info['data_width']/8))

        if bram_dtype != data.dtype:
            print "WARNING! data types between write bram and data don't match."
            print "bram dtype: " + str(bram_dtype)
            print "data dtype: " + str(bram_dtype)
            print "Attempting to write in bram anyway."
        
        self.fpga.write(bram, data.tobytes())

    def write_bram_list_data(self, bram_info, data_list):
        """
        Similar to write_bram_data but it receives a list of data arrays, and write it into 
        a list of brams. In this case 'bram_name' is 'bram_list', a list of bram names.
        :param bram_info: dictionary with the info of the brams. The dictionary format is the
            same as for get_bram_list_data().
        :param data_list: list of data array to write on the brams.
        """
        for bram, data in zip(bram_info['bram_list'], data_list):
            # make a new bram info only with current bram
            current_bram_info = bram_info.copy()
            current_bram_info['bram_name'] = bram
            self.write_bram_data(current_bram_info, data)

    def write_bram_list2d_data(self, bram_info, data_list2d):
        """
        Similar to write_bram_list2d_data but it receives a list of list of data arrays, 
        and write them into a list of list of brams. In this case 'bram_list' is 'bram_list2d', 
        a 2d list of bram names.
        :param bram_info: dictionary with the info of the brams. The dictionary format is the
            same as for get_bram_list2d_data().
        :param data_list2d: list of list data array to write on the brams.
        """
        for bram_list, data_list in zip(bram_info['bram_list2d'], data_list2d):
            # make a new bram info only with current bram_list
            current_bram_info = bram_info.copy()
            current_bram_info['bram_list'] = bram_list
            self.write_bram_list_data(current_bram_info)
