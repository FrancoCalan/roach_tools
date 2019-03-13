import numexpr
import Tkinter as Tk
import matplotlib.animation as animation
from plotter import Plotter

class Animator(Plotter):
    """
    Generic animator class.
    """
    def __init__(self, calanfpga):
        Plotter.__init__(self, calanfpga)
        self.reg_entries = {} # reference to additional GUI entries to modify registers in FPGA
        self.labels      = {} # reference to additional GUI labels that can later be updated

    def start_animation(self):
        """
        Add the basic parameters to the plot and starts an animation.
        """
        self.create_figure_window()
        anim = animation.FuncAnimation(self.figure.fig, animate, fargs=(self,), blit=True)
        Tk.mainloop()

    def add_reg_entry(self, reg):
        """
        Add a text entry to the GUI to modify a register in FPGA.
        The desired value must be written in the entry textbox,
        and the value is assigned by pressing <Return> with the textbox focused.
        :param reg: name of the register to modify by the entry.
            Also used as the key for the reg_entries dictionary.
        """
        frame = Tk.Frame(master=self.figure.root)
        frame.pack(side = Tk.TOP, anchor="w")
        label = Tk.Label(frame, text=reg+":")
        label.pack(side=Tk.LEFT)
        entry = Tk.Entry(frame)
        entry.insert(Tk.END, self.fpga.read_reg(reg))
        entry.pack(side=Tk.LEFT)
        entry.bind('<Return>', lambda x: self.set_reg_from_entry(reg, entry))
        self.reg_entries[reg] = entry

    def add_label(self, label_key, label_text):
        """
        Add a label in a new frame in the GUI. The label can
        be eventually updated to show data in real-time.
        :param label_key: identifier key in the label dictionary.
        :param label_text: (initial) text of the label.
        """
        frame = Tk.Frame(master=self.figure.root)
        frame.pack(side = Tk.TOP, anchor="w")
        label = Tk.Label(frame, text=label_text)
        label.pack(side=Tk.LEFT)
        self.labels[label_key](label)

    def set_reg_from_entry(self, reg, entry):
        """
        Modify a FPGA register from the value of an entry.
        """
        string_val = entry.get()
        try:
            val = int(numexpr.evaluate(string_val))
        except:
            raise Exception('Unable to parse value in textbox: ' + string_val)
        self.fpga.set_reg(reg, val)

    def add_reset_button(self, reg_name, button_text):
        """
        Add reset button to the button panel of the GUI.
        Once pressed, the register is reset, that is, is set to 1 and
        the 0 immediately.
        :param reg_name: name of the register affected by the button.
        :param button_text: default text to display in the button.
        """
        reset_button = Tk.Button(self.button_frame, text=button_text)
        reset_button.config(command=lambda: self.fpga.reset_reg(reg_name))
        reset_button.pack(side=Tk.LEFT)

    def add_push_button(self, reg_name, button_text_raised, button_text_sunken):
        """
        Add push button to the button panel of the GUI.
        When pressed the button toggles states between raised and sunken.
        When it toggles to sunken, the register is set to 1.
        When it toggles to raised, the register is set to 0.
        :param reg_name: name of the register affected by the button.
        :param button_text_raised: default text to display in the button when raised.
        :param button_text_sunken: default text to display in the button when sunken.
        """
        push_button = Tk.Button(self.button_frame)
        push_button.config(command=lambda: self.toggle_push_button(push_button, reg_name, button_text_raised, button_text_sunken))
        push_button.pack(side=Tk.LEFT)
        if self.fpga.read_reg(reg_name) == 0:
            push_button.config(relief=Tk.RAISED)
            push_button.config(text=button_text_raised)
        else:
            push_button.config(relief=Tk.SUNKEN)
            push_button.config(text=button_text_sunken)

    def toggle_push_button(self, push_button, reg_name, button_text_raised, button_text_sunken):
        """
        Toggles a push button by changing the register value,
        and modifying the button text.
        :param push_button: button to toggle.
        :param reg_name: name of the register affected by the button.
        :param button_text_raised: default text to display in the button when raised.
        :param button_text_sunken: default text to display in the button when sunken.
        """
        if self.fpga.read_reg(reg_name) == 1:
            push_button.config(relief=Tk.RAISED)
            push_button.config(text=button_text_raised)
            self.fpga.set_reg(reg_name, 0)
        else:
            push_button.config(relief=Tk.SUNKEN)
            push_button.config(text=button_text_sunken)
            self.fpga.set_reg(reg_name, 1)

def animate(_, self):
    """
    It's call on every frame of the animation. Updates the data.
    """
    animation_data = self.get_data()
    self.figure.plot_axes(animation_data)

    return []
