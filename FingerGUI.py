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

screenwidth = 800
screenheight = 480

# Declare button dimensions
btnheight = int(screenheight / 3)
btnwidth = 128
btnpad = 5

# Declare the root container for the GUI
root = tk.Tk()
root.geometry('{}x{}'.format(screenwidth, screenheight))


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
        icon = ImageTk.PhotoImage(file="icons/camera.png")
        self.photobutton.config(height=btnheight, width=btnwidth,
                                image=icon,
                                command=lambda: Startpage.previewCamera(self),
                                highlightthickness=0, bd=0)
        self.photobutton.image = icon
        self.photobutton.pack()
        self.photobutton.place(y=0)

        # Create calculate button and place it in the buttonframe
        self.calculatebutton = tk.Button(self.btnFrame)
        icon = ImageTk.PhotoImage(file="icons/calc.png")
        self.calculatebutton.config(height=btnheight, width=btnwidth,
                                    image=icon,
                                    command=lambda: Startpage.calculateRatio(self),
                                    highlightthickness=0, bd=0)
        self.calculatebutton.image = icon
        self.calculatebutton.pack()
        self.calculatebutton.place(y=screenheight/3)

        # Create the shutdown button and place it in the buttonframe
        self.powerbutton = tk.Button(self.btnFrame)
        icon = ImageTk.PhotoImage(file="icons/power-icon.png")
        self.powerbutton.config(height=btnheight, width=btnwidth,
                                image=icon,
                                command=lambda: Startpage.closeProgram(self),
                                highlightthickness=0, bd=0)
        self.powerbutton.image = icon
        self.powerbutton.pack()
        self.powerbutton.place(y=2*screenheight/3)

        # self.btnQuitPreview = tk.Button(self.btnFrame, height=btnheight, width=btnwidth, text="Quit preview",
        #                                 command=lambda: Startpage.quitPreview(self))

        # Create the resultframe inside the backgroundframe and set its color to green for testing purposes
        self.resultframe = tk.Frame(root, bg="green")
        self.resultframe.pack(in_=Startpage.frame)
        self.resultframe.place(x=btnwidth, height=screenheight, width=screenwidth - btnwidth)

        ratioframe = tk.Frame(self.resultframe, bg="red")
        # ratioframe.pack(in_=self.resultframe)
        # ratioframe.place(height=0.5*screenheight, width=screenwidth-btnwidth)

        angleframe = tk.Frame(self.resultframe, bg="blue")
        # angleframe.pack(in_=self.resultframe)
        # angleframe.place(y=0.5*screenheight, height=0.5*screenheight, width=screenwidth-btnwidth)

        # Create result label and place it in the ratio frame
        self.ratiolabel = tk.Label(ratioframe, text="Ratio")
        # self.ratiolabel.pack()
        # self.ratiolabel.place(width=screenwidth - btnwidth, height=0.5*screenheight)

        # Create calculating label and place it in the resultframe
        self.anglelabel = tk.Label(angleframe, text="Angle")
        # self.anglelabel.pack()
        # self.anglelabel.place(width=screenwidth - btnwidth, height=0.5*screenheight)

        self.previewFrame = tk.Frame(root, bg="green")
        self.previewFrame.pack(in_=Startpage.frame)
        self.previewFrame.place(x=btnwidth, height=screenheight, width=screenwidth - btnwidth)

        self.stopEvent = threading.Event()
        self.thread = threading.Thread(target=self.videoLoop)
        self.thread.start()

    def previewCamera(self):

        self.resultframe.place_forget()
        self.resultframe.pack_forget()

        self.previewFrame = tk.Frame(root, bg="green")
        self.previewFrame.pack(in_=Startpage.frame)
        self.previewFrame.place(x=btnwidth, height=screenheight, width=screenwidth - btnwidth)

        self.stopEvent = threading.Event()
        self.thread = threading.Thread(target=self.videoLoop)
        self.thread.start()

        # self.photobutton.place_forget()
        # self.photobutton.pack_forget()

        # self.btnQuitPreview.pack()
        # self.btnQuitPreview.place(y=0)

    def videoLoop(self):

        panel = None

        vs = VideoStream(usePiCamera=False).start()
        try:
            while not self.stopEvent.is_set():
                currentFrame = vs.read()
                if currentFrame is not None:
                    currentFrame = imutils.resize(currentFrame, width=screenwidth - btnwidth)
                    image = cv2.cvtColor(currentFrame, cv2.COLOR_BGR2RGB)
                    image = Image.fromarray(image)
                    image = ImageTk.PhotoImage(image)

                    if panel is None:
                        panel = tk.Label(self.previewFrame, image=image)
                        panel.image = image
                        panel.pack(in_=self.previewFrame)
                        panel.place(width=screenwidth-btnwidth, height=screenheight)
                    else:
                        panel.configure(image=image)
                        panel.image = image

        except RuntimeError:
            print("RuntimeError")

        panel.place_forget()
        panel.pack_forget()

        self.previewFrame.place_forget()
        self.previewFrame.pack_forget()
        vs.stop()

        self.resultframe.pack(in_=Startpage.frame)
        self.resultframe.place(x=btnwidth, relheight=1.0, width=480 - btnwidth)

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
        if self.stopEvent is not None:
            self.stopEvent.set()

        time.sleep(1)
        fingertipCoordinates = (0.0, 0.0)
        nailbedCoordinates = (0.0, 0.0)
        jointCoordinates = (0.0, 0.0)
        # ratio, fingertipCoordinates, nailbedCoordinates, jointCoordinates = calculate()

        jointVector = list(tuple(np.subtract(jointCoordinates, nailbedCoordinates)))
        lengthJointVector = sum(map(abs, jointVector))
        fingertipVector = list(tuple(np.subtract(fingertipCoordinates, nailbedCoordinates)))
        lengthFingertipVector = sum(map(abs, fingertipVector))

        angle = 360 - np.degrees(np.arccos(
            np.dot([x / lengthJointVector for x in jointVector], [x / lengthFingertipVector for x in fingertipVector])))

        self.anglelabel["text"] = angle
        # self.ratiolabel["text"] = ratio

    @staticmethod
    def shutdown():
        os.system('sudo shutdown now -h')

    @staticmethod
    def reboot():
        os.system('sudo reboot')

    # def quitPreview(self):
        # self.stopEvent.set()
        # self.btnQuitPreview.place_forget()
        # self.btnQuitPreview.pack_forget()
        # self.photobutton.pack()
        # self.photobutton.place()


if __name__ == "__main__":
    VingerGUI()
    root.mainloop()