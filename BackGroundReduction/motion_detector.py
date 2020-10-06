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
from image_processing import *
# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", help="path to the video file")
ap.add_argument("-a", "--min-area", type=int, default=3000, help="minimum area size")
args = vars(ap.parse_args())

# if the video argument is None, then we are reading from webcam
if args.get("video", None) is None:
	vs = cv2.VideoCapture(0)

# reduction = cv2.createBackgroundSubtractorMOG2(detectShadows=False, varThreshold=40) #stable but ok
# reduction = cv2.bgsegm.createBackgroundSubtractorCNT(10,False,20) #not working 
# reduction = cv2.bgsegm.createBackgroundSubtractorGMG() #very noisy but fast 
reduction = cv2.bgsegm.createBackgroundSubtractorGSOC(replaceRate = 0.035) #initial frames very high, but vert stable
# loop over the frames of the video
filename = "image_crop_number"
# f = open("Cropped_images/" + filename)
ctr = 0

while True:
	ctr+=1
	# grab the current frame and initialize the occupied/unoccupied
	# text
	# frame = vs.read()
	# frame = frame if args.get("video", None) is None else frame[1]
	# text = "Unoccupied"
	
	# if the frame could not be grabbed, then we have reached the end
	# of the video
	# if frame is None:
	# 	break

	# # resize the frame, convert it to grayscale, and blur it
	# frame = imutils.resize(frame, width=500)
	# gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	# gray = cv2.GaussianBlur(gray, (21, 21), 0)

	# # if the first frame is None, initialize it
	# if firstFrame is None:
	# 	firstFrame = gray
	# 	continue

	# compute the absolute difference between the current frame and
	# first frame
	# frameDelta = cv2.absdiff(firstFrame, gray)
	# thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]
	_,frame = vs.read()
	thresh = reduction.apply(frame)
	# dilate the thresholded image to fill in holes, then find contours
	# on thresholded image
	kernel = np.ones((5,5), np.uint8)
	# thresh = cv2.erode(thresh,kernel,iterations=1)
	# thresh = cv2.dilate(thresh,kernel,iterations=1)

	# thresh = cv2.dilate(thresh,kernel, iterations=2)
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
		if cv2.contourArea(c) < args["min_area"]:
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
		cv2.imwrite("Cropped_images/" + filename + ".jpg", crop_img)

	# cv2.waitKey(0)

	# show the frame and record if the user presses a key
	cv2.imshow("Security Feed", frame)
	cv2.imshow("Thresh", thresh)
	# cv2.imshow("Frame Delta", frameDelta)
	key = cv2.waitKey(1) & 0xFF

	# if the `q` key is pressed, break from the lop
	if key == ord("q"):
		break

# cleanup the camera and close any open windows
vs.stop() if args.get("video", None) is None else vs.release()
cv2.destroyAllWindows()