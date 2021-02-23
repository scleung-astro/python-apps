'''
This is a short app using Tkinter as GUI. It receives the user input of the 
city, then it uses the OpenWeather api to get the real time weather and 
display it in a graphical way. 

Written by Shing Chi Leung at 22 Feb 2021
'''

import numpy as np
import pandas as pd

import tkinter as tk
from tkinter import Label, LabelFrame, Message, ttk, Menu

from weather_api import weather_api_key

import requests
import json

import re
from datetime import datetime, timedelta

# the backend of the app. It controls the data fetching part and the setup of 
# internet fetching 
class WeatherBackend():

    def __init__(self):

        # first read the short city list
        self.file_path = "city_list_short.csv"
        self.df_city_list = pd.read_csv(self.file_path)

        # clean the data
        self.df_city_list.drop("Unnamed: 0", axis=1, inplace=True)
        self.df_city_list["state"].fillna("", inplace=True)

        # debug use
        print(self.df_city_list.head(10))

        # city id
        self.city_id = None

        # preparing for data fetching
        # base_url variable to store url 
        self.base_url = "http://api.openweathermap.org/data/2.5/weather?"

    # get the city_id from the dataframe city_list
    def set_city_id(self, id):
        self.city_id = id

    # get ta list of cities for a given name
    def get_candidates(self, name):
        candidates = self.df_city_list[self.df_city_list["name"]==name]
        return candidates

    # get the weather using the OpenWeather api
    def get_weather(self):

        full_url = self.base_url + "id=" + str(self.city_id) + "&appid=" + weather_api_key
        print("fetching {}".format(full_url))

        # get responses 
        responses = requests.get(full_url)

        # transfer to json
        x = responses.json()

        # when the input is correct
        return x

