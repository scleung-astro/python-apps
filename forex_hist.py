'''
This is a short app designed to fetch the historcial forex data for given 
pairs (based on my choices), and in a given time frame. Then the user can
add extra indicators on the graph for their study. In this version, 
exponential moving average and Bollinger's Band. The GUI relies on 
Tkinter library.

Written by Shing Chi Leung at 21 February 2021
'''

import yfinance  as yf
import pandas as pd

import tkinter as tk
from tkinter import Label, Message, ttk, Menu

# for plotting graphs on Canvas in Tkineter
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

# This is the backend class for the app. It fetches and analyzes the data.
class ForexHist():

    def __init__(self):
        self.df = None
        
        # the forex pair to look at
        self.pair = None

        # begin and end date of the fetched data
        self.start_date = None
        self.end_date = None

    def set_pair(self, pair):
        self.pair = pair

    def set_start_date(self, date):
        self.start_date = date

    def set_end_date(self, date):
        self.end_date = date

    # calculate Exponential moving average of period 9
    def get_EMA9(self):
        self.df["EMA9"] = self.df["Close"].ewm(span=9).mean()

    # calculate Exponential moving average of period 20
    def get_EMA20(self):
        self.df["EMA20"] = self.df["Close"].ewm(span=20).mean()

    # calculate Bollinger's band
    def get_Bollinger(self):
        self.df["Mean"] = self.df["Close"].rolling(window=20).mean()
        self.df["Std"] = self.df["Close"].rolling(window=20).std()

        self.df["Bol Hi"] = self.df["Mean"] + self.df["Std"] * 2
        self.df["Bol Lo"] = self.df["Mean"] - self.df["Std"] * 2

    # use yfinance module to fetch the data and analyze the data
    def get_data(self):
        self. df = yf.download(self.pair, self.start_date, self.end_date)
        print(self.df.tail(5))

        self.get_EMA9()
        self.get_EMA20()
        self.get_Bollinger()

