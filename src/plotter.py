import json
import Tkinter as Tk
from experiment import Experiment
from datetime import datetime

class Plotter(Experiment):
    """
    Generic plotter class.
    """
    def __init__(self, calanfpga):
        Experiment.__init__(self, calanfpga)

    def create_figure_window(self):
        """
        Create the figure window, plots and optional widgets.
        """
        self.figure.create_window()
        self.add_figure_widgets()

    def add_figure_widgets(self):
        """
        Add widgets to animator figure. By default don't add any widget.
        """
        pass

    def add_save_widgets(self, save_name):
        """
        Add save widgets (data and pdf image) to animator figure.
        """
        # button frame
        self.button_frame = Tk.Frame(master=self.figure.root)
        self.button_frame.pack(side=Tk.TOP, anchor="w")
 
        # save button
        self.save_button = Tk.Button(self.button_frame, text='Save', command=self.save_data)
        self.save_button.pack(side=Tk.LEFT)
        
        # save entry
        save_frame = Tk.Frame(master=self.figure.root)
        save_frame.pack(side = Tk.TOP, anchor="w")
        save_label = Tk.Label(save_frame, text="Save/Print filename:")
        save_label.pack(side=Tk.LEFT)
        self.save_entry = Tk.Entry(save_frame)
        self.save_entry.insert(Tk.END, save_name)
        self.save_entry.pack(side=Tk.LEFT)

        # save datetime checkbox
        self.datetime_check = Tk.IntVar()
        self.save_datetime_checkbox = Tk.Checkbutton(save_frame, text="add datetime", variable=self.datetime_check)
        self.save_datetime_checkbox.pack(side=Tk.LEFT)

        # print button
        self.print_button = Tk.Button(self.button_frame, text='Print', command=self.save_fig)
        self.print_button.pack(side=Tk.LEFT)

    def save_data(self):
        """
        Save plot data and aditional data from experiment (if apply) 
        in JSON format.
        """
        save_data = self.figure.get_save_data()
        json_filename = self.save_entry.get()
        if self.datetime_check.get():
            json_filename += ' ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        with open(json_filename+'.json', 'w') as jsonfile:
                json.dump(save_data, jsonfile,  indent=4)
        print "Data saved."
        
    def save_fig(self):
        """
        Save current plot as a .pdf figure.
        """
        fig_filename = self.save_entry.get()
        if self.datetime_check.get():
            fig_filename += ' ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.figure.fig.savefig(fig_filename + '.pdf')
        print "Plot saved."

    def show_plot(self):
        """
        Create the plot window and plot the data.
        """
        self.create_figure_window()
        plot_data = self.get_data()
        self.figure.plot_axes(plot_data)
        Tk.mainloop()
