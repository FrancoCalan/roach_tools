class Experiment():
    """
    Most generic class. Repesents a generic experiment in roach with any model.
    It only initialize the most generic attributes for an experiment: configuration 
    settings, and model.
    """
    def __init__(self, calanfpga):
        self.fpga = calanfpga
        self.settings = self.fpga.settings

