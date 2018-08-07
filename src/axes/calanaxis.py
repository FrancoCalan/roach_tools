class CalanAxis():
    """
    Generic axis class for plotting.
    """
    def __init__(self, ax, xdata, title):
        self.ax = ax
        self.ax.grid()
        self.xdata = xdata
        self.ax.set_title(title)

    def gen_xdata_dict(self):
        """
        Generates dict with xdata of the axis. The key assigned to the
        data is 'xlabel'.
        """
        key = self.format_key(self.ax.get_xlabel())
        return {key : self.xdata.tolist()}

    def format_key(self, key):
        """
        Format the key string for the dict generation. Replaces 
        uppercase for lowercase, whitespaces for '_', and removes 
        '[' and ']'.
        """
        key = key.strip() # remove lead and tailing whitespaces
        key = key.lower() # replace uppercase with lowercase
        key = key.replace(' ', '_')
        remove_chars = "[]$\\"
        for char in remove_chars:        
            key = key.replace(char, '')
        return key
