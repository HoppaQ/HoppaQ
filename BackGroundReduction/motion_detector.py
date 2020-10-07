# USAGE
# python motion_detector.py
# python motion_detector.py --video videos/example_01.mp4

# import the necessary packages
# from imutils.video import VideoStream
import argparse
import datetime
import imutils
import time
import cv2 
import numpy as np
import os
from PIL import Image
import sys
from inspect import getsourcefile


sys.path.append(os.path.abspath(os.path.join('', 'CRAFTpytorch/')))

# print(sys.path	)
# import 
from  CRAFTpytorch import *

def initialize():
	# construct the argument parser and parse the arguments
	ap = argparse.ArgumentParser()
	ap.add_argument("-v", "--video", help="path to the video file")
	ap.add_argument("-a", "--min-area", type=int, default=3000, help="minimum area size")
	args = vars(ap.parse_args())
	min_area = args["min_area"]
	# if the video argument is None, then we are reading from webcam
	if args.get("video", None) is None:
		vs = cv2.VideoCapture(0)

	# reduction = cv2.createBackgroundSubtractorMOG2(detectShadows=False, varThreshold=40) #stable but ok
	# reduction = cv2.bgsegm.createBackgroundSubtractorCNT(10,False,20) #not working 
	# reduction = cv2.bgsegm.createBackgroundSubtractorGMG() #very noisy but fast 
	reduction = cv2.bgsegm.createBackgroundSubtractorGSOC(replaceRate = 0.035) #initial frames very high, but vert stable

	return vs, reduction, min_area

def motion_detector(vs, reduction, min_area):
	# loop over the frames of the video
	filename = "image_crop_number"
	# f = open("Cropped_images/" + filename)
	ctr = 0

	while True:
		ctr+=1
		_,frame = vs.read()
		thresh = reduction.apply(frame)
		# dilate the thresholded image to fill in holes, then find contours
		# on thresholded image
		kernel = np.ones((5,5), np.uint8)

		cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
		cnts = imutils.grab_contours(cnts)
		x = 1
		y = 1
		w = 1
		h = 1
		x1,y1,w1,h1 = 629,469,1,1

		# loop over the contours
		for c in cnts:
			# if the contour is too small, ignore it
			if cv2.contourArea(c) < min_area:
				continue
			(x, y, w, h) = cv2.boundingRect(c)
			x1 = min(x1, x)
			y1 = min(y1,y)
			w1 = max(w1,w)
			h1 = max(h1,h)
		cv2.rectangle(frame, (x1, y1), (x1 + w1, y1 + h1),  (0, 255, 0),2)
	    # text = "Occupied"
		# print(frame.shape)
		crop_img = frame[y1:y1+h1, x1:x1+w1,:]
		cv2.imshow("cropped", crop_img)
		if(crop_img.shape[0] > 40 and crop_img.shape[1] > 40):
			filename = filename[:-len(str(ctr))] + str(ctr)
			# cv2.imwrite("Cropped_images/" + filename + ".jpg", crop_img)
			image_processing(crop_img,filename)

		# show the frame and record if the user presses a key
		cv2.imshow("Security Feed", frame)
		cv2.imshow("Thresh", thresh)
		# cv2.imshow("Frame Delta", frameDelta)
		key = cv2.waitKey(1) & 0xFF

		# if the `q` key is pressed, break from the lop
		if key == ord("q"):
			break


	return -1 

def clearn_up():
	# cleanup the camera and close any open windows
	vs.stop() if args.get("video", None) is None else vs.release()
	cv2.destroyAllWindows()

def image_processing(image, filename):
	# image = cv.imread('Cropped_images/image_crop_num104.jpg')

    # im = Image.open("Cropped_images/image_crop_num104.jpg")
    # im.save("test-600.png", dpi=(1024,1024))

    # size = 500, int(500*image.shape[0]/image.shape[1])
    # im = Image.open("Cropped_images/image_crop_num104.jpg")
    # im_resized = im.resize(size, Image.ANTIALIAS)
    # im_resized.save("my_image_resized.png", "PNG")
    # image = cv2.imread('my_image_resized.png')

    kernel = np.array([[-1, -1, -1], 
                   [-1, 9,-1], 
                   [-1, -1, -1]])

    # Sharpen image
    image_sharp = cv2.filter2D(image, -1, kernel)
    # sharpened_image = unsharp_mask(image)
    # cv2.imwrite('my-sharpened-image.jpg', image_sharp)
    cv2.imshow("sharpened_image", image_sharp)

    cv2.imwrite("BackGroundReduction/Cropped_images/" + filename + ".jpg", image_sharp)
