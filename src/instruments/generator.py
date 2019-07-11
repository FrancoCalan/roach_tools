import vxi11, socket

class Generator():
    """
    Generic class to control signal generators.
    """
    def __init__(self, instr, instr_info): 
        self.instr = instr
        self.sleep_time = 0.1
        try:
            self.def_freq = instr_info['def_freq']
        except KeyError:
            self.def_freq = 10
        try:
            self.def_power = instr_info['def_power']
        except KeyError:
            self.def_power = -100

        # set multiplier for the displayed frequency
        if 'freq_mult' in instr_info:
            freq_mult = instr_info['freq_mult']
            self.set_freq_mult(freq_mult)

        # set default parameters
        #self.set_freq_mhz()
        #self.set_power_dbm()
        
    def close_connection(self):
        self.instr.close()

def create_generator(instr_info):
    """
    Create the appropiate generator object given the instr_info
    dictionary.
    :param instr_info: generator instrument info dictionary.
        The instr_info format is:
        {'instr_type' : type of generator, defined by the 
            command keywords.
         'connection' : type of connection in Visa format.
            See https://pyvisa.readthedocs.io/en/stable/names.html
         'def_freq'   : Default frequency to use when not specified 
            (in MHz).
         'def_power'  : Default power level to use when not specified
            (in dBm).
        }
    :param print_msgs: True: print command messages. False: do not.
    :return: Generator object.
    """
    from scpi_generator import ScpiGenerator
    from anritsu_generator import AnritsuGenerator
    from sim_generator import SimGenerator
    
    # create the proper generator object with the correct inctruction keywords
    if instr_info['type'] == 'scpi':
        instr = vxi11.Instrument(instr_info['connection'])
        return ScpiGenerator(instr, instr_info)
    elif instr_info['type'] == 'anritsu':
        instr = vxi11.Instrument(instr_info['connection'])
        return AnritsuGenerator(instr, instr_info)
    elif instr_info['type'] == 'sim':
        return SimGenerator(None, instr_info)
    else: 
        print("Error: Instrument type " + instr_info['type'] + "not recognized.")
        exit()
