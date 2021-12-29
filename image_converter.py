# this apps reads and loads a image file 
# and then add filter on it. Try to import 
# your pictures and add new effects on it!
#
# Created by Shing CHi Leung at 18 Sep 2021
#

import tkinter as tk
from tkinter import ttk, Message, messagebox
from tkinter.filedialog import askopenfilename, asksaveasfilename

#from PIL import Image, ImageTk, ImageFilter
import matplotlib.pyplot as plt
import matplotlib.image as mplimg

# for image transformation
import numpy as np

class ImageConverter():

    def __init__(self, filename):

        self.image = mplimg.imread(filename)

        self.image_row = self.image.shape[0]
        self.image_col = self.image.shape[1]

        self.X_edge_filter = np.array([[1,2,1],[0,0,0],[-1,-2,-1]])
        self.Y_edge_filter = np.array([[1,0,-1],[2,0,-2],[1,0,-1]])
        self.Blur_filter = np.ones((3,3)) / 9
        self.Laplacian_filter = np.array([[0,1,0],[1,-4,1],[0,1,0]])

    def filter_image(self, image, filter_choice):

        imgPadded = np.zeros((self.image_row+2, self.image_col+2))    
        imgPadded[1:self.image_row+1,1:self.image_col+1] = image[:,:]

        # set the filter
        if filter_choice == "X_edge":
            my_filter = self.X_edge_filter
        elif filter_choice == "Y_edge":
            my_filter = self.Y_edge_filter
        elif filter_choice == "Blur":
            my_filter = self.Blur_filter
        elif filter_choice == "Laplacian":
            my_filter = self.Laplacian_filter

        new_image = np.zeros((self.image_row,self.image_col))
        for i in range(self.image_row):
            for j in range(self.image_col):
                new_image[i,j] = sum(np.reshape(my_filter[0:3,0:3] * imgPadded[i:i+3,j:j+3], (-1)))
                #new_image[i,j] = sum(my_filter[0:3,0:3] * imgPadded[i:i+3,j:j+3])

        return new_image

    def apply_red_filter(self):

        R = self.image[:,:,0]
        mplimg.imsave("tmp.png", R, cmap="Reds")

    def apply_green_filter(self):

        R = self.image[:,:,1]
        mplimg.imsave("tmp.png", R, cmap="Greens")

    def apply_blue_filter(self):

        R = self.image[:,:,2]
        mplimg.imsave("tmp.png", R, cmap="Blues")

    def apply_xedge_filter(self):

        R, G, B = self.image[:,:,0], self.image[:,:,1], self.image[:,:,2]
        imgGray = (0.2989 * R + 0.5870 * G + 0.1140 * B) 
        image = self.filter_image(imgGray, "X_edge")
        mplimg.imsave("tmp.png", image)

    def apply_yedge_filter(self):

        R, G, B = self.image[:,:,0], self.image[:,:,1], self.image[:,:,2]
        imgGray = (0.2989 * R + 0.5870 * G + 0.1140 * B) 
        image = self.filter_image(imgGray, "Y_edge")
        mplimg.imsave("tmp.png", image)

    def apply_blur_filter(self):

        R, G, B = self.image[:,:,0], self.image[:,:,1], self.image[:,:,2]
        imgGray = (0.2989 * R + 0.5870 * G + 0.1140 * B) 
        image = self.filter_image(imgGray, "Blur")
        mplimg.imsave("tmp.png", image)

    def apply_laplacian_filter(self):

        R, G, B = self.image[:,:,0], self.image[:,:,1], self.image[:,:,2]
        imgGray = (0.2989 * R + 0.5870 * G + 0.1140 * B) 
        image = self.filter_image(imgGray, "Laplacian")
        mplimg.imsave("tmp.png", image)


