import cv2
import numpy as np
import RPi.GPIO as gpio
from multiprocessing import Pool
import time
from imutils.video import VideoStream

def workerProcess(inputImage,fingertipModel,nailbedModel,jointModel):

    surf = cv2.xfeatures2d.SURF_create()
    surf.setHessianThreshold(400)
    surf.setExtended(True)
    bf = cv2.BFMatcher() 
    
    imgbw = np.zeros((640,480),dtype=np.uint8)
    fingertipmask = np.zeros((480,190),dtype=np.uint8)
    nailbedmask = np.zeros((480,150),dtype=np.uint8)
    jointmask = np.zeros((480,250),dtype=np.uint8)
    erodemask = np.ones((3,3),dtype=np.uint8)

    imgbw = np.array(cv2.dilate(inputImage, erodemask ,imgbw))
    fingertipmask = imgbw[:,450:]

    kptip, destip = surf.detectAndCompute(fingertipmask,None)

    tipcoordinates = (0,0)
    bedcoordinates = (0,0)
    jointcoordinates = (0,0)
    bedlinediff = np.zeros((1,480),dtype=np.int16)
    jointlinediff = np.zeros((1,480),dtype=np.int16)
    bedlength = 0
    jointlength = 0

    try:
        # find fingertip
        matches = bf.match(fingertipModel,destip)
        sumoftipcoordinates = (0,0)
        i=0
        for x in kptip:
            sumoftipcoordinates = (sumoftipcoordinates[0] + kptip[i].pt[1],sumoftipcoordinates[1] + kptip[i].pt[0])
            i=i+1
        tipcoordinates = (sumoftipcoordinates[0]/i, 450 + sumoftipcoordinates[1]/i)
    
        # crop nailbed and joint from original image
        nailbedmask = imgbw[:,tipcoordinates[1] - 250:tipcoordinates[1] - 100]
        jointmask = imgbw[:,max(tipcoordinates[1] - 500,0):tipcoordinates[1] - 250]
    
        # find nailbed
        kpbed, desbed = surf.detectAndCompute(nailbedmask,None)
        try:
            matchesbed = bf.match(nailbedModel,desbed)
        except:
            print("no nailbed")
        sumofbedcoordinates = (0,0)
        i = 0
        for x in kpbed:
            sumofbedcoordinates = (sumofbedcoordinates[0] + kpbed[i].pt[1],sumofbedcoordinates[1] + kpbed[i].pt[0])
            i=i+1
        bedcoordinates = (sumofbedcoordinates[0]/i, tipcoordinates[1]-250 + sumofbedcoordinates[1]/i)
    
        # find joint
        kpjoint, desjoint = surf.detectAndCompute(jointmask,None)
        try:
            matchesjoint = bf.match(jointModel,desjoint)
        except:
            print("no joint")
        sumofjointcoordinates = (0,0)
        i = 0
        for x in kpjoint:
            sumofjointcoordinates = (sumofjointcoordinates[0] + kpjoint[i].pt[1],sumofjointcoordinates[1] + kpjoint[i].pt[0])
            i=i+1
        jointcoordinates = (sumofjointcoordinates[0]/i, max(tipcoordinates[1]-500,0) + sumofjointcoordinates[1]/i)
    
        # define vertical lines based on coordinates found
        bedline = imgbw[0:480,bedcoordinates[1]]
        jointline = imgbw[:,jointcoordinates[1]]
            
    
        # differentiate the found lines
        for i in range(0,bedline.shape[0]-1):
            bedlinediff[0,i] = np.int16(bedline[i])-np.int16(bedline[i+1])
            jointlinediff[0,i] = np.int16(jointline[i]) - np.int16(jointline[i+1])
    
        
        bedlength = abs(np.argmax(bedlinediff[0,:]) - np.argmin(bedlinediff[0,:]))
        jointlength = abs(np.argmax(jointlinediff[0,:]) - np.argmin(jointlinediff[0,:]))    
    except:
        print("No matches found")
        jointlength=0
    if (jointlength==0):
        ratio = None
        print('No ratio')
    else:
        ratio = bedlength/jointlength
        
    return (ratio,tipcoordinates,bedcoordinates,jointcoordinates)
    

def calculate():    
    # initialize classes and containers
    imageHolder = np.zeros(shape=(480,640,10),dtype=np.uint8)
    threshold = 150
    it = [None] * 10
    ratio = np.zeros(shape=(10,1))

    surf = cv2.xfeatures2d.SURF_create()
    surf.setHessianThreshold(400)
    surf.setExtended(True)
    bf = cv2.BFMatcher() 
    
    # initialize gpio for leds
    gpio.setwarnings(False)
    gpio.setmode(gpio.BOARD)
    gpio.setup(3,gpio.OUT)
    p = gpio.PWM(3,2000)
    p.start(100)
    # open reference image for finger tip recognition
    referenceimage = cv2.imread("/home/pi/Desktop/rawimage.jpg")
    kpref, fingertipModel = surf.detectAndCompute(referenceimage,None)
    
    referencebedimage = cv2.imread("/home/pi/Desktop/nailbedraw.jpg")
    kpbedref, nailbedModel = surf.detectAndCompute(referencebedimage,None)
    
    referencejointimage = cv2.imread("/home/pi/Desktop/jointraw.jpg")
    kpjointref, jointModel = surf.detectAndCompute(referencejointimage,None)
    
    
    vs = VideoStream(usePiCamera=True,resolution=(640,480)).start()    
    time.sleep(1)
    for j in range(0,9):
        
        currentFrame = vs.read()
        imgbw = cv2.cvtColor(currentFrame,cv2.COLOR_RGB2GRAY)
        imgbw = (imgbw > threshold)
        imgbw = imgbw.astype(np.uint8,copy=False)*255
        imageHolder[:,:,j] = imgbw[:,:]
            
    p.stop()
    vs.stop()

    pool = Pool(processes=1,maxtasksperchild=None)

    for j in range(0,9): 
        #it[j] = pool.apply_async(workerProcess,(imageHolder[:,:,j],fingertipModel,nailbedModel,jointModel))
        it[j] = workerProcess(imageHolder[:,:,j],fingertipModel,nailbedModel,jointModel)
    #for l in range(0,9):
    #    try:
    #        it[l].get(timeout=80)
    #    except:
    #        print(l)
    #        pool.terminate()
    #        raise
    
    ratiosum = 0.0
    fingertipCoordinates = (0.0,0.0)
    nailbedCoordinates = (0.0,0.0)
    jointCoordinates = (0.0,0.0)
    k = 0.0
    for i in range(0,9):
        if isinstance(it[i][0],str):
            print(it[i][0])
            
        else:
            if (it[i][0]!=None and it[i][0]<3.0 and it[i][0]>0.1):
                ratiosum = ratiosum + it[i][0]
                fingertipCoordinates = (fingertipCoordinates[0] + it[i][1][0],fingertipCoordinates[1] + it[i][1][1])
                nailbedCoordinates = (nailbedCoordinates[0] + it[i][2][0],nailbedCoordinates[1] + it[i][2][1])
                jointCoordinates = (jointCoordinates[0] + it[i][3][0],jointCoordinates[1] + it[i][3][1])
                k = k+1.0

    
    if (k<=3):
        return ('Please \n try again',(0.0,0.0),(0.0,0.0),(0.0,0.0))
                
    return ("{0:10.6f}".format(float(ratiosum)/float(k)),tuple(x/k for x in fingertipCoordinates),tuple(x/k for x in nailbedCoordinates),tuple(x/k for x in jointCoordinates))
