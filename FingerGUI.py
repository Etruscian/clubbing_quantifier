import os
import threading
import time
import tkinter as tk

import cv2
import imutils
import numpy as np
from PIL import Image, ImageTk
from imutils.video import VideoStream

# from Old.fingerscanner_working import calculate

# Declare the root container for the GUI
root = tk.Tk()

screenwidth = 800  # root.winfo_screenwidth()
screenheight = 480  # root.winfo_screenheight()

root.geometry('{}x{}'.format(screenwidth, screenheight))

# Declare button dimensions
btnheight = int(screenheight / 3)
btnwidth = 0.16*screenwidth
btnpad = 5


# root.attributes('-fullscreen', True)


# Declaration of GUI class
class VingerGUI:
    def __init__(self):
        global root
        # Call the start page
        Startpage(self)

    def show_frame(self, cont):
        cont(self)


class Startpage:

    frame = None
    resultframe = None
    previewFrame = None
    btnFrame = None
    ratioframe = None
    angleframe = None

    image = None
    imagelabel = None

    fingertipmarker = None
    nailbedmarker = None
    jointmarker = None
    nailbedline = None
    jointline = None

    fingertippoint = ()
    nailbedpoint = ()
    jointpoint = ()

    photobutton = None
    calculatebutton = None
    powerbutton = None
    btnQuitPreview = None

    ratiolabel = None
    anglelabel = None

    thread = None
    stopEvent = None

    # Initializes the startpage.
    def __init__(self, controller):
        global root

        # Instantiate the controller handling the startpage
        Startpage.controller = controller

        # Create the background frame, make it full screen and set its color to white
        Startpage.frame = tk.Frame(root, bg="white")
        Startpage.frame.pack()
        Startpage.frame.place(relheight=1.0, relwidth=1.0)

        # Create the buttonframe, which stores all buttons. Its color is set to black for testing purposes
        self.btnFrame = tk.Frame(root, bg="black")
        self.btnFrame.pack(in_=Startpage.frame)
        self.btnFrame.place(height=screenheight, width=btnwidth)

        # Create the Preview camera button and place it in the buttonframe
        self.photobutton = tk.Button(self.btnFrame)
        icon = Image.open("./icons/camera.png").resize((int(btnwidth), int(btnwidth)), Image.ANTIALIAS)
        icon = ImageTk.PhotoImage(icon)
        self.photobutton.config(height=btnheight, width=btnwidth,
                                image=icon,
                                command=lambda: Startpage.takePicture(self),
                                highlightthickness=0, bd=0)
        self.photobutton.image = icon
        self.photobutton.pack()
        self.photobutton.place(y=0)

        # Create calculate button and place it in the buttonframe
        self.calculatebutton = tk.Button(self.btnFrame)
        icon = Image.open("./icons/calc.png").resize((int(btnwidth), int(btnwidth)), Image.ANTIALIAS)
        icon = ImageTk.PhotoImage(icon)
        self.calculatebutton.config(height=btnheight, width=btnwidth,
                                    image=icon,
                                    command=lambda: Startpage.calculateRatio(self),
                                    highlightthickness=0, bd=0)
        self.calculatebutton.image = icon
        self.calculatebutton.pack()
        self.calculatebutton.place(y=screenheight/3)

        # Create the shutdown button and place it in the buttonframe
        self.powerbutton = tk.Button(self.btnFrame)
        icon = Image.open("./icons/power-icon.png").resize((int(btnwidth), int(btnwidth)), Image.ANTIALIAS)
        icon = ImageTk.PhotoImage(icon)
        self.powerbutton.config(height=btnheight, width=btnwidth,
                                image=icon,
                                command=lambda: Startpage.closeProgram(self),
                                highlightthickness=0, bd=0)
        self.powerbutton.image = icon
        self.powerbutton.pack()
        self.powerbutton.place(y=2*screenheight/3)

        # Create the resultframe inside the backgroundframe and set its color to green for testing purposes
        self.resultframe = tk.Frame(root, bg="green")
        self.resultframe.pack(in_=Startpage.frame)
        self.resultframe.place(x=btnwidth, height=screenheight, width=screenwidth - btnwidth)

        self.ratioframe = tk.Frame(self.resultframe, bg="red")

        self.angleframe = tk.Frame(self.resultframe, bg="blue")

        # Create result label and place it in the ratio frame
        self.ratiolabel = tk.Label(self.ratioframe, text="Ratio")

        # Create calculating label and place it in the resultframe
        self.anglelabel = tk.Label(self.angleframe, text="Angle")

        self.previewFrame = tk.Frame(root, bg="green")
        self.previewFrame.pack(in_=Startpage.frame)
        self.previewFrame.place(x=btnwidth, height=screenheight, width=screenwidth - btnwidth)

        self.stopEvent = threading.Event()
        self.thread = threading.Thread(target=self.videoLoop)
        self.thread.start()

    def setpoint(self, event):
        if self.fingertipmarker is None:
            self.fingertippoint = (event.x, event.y)
            self.fingertipmarker = self.imagelabel.create_oval((event.x, event.y, event.x, event.y), width=3.0)
        elif not self.nailbedpoint:
            self.nailbedpoint = (event.x, event.y)
            self.nailbedmarker = self.imagelabel.create_oval((event.x, event.y, event.x, event.y), width=3.0)
        elif self.nailbedline is None:
            self.nailbedpoint += event.x, event.y
            print(self.nailbedpoint)
            self.nailbedline = self.imagelabel.create_line(self.nailbedpoint[0], self.nailbedpoint[1],
                                                           self.nailbedpoint[2], self.nailbedpoint[3], width=3.0)
        elif not self.jointpoint:
            self.jointpoint = (event.x, event.y)
            self.jointmarker = self.imagelabel.create_oval((event.x, event.y, event.x, event.y), width=3.0)
        elif self.jointline is None:
            self.jointpoint += (event.x, event.y)
            self.jointline = self.imagelabel.create_line(self.jointpoint[0], self.jointpoint[1], self.jointpoint[2],
                                                         self.jointpoint[3], width=3.0)

    def undo(self):
        if self.jointline is not None:
            self.imagelabel.delete(self.jointline)
            self.jointline = None
            self.jointpoint = self.jointpoint[0], self.jointpoint[1]
        elif self.jointpoint:
            self.jointpoint = ()
            self.imagelabel.delete(self.jointmarker)
        elif self.nailbedline is not None:
            self.imagelabel.delete(self.nailbedline)
            self.nailbedline = None
        elif self.nailbedpoint:
            self.nailbedpoint = ()
            self.imagelabel.delete(self.nailbedmarker)
        elif self.fingertipmarker is not None:
            self.imagelabel.delete(self.fingertipmarker)
            self.fingertipmarker = None
            self.fingertippoint = ()
        else:
            self.imagelabel.destroy()
            self.stopEvent = threading.Event()
            self.thread = threading.Thread(target=self.videoLoop)
            self.thread.start()
            icon = Image.open("./icons/camera.png").resize((int(btnwidth), int(btnwidth)), Image.ANTIALIAS)
            icon = ImageTk.PhotoImage(icon)
            self.photobutton.config(height=btnheight, width=btnwidth,
                                    image=icon,
                                    command=lambda: Startpage.takePicture(self),
                                    highlightthickness=0, bd=0)
            self.photobutton.image = icon

    def returntostart(self):
        self.resultframe.pack_forget()
        self.resultframe.place_forget()
        self.previewFrame.pack(in_=Startpage.frame)
        self.previewFrame.place(x=btnwidth, height=screenheight, width=screenwidth - btnwidth)
        self.stopEvent = threading.Event()
        self.thread = threading.Thread(target=self.videoLoop)
        self.thread.start()
        self.photobutton.config(command=lambda: Startpage.takePicture(self))

    def takePicture(self):
        if self.stopEvent is not None:
            self.stopEvent.set()

        self.imagelabel = tk.Canvas(self.previewFrame, width=screenwidth-btnwidth, height=screenheight,
                                    bd=0)
        self.imagelabel.create_image((screenwidth-btnwidth)/2, screenheight/2, anchor=tk.CENTER, image=self.image)
        self.imagelabel.image = self.image
        self.imagelabel.pack(in_=self.previewFrame)
        self.imagelabel.place(height=screenheight, width=screenwidth - btnwidth)
        self.imagelabel.bind("<Button-1>", self.setpoint)

        icon = Image.open("./icons/undo.png").resize((int(btnwidth), int(btnwidth)), Image.ANTIALIAS)
        icon = ImageTk.PhotoImage(icon)
        self.photobutton.config(height=btnheight, width=btnwidth,
                                image=icon,
                                command=lambda: Startpage.undo(self),
                                highlightthickness=0, bd=0)
        self.photobutton.image = icon

    def videoLoop(self):

        panel = None

        vs = VideoStream(usePiCamera=False).start()
        try:
            while not self.stopEvent.is_set():
                currentFrame = vs.read()
                if currentFrame is not None:
                    currentFrame = imutils.resize(currentFrame, width=int(screenwidth - btnwidth))
                    image = cv2.cvtColor(currentFrame, cv2.COLOR_BGR2RGB)
                    image = Image.fromarray(image)
                    self.image = ImageTk.PhotoImage(image)

                    if panel is None:
                        panel = tk.Label(self.previewFrame, image=self.image)
                        panel.image = self.image
                        panel.pack(in_=self.previewFrame)
                        panel.place(width=screenwidth-btnwidth, height=screenheight)
                    else:
                        panel.configure(image=self.image)
                        panel.image = self.image

        except RuntimeError:
            print("RuntimeError")

        panel.place_forget()
        panel.pack_forget()

        vs.stop()

    def closeProgram(self):
        top = tk.Toplevel()
        top.resizable(0, 0)
        top.title('Shutdown')
        top.geometry('%dx%d+%d+%d' % (300, 100, 110, 90))
        shutdownBtn = tk.Button(top, text='Shutdown', command=self.shutdown)
        shutdownBtn.pack()
        shutdownBtn.place(relheight=0.5, width=66, x=25, y=25)
        rebootBtn = tk.Button(top, text='Reboot', command=self.reboot)
        rebootBtn.pack()
        rebootBtn.place(relheight=0.5, width=66, x=117, y=25)
        cancelBtn = tk.Button(top, text='Cancel', command=top.destroy)
        cancelBtn.pack()
        cancelBtn.place(relheight=0.5, width=66, x=209, y=25)

    def calculateRatio(self):
        maxjointvalue = max((self.jointpoint[3], self.jointpoint[1]))
        maxjointindex = self.jointpoint.index(maxjointvalue)
        maxnailbedvalue = max((self.nailbedpoint[3], self.nailbedpoint[1]))
        maxnailbedindex = self.nailbedpoint.index(maxnailbedvalue)

        nailbedlength = np.sqrt((self.nailbedpoint[3] - self.nailbedpoint[1]) ** 2 +
                                (self.nailbedpoint[2] - self.nailbedpoint[0]) ** 2)

        jointlength = np.sqrt((self.jointpoint[3]-self.jointpoint[1]) ** 2 +
                              (self.jointpoint[2] - self.jointpoint[0]) ** 2)

        ratio = nailbedlength/jointlength

        jointVector = list(tuple(np.subtract((self.jointpoint[maxjointindex-1], self.jointpoint[maxjointindex]),
                                             (self.nailbedpoint[maxnailbedindex-1],
                                              self.nailbedpoint[maxnailbedindex]))))
        lengthJointVector = sum(map(abs, jointVector))

        fingertipVector = list(tuple(np.subtract(self.fingertippoint,
                                                 (self.nailbedpoint[maxnailbedindex-1],
                                                  self.nailbedpoint[maxnailbedindex]))))
        lengthFingertipVector = sum(map(abs, fingertipVector))

        angle = 360 - np.degrees(np.arccos(
            np.dot([x / lengthJointVector for x in jointVector], [x / lengthFingertipVector for x in fingertipVector])))

        self.anglelabel["text"] = angle
        self.ratiolabel["text"] = ratio

        self.previewFrame.pack_forget()
        self.previewFrame.place_forget()
        self.imagelabel.destroy()

        self.ratioframe.pack(in_=self.resultframe)
        self.ratioframe.place(height=0.5*screenheight, width=screenwidth-btnwidth)
        self.angleframe.pack(in_=self.resultframe)
        self.angleframe.place(y=0.5*screenheight, height=0.5*screenheight, width=screenwidth-btnwidth)
        self.ratiolabel.pack()
        self.ratiolabel.place(width=screenwidth - btnwidth, height=0.5*screenheight)
        self.anglelabel.pack()
        self.anglelabel.place(width=screenwidth - btnwidth, height=0.5*screenheight)
        self.photobutton.config(command=lambda: Startpage.returntostart(self))

    @staticmethod
    def shutdown():
        os.system('sudo shutdown now -h')

    @staticmethod
    def reboot():
        os.system('sudo reboot')


if __name__ == "__main__":
    VingerGUI()
    root.mainloop()