class ImageConverterApp(tk.Tk):

    def __init__(self):

        tk.Tk.__init__(self)
        self.create_widget()

        self.imageConverter = None

    def quit_app(self):
        self.quit()
        self.destroy()
        quit()

    def create_widget(self):

        # meta data
        self.title("Image Converter")


        # menu bar
        self.menu_bar = tk.Menu(self)
        self.config(menu=self.menu_bar)

        # file menu
        self.file_menu = tk.Menu(self)
        self.file_menu.add_command(label="Open", command=self.open_file)
        self.file_menu.add_command(label="Save", command=self.save_file)
        self.file_menu.add_command(label="Quit", command=self.quit_app)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)

        # help menu
        self.help_menu = tk.Menu(self)
        self.help_menu.add_command(label="About", command=self.about_app)
        self.menu_bar.add_cascade(label="Help", menu=self.help_menu)

        # Canvas frame
        self.canva_frame = ttk.LabelFrame(self, text="Image Canva")
        self.canva_frame.grid(row=0, column=0, columnspan=1, sticky="W")

        self.canva_width = 300
        self.canva_height = 300

        self.canvas = tk.Canvas(self.canva_frame, width=self.canva_width, height=self.canva_height) 
        self.canvas.grid(row=0,column=0, columnspan=1, sticky="W")

        # button frame
        self.button_frame = ttk.LabelFrame(self, text="Add your filters")
        self.button_frame.grid(row=1,column=0, columnspan=1, sticky="W")

        self.show_button = ttk.Button(self.button_frame, text="Show", command=self.show_figure)
        self.show_button.grid(row=0,column=0, columnspan=1, sticky="W")

        self.redfilter_button = ttk.Button(self.button_frame, text="Red", command=self.red_filter)
        self.redfilter_button.grid(row=0,column=1, columnspan=1, sticky="W")

        self.greenfilter_button = ttk.Button(self.button_frame, text="Green", command=self.green_filter)
        self.greenfilter_button.grid(row=0,column=2, columnspan=1, sticky="W")

        self.bluefilter_button = ttk.Button(self.button_frame, text="Blue", command=self.blue_filter)
        self.bluefilter_button.grid(row=0,column=3, columnspan=1, sticky="W")

        self.xedge_button = ttk.Button(self.button_frame, text="X-Edge", command=self.xedge_filter)
        self.xedge_button.grid(row=1,column=0, columnspan=1, sticky="W")

        self.yedge_button = ttk.Button(self.button_frame, text="Y-Edge", command=self.yedge_filter)
        self.yedge_button.grid(row=1,column=1, columnspan=1, sticky="W")

        self.blur_button = ttk.Button(self.button_frame, text="Blur", command=self.blur_filter)
        self.blur_button.grid(row=1,column=2, columnspan=1, sticky="W")

        self.laplacian_button = ttk.Button(self.button_frame, text="Laplacian", command=self.laplacian_filter)
        self.laplacian_button.grid(row=1,column=3, columnspan=1, sticky="W")

    def open_file(self):

        self.image_filename = askopenfilename()
        self.image = tk.PhotoImage(file=self.image_filename)
        self.imageConverter = ImageConverter(self.image_filename)

        messagebox.showinfo(
            title= "File successfully read", 
            message = "The picture is succesfully read.")

        #self.image_height = self.image.shape[0]
        #self.image_width = self.image.shape[1]

    def show_figure(self):
        self.canvas.delete("all")
        self.canvas.create_image(self.canva_width/2,self.canva_height/2,image=self.image)

    def red_filter(self):
        self.canvas.delete("all")
        self.imageConverter.apply_red_filter()
        self.filtered_image = tk.PhotoImage(file="tmp.png") 
        self.canvas.create_image(self.canva_width/2,self.canva_height/2,image=self.filtered_image)

    def green_filter(self):
        self.canvas.delete("all")
        self.imageConverter.apply_green_filter()
        self.filtered_image = tk.PhotoImage(file="tmp.png") 
        self.canvas.create_image(self.canva_width/2,self.canva_height/2,image=self.filtered_image)

    def blue_filter(self):
        self.canvas.delete("all")

        self.imageConverter.apply_blue_filter()
        self.filtered_image = tk.PhotoImage(file="tmp.png") 
        self.canvas.create_image(self.canva_width/2,self.canva_height/2,image=self.filtered_image)

    def xedge_filter(self):
        self.canvas.delete("all")

        self.imageConverter.apply_xedge_filter()
        self.filtered_image = tk.PhotoImage(file="tmp.png") 
        self.canvas.create_image(self.canva_width/2,self.canva_height/2,image=self.filtered_image)


    def yedge_filter(self):
        self.canvas.delete("all")

        self.imageConverter.apply_yedge_filter()
        self.filtered_image = tk.PhotoImage(file="tmp.png") 
        self.canvas.create_image(self.canva_width/2,self.canva_height/2,image=self.filtered_image)


    def blur_filter(self):
        self.canvas.delete("all")

        self.imageConverter.apply_blur_filter()
        self.filtered_image = tk.PhotoImage(file="tmp.png") 
        self.canvas.create_image(self.canva_width/2,self.canva_height/2,image=self.filtered_image)


    def laplacian_filter(self):
        self.canvas.delete("all")

        self.imageConverter.apply_laplacian_filter()
        self.filtered_image = tk.PhotoImage(file="tmp.png") 
        self.canvas.create_image(self.canva_width/2,self.canva_height/2,image=self.filtered_image)


    def save_file(self):
        filename = askopenfilename()
        self.IC.save_file()

    def about_app(self):

        new_window = tk.Toplevel(self)
        new_window.title("About the App")

        message_text = "This is a small Tkinter Python App designed for adding filter " + \
            "to images of your own choice. Some common filters such as edge finder " + \
            "are available. You can also try with your own designed filter too! \n" + \
            "Created by Shing Chi Leung at 18 Sep 2021."

        Message(new_window, text=message_text).pack()

        # keep the size of the help window
        new_window.resizable(False, False)

def main():

    imageConverterApp = ImageConverterApp()
    imageConverterApp.mainloop()

if __name__=="__main__":
    main()