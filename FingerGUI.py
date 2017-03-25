import tkinter as tk
from PIL import Image, ImageTk
import numpy as np
import cv2
import time
import threading
from fingerscanner_working import calculate
import os
import imutils
from imutils.video import VideoStream

# Declare button dimensions
btnheight = int(20/3)
btnwidth = 160
btnpad=5

# Declare the root container for the GUI
root = tk.Tk()
root.attributes('-fullscreen', True)

# Declaration of GUI class
class vingerGUI:
    def __init__(self, *args, **kwargs):
        global root
	# Call the start page
        Startpage(self)
                
    def show_frame(self, cont):
        cont(self)


class Startpage:
    frame = None
    resultframe= None
    previewFrame = None
    btnFrame = None
    controller = None
    btn = None
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
        self.btnFrame.place(relheight=1.0, width=btnwidth)

	# Create the Preview camera button and place it in the buttonframe
        self.btn = tk.Button(self.btnFrame, height=btnheight, width=btnwidth, text = "Preview camera",
                        command = lambda: Startpage.previewCamera(self))
        self.btn.pack()
        self.btn.place()
        
	# Create calculate button and place it in the buttonframe
        clsbtn = tk.Button(self.btnFrame, height=btnheight, width=btnwidth, text = "Calculate ratio",
                        command = lambda: Startpage.calculateRatio(self))
        clsbtn.pack()
        clsbtn.place()

	# Create the shutdown button and place it in the buttonframe
        shutoffbtn = tk.Button(self.btnFrame, height=btnheight, width=btnwidth, text = "Shutdown",
                        command = lambda: Startpage.closeProgram(self))
        
        shutoffbtn.pack()
        shutoffbtn.place()

        self.btnQuitPreview = tk.Button(self.btnFrame,height=btnheight, width=btnwidth, text="Quit preview",
                        command = lambda: Startpage.quitPreview(self))

	# Create the resultframe inside the backgroundframe and set its color to green for testing purposes
        self.resultframe = tk.Frame(root,bg="green", width=500)
        self.resultframe.pack(in_=Startpage.frame)
        self.resultframe.place(x=btnwidth,relheight=1.0, width=480-btnwidth)

        ratioframe = tk.Frame(self.resultframe,width=500,bg="red")
        ratioframe.pack(in_=self.resultframe)
        ratioframe.place(relheight=0.5,relwidth=1.0)

        angleframe = tk.Frame(self.resultframe,width=500,bg="blue")
        angleframe.pack(in_=self.resultframe)
        angleframe.place(y=160,relheight=0.5,relwidth=1.0)
        
        # Create result label and place it in the ratio frame
        self.ratiolabel = tk.Label(ratioframe,text="Ratio")
        self.ratiolabel.pack()
        self.ratiolabel.place(width=480-btnwidth,height=160)

	# Create calculating label and place it in the resultframe
        self.anglelabel = tk.Label(angleframe,text="Angle")
        self.anglelabel.pack()
        self.anglelabel.place(width=480-btnwidth,height=160)
        
    def previewCamera(self):
        
        self.resultframe.place_forget()
        self.resultframe.pack_forget()

        self.previewFrame = tk.Frame(root,bg="green",width=500)
        self.previewFrame.pack(in_=Startpage.frame)
        self.previewFrame.place(x=btnwidth,relheight=1.0,width=480-btnwidth)

        self.stopEvent = threading.Event()
        self.thread = threading.Thread(target=self.videoLoop)
        self.thread.start()

        self.btn.place_forget()
        self.btn.pack_forget()

        self.btnQuitPreview.pack()
        self.btnQuitPreview.place()

    def videoLoop(self):
        currentFrame = None
        panel = None

        vs = VideoStream(usePiCamera=True).start()
        try:
            while not self.stopEvent.is_set():
                currentFrame = vs.read()
                if currentFrame is not None:
                    currentFrame = imutils.resize(currentFrame,width=480-btnwidth)
                    image = cv2.cvtColor(currentFrame,cv2.COLOR_BGR2RGB)
                    image = Image.fromarray(image)
                    image = ImageTk.PhotoImage(image)

                    if panel is None:
                        panel = tk.Label(self.previewFrame,image=image)
                        panel.image = image
                        panel.pack(in_=self.previewFrame)
                        panel.place(relwidth=1.0,relheight=1.0)
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
        self.resultframe.place(x=btnwidth, relheight=1.0,width=480-btnwidth)
    
    def closeProgram(self):
        top = tk.Toplevel()
        top.resizable(0,0)
        top.title('Shutdown')
        top.geometry('%dx%d+%d+%d' % (300, 100, 110, 90))
        shutdownBtn = tk.Button(top,text='Shutdown', command=self.shutdown)
        shutdownBtn.pack()
        shutdownBtn.place(relheight=0.5, width=66, x=25, y=25)
        rebootBtn = tk.Button(top,text='Reboot', command=self.reboot)
        rebootBtn.pack()
        rebootBtn.place(relheight=0.5, width=66, x=117, y=25)
        cancelBtn = tk.Button(top,text='Cancel', command=top.destroy)
        cancelBtn.pack()
        cancelBtn.place(relheight=0.5, width=66, x=209, y=25)

    def calculateRatio(self):
        if self.stopEvent is not None:
            self.stopEvent.set()
            
        time.sleep(1)
        fingertipCoordinates = (0.0,0.0)
        nailbedCoordinates = (0.0,0.0)
        jointCoordinates = (0.0,0.0)
        ratio, fingertipCoordinates, nailbedCoordinates, jointCoordinates = calculate()

        jointVector = list(tuple(np.subtract(jointCoordinates,nailbedCoordinates)))
        lengthJointVector = sum(map(abs,jointVector))
        fingertipVector = list(tuple(np.subtract(fingertipCoordinates,nailbedCoordinates)))
        lengthFingertipVector = sum(map(abs,fingertipVector))

        angle = 360 - np.degrees(np.arccos(np.dot([x/lengthJointVector for x in jointVector],[x/lengthFingertipVector for x in fingertipVector])))

        self.anglelabel["text"] = angle
        self.ratiolabel["text"] = ratio
    
    def shutdown(self):
        os.system('sudo shutdown now -h')

    def reboot(self):
        os.system('sudo reboot')

    def quitPreview(self):
        self.stopEvent.set()
        self.btnQuitPreview.place_forget()
        self.btnQuitPreview.pack_forget()
        self.btn.pack()
        self.btn.place()

if __name__ == "__main__":

    vingerGUI()
    root.mainloop()
