class CalanAxis():
    """
    Generic axis class for plotting.
    """
    def __init__(self, ax, title=""):
        self.ax = ax
        self.ax.set_title(title)

def format_key(key):
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