# the front end of the app, it controls the GUI, collect the user's input 
# and display the weather information received from the backend
class WeatherFrontend(tk.Tk):

    def __init__(self):

        tk.Tk.__init__(self)
        
        self.create_widget()
        self.resizable(False, False)

        # initialize the backend
        self.weather_backend = WeatherBackend()

    # stop the app mainloop
    def quit_app(self):
        self.quit()
        self.destory()
        exit()

    # for the visual part of app
    def create_widget(self):
        
        # meta data of the app
        self.title("Weather Apps")

        # menu bar for easy use
        self.menu_bar = Menu(self)
        self.config(menu=self.menu_bar)

        # file menu
        self.file_menu = Menu()
        self.file_menu.add_command(label="exit", command=self.quit_app)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)

        # help menu
        self.help_menu = Menu()
        self.help_menu.add_command(label="About", command=self.get_about)
        self.menu_bar.add_cascade(label="Help", menu=self.help_menu)

        # the top frame for all widgets related to user input
        self.header_frame = ttk.LabelFrame(self, text="User Input")
        self.header_frame.grid(column=0, row=0, sticky="W")

        self.header_label = ttk.Label(self.header_frame, text="Add your city for today's weather:")
        self.header_label.grid(column=0, row=1, sticky="W")

        # input of city
        self.city_choice = tk.StringVar()
        self.city_entry = ttk.Entry(self.header_frame, width=40, textvariable=self.city_choice)
        self.city_entry.insert(0, "Los Angeles")
        self.city_entry.grid(column=0, row=2, sticky="W")

        # display the possible cities based on the name given
        self.get_cityid_btn = ttk.Button(self.header_frame, text="Add City ID", command=self.get_cityid)
        self.get_cityid_btn.grid(column=1, row=2, stick="W")

        # the frame for display possible city choice
        self.citylist_frame = ttk.LabelFrame(self, text="City choices")
        self.citylist_frame.grid(column=0,row=1, sticky="W")
        
        # the list for showing the city choice
        self.citylist_scrollbar = ttk.Scrollbar(self.citylist_frame, orient="vertical")
        self.citylist_listbox = tk.Listbox(self.citylist_frame, yscrollcommand=self.citylist_scrollbar.set, width=30, height=3)
        self.citylist_listbox.grid(column=0, row=0, sticky="W")
        self.citylist_listbox.yview()
        self.citylist_scrollbar.config(command=self.citylist_listbox.yview)
        self.citylist_scrollbar.grid(column=1, row=0)

        # get the weather data from backend
        self.get_weather_btn = ttk.Button(self.citylist_frame, text="Get Weather", command=self.get_weather)
        self.get_weather_btn.grid(column=2, row=0, sticky="SE")

        # the frame for reporting the weather result
        self.weather_report_frame = ttk.LabelFrame(self, text="Weather Report")
        self.weather_report_frame.grid(column=0, row=2)

        # canvas for drawing the weather
        self.weather_canvas = tk.Canvas(self.weather_report_frame, height=340, width=340)
        self.weather_canvas.grid(column=0, columnspan=4, row=0)
        self.canvas_image = None

        # labels and values for essential weather quantities
        # current temperature
        self.temp_label = tk.Label(self.weather_report_frame, text="Temp:")
        self.temp_label.grid(column=0, row=1, sticky="W")

        self.temp_value_label = tk.Label(self.weather_report_frame, text="")
        self.temp_value_label.grid(column=1, row=1, sticky="W")

        # maximum temperature
        self.max_temp_label = tk.Label(self.weather_report_frame, text="Temp (max):")
        self.max_temp_label.grid(column=2, row=1, sticky="W")

        self.max_temp_value_label = tk.Label(self.weather_report_frame, text="")
        self.max_temp_value_label.grid(column=3, row=1, sticky="W")

        # humidity
        self.humidity_label = tk.Label(self.weather_report_frame, text="Humidity:")
        self.humidity_label.grid(column=0, row=2, sticky="W")

        self.humidity_value_label = tk.Label(self.weather_report_frame, text="")
        self.humidity_value_label.grid(column=1, row=2, sticky="W")

        # minimum temperature
        self.min_temp_label = tk.Label(self.weather_report_frame, text="Temp (min):")
        self.min_temp_label.grid(column=2, row=2, sticky="W")

        self.min_temp_value_label = tk.Label(self.weather_report_frame, text="")
        self.min_temp_value_label.grid(column=3, row=2, sticky="W")

        # sunrise time
        self.sunrise_label = tk.Label(self.weather_report_frame, text="Sunrise:")
        self.sunrise_label.grid(column=0, row=3, sticky="W")

        self.sunrise_value_label = tk.Label(self.weather_report_frame, text="")
        self.sunrise_value_label.grid(column=1, row=3, sticky="W")

        # sunset time
        self.sunset_label = tk.Label(self.weather_report_frame, text="Sunset:")
        self.sunset_label.grid(column=2, row=3, sticky="W")

        self.sunset_value_label = tk.Label(self.weather_report_frame, text="")
        self.sunset_value_label.grid(column=3, row=3, sticky="W")

    # get the weather data from backend
    def get_weather(self):


        # from the chosen city, filter the city_id and set the city_id in backend
        selected_city = self.citylist_listbox.selection_get()
        city_id = re.search(r"([0-9]+)", selected_city)
        self.weather_backend.set_city_id(city_id.group(0))

        # fetch the data
        weather = self.weather_backend.get_weather()

        print(weather.keys())

        # extract the data from the dictionary weather
        if weather["cod"] != "404":

            y = weather["main"]

            # update the display
            self.temp_value_label["text"] = round(y["temp"] - 273.15, 2)
            self.humidity_value_label["text"] = str(y["humidity"]) + "%"

            self.max_temp_value_label["text"] = round(y["temp_max"] - 273.15, 2)
            self.min_temp_value_label["text"] = round(y["temp_min"] - 273.15, 2)

            # adjust the subrise/sunset time by the timezone
            timezone = weather["timezone"]
            z = weather["sys"]
            sunrise_time = (datetime.utcfromtimestamp(z["sunrise"]) + timedelta(seconds=timezone)).strftime('%H:%M')
            sunset_time = (datetime.utcfromtimestamp(z["sunset"]) + timedelta(seconds=timezone)).strftime('%H:%M')

            # update the display
            self.sunrise_value_label["text"] = sunrise_time
            self.sunset_value_label["text"] = sunset_time

            print(weather["weather"][0]["main"])

            y = weather["weather"][0]

            # use the weather code to get the correct weather image
            if y["id"] // 100 <= 5:

                # raining image
                self.canvas_image = tk.PhotoImage(file="weatherapp_rain.png")
                self.weather_canvas.create_image(20, 20, anchor=tk.NW, image=self.canvas_image)    

            elif y["id"] // 100 == 6:

                # snowing image
                self.canvas_image = tk.PhotoImage(file="weatherapp_snow.png")
                self.weather_canvas.create_image(20, 20, anchor=tk.NW, image=self.canvas_image)

            elif y["id"] // 100 == 7:

                # cloudy image
                self.canvas_image = tk.PhotoImage(file="weatherapp_cloud.png")
                self.weather_canvas.create_image(20, 20, anchor=tk.NW, image=self.canvas_image)        

            elif y["id"] // 100 >= 8:

                # separate sunny and cloudy baseed on the descrption
                if weather["weather"][0]["main"] == "Clear":
                    self.canvas_image = tk.PhotoImage(file="weatherapp_sun.png")
                    self.weather_canvas.create_image(20, 20, anchor=tk.NW, image=self.canvas_image)    
                else:
                    self.canvas_image = tk.PhotoImage(file="weatherapp_cloud.png")
                    self.weather_canvas.create_image(20, 20, anchor=tk.NW, image=self.canvas_image)        
                #self.weather_canvas.image = self.canvas_image


        else:
            print("City ID not found")
        
    # check the city_id database in backend and get the candidate cities
    def get_cityid(self):
        candidates = self.weather_backend.get_candidates(self.city_choice.get())
        self.fill_candidate_city_listbox(candidates.to_numpy())

    # update the candidate city list 
    def fill_candidate_city_listbox(self, candidates):
        for i in range(candidates.shape[0]):
            name = candidates[i,2] + ", " + candidates[i,1] + ", " + candidates[i,0] + " (" + str(candidates[i,3]) + ")"
            self.citylist_listbox.insert(i, name)

    # pops the "ABOUT" window 
    def get_about(self):

        new_window = tk.Toplevel(self)
        new_window.title("About")
        
        message_text = "This apps will get you the current weather and 3-hour forecast " + \
            "from OpenWeatherMap API. By choosing the city (or states when necessary), " + \
            "this app will provide you the current temperature, humidity and other " + \
            "major weather quantities."
        Message(new_window, text=message_text).pack()

        new_window.resizable(False, False)


# the app can be called by simply using the frontend, then the 
# backend will be automatically called during initialization
def main():

    weather_app = WeatherFrontend()
    weather_app.mainloop()


    # sample code to test the OpenWeather api
    '''
    # complete URL
    full_url = base_url + "id=" + city_id + "&appid=" + weather_api_key

    # get responses 
    responses = requests.get(full_url)

    # transfer to json
    x = responses.json()

    # when the input is correct
    if x["cod"] != "404":

        print(x.keys())

        y = x["main"]
        print(y.keys())

        curr_temp = y["temp"]
        curr_press = y["pressure"]
        curr_humid = y["humidity"]

        z = x["weather"]
        print(z)

        weather_description = z[0]["description"] 

        print(curr_temp, curr_press, curr_humid, weather_description)

    else:
        print("City ID not found")
    '''

if __name__=="__main__":
    main()