# this is the frontend class of the app. It adopts the backend class as a
# variable and construct the GUI. It inherits the Tkinter class so that 
# all widget can be directly built on it
class ForexHistApp(tk.Tk):

    def __init__(self):

        tk.Tk.__init__(self)
        self.create_widget()
        self.resizable(False, False)

        # the backend class
        self.forex_hist = ForexHist()

    # stop the loop and quit the apps
    def quit_apps(self):
        self.quit()
        self.destroy()
        exit()

    # draw the front end
    def create_widget(self):
        self.create_header()
        self.create_plotbox()

    # all the user input interface
    def create_header(self):

        # apps title 
        self.title("Forex Historical Price Analyzer")

        # create menu bar widget
        self.menu_bar = Menu(self)
        self.config(menu=self.menu_bar)

        # add the file menu options
        self.file_menu = Menu(self.menu_bar, tearoff=0)
        self.file_menu.add_command(label="Exit",command=self.quit_apps)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)

        # add the help menu options
        self.help_menu = Menu(self.menu_bar, tearoff=0)
        self.help_menu.add_command(label="About",command=self.show_help_window)
        self.menu_bar.add_cascade(label="Help", menu=self.help_menu)

        # title frame for storing the user input interface
        self.header_frame = ttk.LabelFrame(self, text="Forex options")
        self.header_frame.grid(column=0,row=0, sticky="W")

        # header
        self.header = ttk.Label(self.header_frame, text = "Forex Sector")
        self.header.grid(column=0, row=0, sticky="W")

        # forex label and its choice
        self.forex_label = ttk.Label(self.header_frame, text="Forex: ")
        self.forex_label.grid(column=0, row=1, sticky="W")

        self.forex_pair = tk.StringVar()
        self.forex_pair_chosen = ttk.Combobox(self.header_frame, width=10, textvariable=self.forex_pair, state="readonly")
        self.forex_pair_chosen["values"] = ("USDJPY", "EURJPY", "AUDJPY")
        self.forex_pair_chosen.current(0)
        self.forex_pair_chosen.grid(column=0, row=2)

        # start date 
        self.start_date_label = ttk.Label(self.header_frame, text="Start Date")
        self.start_date_label.grid(column=1,row=1)

        self.start_date = tk.StringVar()
        self.start_date_box = ttk.Entry(self.header_frame, width=10, text="2020-01-01", textvariable=self.start_date)
        self.start_date_box.insert(0, '2020-01-01')
        self.start_date_box.grid(column=1, row=2)

        # end date
        self.end_date_label = ttk.Label(self.header_frame, text="End Date")
        self.end_date_label.grid(column=2,row=1)

        self.end_date = tk.StringVar()
        self.end_date_box = ttk.Entry(self.header_frame, width=10, textvariable=self.end_date)
        self.end_date_box.insert(0, '2020-12-31')
        self.end_date_box.grid(column=2, row=2)

        # fetch data using backend
        self.get_data_button = ttk.Button(self.header_frame, text="Get Data!", command=self.get_data)
        self.get_data_button.grid(column=3,row=2)

        # indicator section 
        self.indicator_label = ttk.Label(self.header_frame, text = "Indicators:")
        self.indicator_label.grid(column=0, row=3, sticky="W")

        # EMA9 
        self.ema9_button = ttk.Button(self.header_frame, text="EMA9", command=self.plot_ema9, state="disable")
        self.ema9_button.grid(column=1,row=3)

        # EMA20
        self.ema20_button = ttk.Button(self.header_frame, text="EMA20", command=self.plot_ema20, state="disable")
        self.ema20_button.grid(column=2,row=3)
        
        # Bollinger's band
        self.bollinger_button = ttk.Button(self.header_frame, text="Bollinger", command=self.plot_bollinger, state="disable")
        self.bollinger_button.grid(column=3,row=3)

    def get_data(self):

        forex_pair = self.forex_pair.get()
        if forex_pair == "USDJPY":
            name = "USDJPY=X" 
        elif forex_pair == "EURJPY":
            name = "EURJPY=X" 
        elif forex_pair == "AUDJPY":
            name = "AUDJPY=X" 

        self.forex_hist.set_pair(name)
        self.forex_hist.set_start_date(self.start_date.get())
        self.forex_hist.set_end_date(self.end_date.get())
        self.forex_hist.get_data()

        # activate the indicator buttons
        self.ema9_button.state(["!disabled"])
        self.ema20_button.state(["!disabled"])
        self.bollinger_button.state(["!disabled"])

        self.plot_data()

    def plot_data(self):

        if self.price_line == None:
            self.price_line, = self.plotax.plot(self.forex_hist.df.index, self.forex_hist.df["Close"])
            self.canvas.draw()
            print(self.price_line)
        else:
            self.price_line.set_xdata(self.forex_hist.df.index.to_numpy())
            self.price_line.set_ydata(self.forex_hist.df["Close"].to_numpy())

            self.plotax.set_xlim(min(self.forex_hist.df.index), max(self.forex_hist.df.index))
            self.plotax.set_ylim(min(self.forex_hist.df["Close"]), max(self.forex_hist.df["Close"]))

            # also remove indicator lines if they are plot on the canvas
            if self.ema9_line != None:
                self.ema9_line.set_linestyle("None")

            if self.ema20_line != None:
                self.ema20_line.set_linestyle("None")

            if self.bolhi_line != None:
                self.bolhi_line.set_linestyle("None")

            if self.bollo_line != None:
                self.bollo_line.set_linestyle("None")

            # need to update the GUI screen
            self.canvas.draw()

    # draw the EMA9 data, if there is no previous data, plot the data and get the line2D object
    # if there is previous line2D object, replace the old data in line2D object with the new one
    def plot_ema9(self):

        if self.ema9_line == None:
            self.ema9_line, = self.plotax.plot(self.forex_hist.df.index, self.forex_hist.df["EMA9"])
        else:
            if self.ema9_line.get_linestyle() == "None":
                self.ema9_line.set_xdata(self.forex_hist.df.index.to_numpy())
                self.ema9_line.set_ydata(self.forex_hist.df["EMA9"].to_numpy())
                self.ema9_line.set_linestyle("solid")
            else:
                self.ema9_line.set_linestyle("None")

        # need to update the GUI screen
        self.canvas.draw()

    # draw the EMA20 data, if there is no previous data, plot the data and get the line2D object
    # if there is previous line2D object, replace the old data in line2D object with the new one
    def plot_ema20(self):
        if self.ema20_line == None:
            self.ema20_line, = self.plotax.plot(self.forex_hist.df.index, self.forex_hist.df["EMA20"])
        else:
            if self.ema20_line.get_linestyle() == "None":
                self.ema20_line.set_xdata(self.forex_hist.df.index.to_numpy())
                self.ema20_line.set_ydata(self.forex_hist.df["EMA20"].to_numpy())
                self.ema20_line.set_linestyle("solid")
            else:
                self.ema20_line.set_linestyle("None")

        # need to update the GUI screen
        self.canvas.draw()

    # draw the BBand data, if there is no previous data, plot the data and get the line2D object
    # if there is previous line2D object, replace the old data in line2D object with the new one
    #
    # repeat for both upper and lower lines
    def plot_bollinger(self):

        if self.bolhi_line == None:
            self.bolhi_line, = self.plotax.plot(self.forex_hist.df.index, self.forex_hist.df["Bol Hi"], c="red")
        else:
            if self.bolhi_line.get_linestyle() == "None":
                self.bolhi_line.set_xdata(self.forex_hist.df.index.to_numpy())
                self.bolhi_line.set_ydata(self.forex_hist.df["Bol Hi"].to_numpy())
                self.bolhi_line.set_linestyle("solid")
                self.bolhi_line.set_c("red")
            else:
                self.bolhi_line.set_linestyle("None")

        if self.bollo_line == None:
            self.bollo_line, = self.plotax.plot(self.forex_hist.df.index, self.forex_hist.df["Bol Lo"], c="red")
        else:
            if self.bollo_line.get_linestyle() == "None":
                self.bollo_line.set_xdata(self.forex_hist.df.index.to_numpy())
                self.bollo_line.set_ydata(self.forex_hist.df["Bol Lo"].to_numpy())
                self.bollo_line.set_linestyle("solid")
                self.bollo_line.set_c("red")
            else:
                self.bollo_line.set_linestyle("None")

        # need to update the GUI screen
        self.canvas.draw()

    # a short window to display the use of the app
    def show_help_window(self):

        # set up geometry of the help window
        new_window = tk.Toplevel(self)
        new_window.title("Help")
        new_window.geometry("200x200")

        # the message
        Message(new_window, text="This apps gets the exchange rate for a given timeframe, \
            then analyze its indicators. Choose the desired forex, starting and ending \
            date, and choose the related indicator").pack()
        new_window.resizable(False, False)

    # the graph section of the apps
    def create_plotbox(self):

        # the plot graph section
        self.plotframe = ttk.LabelFrame(self, text="Forex Price Plot")
        self.plotframe.grid(column=0,row=1)

        # the pyplot setting
        self.plotfig = Figure(figsize=(5,3))
        self.plotax = self.plotfig.add_subplot(111)

        # patch pyplot to Tkinter canvas
        self.canvas = FigureCanvasTkAgg(self.plotfig, self.plotframe)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(column=0,row=2)

        # the location to store the line data
        self.price_line = None
        self.ema9_line = None
        self.ema20_line = None
        self.bolhi_line = None
        self.bollo_line = None


# after the frontend and backend are done, to operate the code will
# only need to call the frontend
def main():

    forex_hist_app = ForexHistApp()
    forex_hist_app.mainloop()

    '''
    forex_hist = ForexHist()
    forex_hist.set_pair("USDJPY=X")
    forex_hist.set_start_date("2020-01-01")
    forex_hist.set_end_date("2020-12-31")
    forex_hist.get_data()
    forex_hist.get_EMA9()
    print(forex_hist.df.tail(10))
    '''


if __name__ == "__main__":
    main()