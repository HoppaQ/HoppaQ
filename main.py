import  BackGroundReduction.motion_detector  as md
import BackGroundReduction.image_processing  as imgp 
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
from time import time
import _thread

import requests
import csv
from ProductController import *
import serial
import os, glob


# time.sleep(10)

# ArduinoUnoSerial = serial.Serial('com15',9600)
# print(ArduinoUnoSerial.readline())


# from async_flask.application import
sys.path.append(os.path.abspath(os.path.join('', 'CRAFTpytorch/')))
sys.path.append(os.path.abspath(os.path.join('', 'deep_text_recognition_benchmark/')))
# print(sys.path	)
# import 
from  CRAFTpytorch import test
from deep_text_recognition_benchmark import  demo,dataset,model,utils
start = time()


def initialize():
	# construct the argument parser and parse the arguments
	ap = argparse.ArgumentParser()
	ap.add_argument("-v", "--video", help="path to the video file")
	ap.add_argument("-a", "--min-area", type=int, default=3000, help="minimum area size")
	args = vars(ap.parse_args())
	min_area = args["min_area"]
	# if the video argument is None, then we are reading from webcam
	if args.get("video", None) is None:
		vs = cv2.VideoCapture(1 + cv2.CAP_DSHOW)

	# reduction = cv2.createBackgroundSubtractorMOG2(detectShadows=False, varThreshold=40) #stable but ok
	# reduction = cv2.bgsegm.createBackgroundSubtractorCNT(10,False,20) #not working 
	# reduction = cv2.bgsegm.createBackgroundSubtractorGMG() #very noisy but fast 
	reduction = cv2.bgsegm.createBackgroundSubtractorGSOC(replaceRate = 0.035) #initial frames very high, but vert stable

	net, refine_net = test.load_main()
	model,converter = demo.load_model()
	return vs, reduction, min_area, net, refine_net,model,converter

def motion_detector(vs, reduction, min_area, net, refine_net,model,converter):
	# loop over the frames of the video
	filename = "image_crop_number"
	# f = open("Cropped_images/" + filename)
	ctr = 0
	images = []
	# os.makedirs(os.path.abspath(os.path.join('', 'result')))

	while True:


		# if (int(time() - start)%90 == 0):
		# 	os.rmdir(os.path.abspath(os.path.join('', 'result')))
		# 	os.makedirs(os.path.abspath(os.path.join('', 'result')))


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
		# print(frame.shape)


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
		# cv2.imshow("cropped", crop_img
		images.append(crop_img)
		# if(crop_img.shape[0] > 40 and crop_img.shape[1] > 40):
		if(len(images) > 40):

			max_size = 0
			im = 0
			im_l = 0
			im_r = 0
			for i in range(len(images)):
				if(images[i].shape[0]*images[i].shape[1] >= max_size):
					max_size = images[i].shape[0]*images[i].shape[1] 
					im = images[i]
					try:
						im_l = images[i-1]
					except:
						im_l = [0]
					try:
						im_r = images[i+1]
					except:
						im_r = [0]
			filename = filename[:-len(str(ctr))] + str(ctr)
			# cv2.imwrite("Cropped_images/" + filename + ".jpg", crop_img)
			
			if(im.shape[0] > 50 and im.shape[1] > 50):
				# print(im)
				image_processing(im,filename, net, refine_net,model,converter)
				images = []

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

def image_processing(image, filename, net, refine_net,model,converter):

	# kernel = np.array([[0, -1, 0], 
	#                [-1, 5,-1], 
	#                [0, -1, 0]])

	# Sharpen image
	# image_sharp = cv2.filter2D(image, -1, kernel)
	image_sharp = image

	# cv2.imshow("sharpened_image", image_sharp)
	# _thread.start_new_thread(test.run_model,(net,refine_net, image_sharp, filename,model,converter))
	all_img, all_pred, all_confidence_scores = test.run_model(net,refine_net, image_sharp, filename,model,converter)

	corpus = [] 
	for i in range(len(all_confidence_scores)):
		if(all_confidence_scores[i] > 0.90):
			print(all_confidence_scores[i], all_pred[i], all_img[i])
			corpus.append({"score" : all_confidence_scores[i] , "pred" : all_pred[i]})

	# brands = DataController.get_all_brands()
	# print(brands)
	# API_ENDPOINT = "http://localhost:8000/billing/addproduct/"
	# data = {'name':"hello", 'brandName':"someBrand", 'price':2400, 'quantity' :1,} 
	# r = requests.post(url = API_ENDPOINT, data = data) 
	#     ProductController.get_product()
	print(corpus)
	dir = 'result'
	for file in os.scandir(dir):
		os.remove(file.path)
	print("Add product")
	# b,prod,p = getProduct(corpus)
	try :
		b,prod,p = getProduct(corpus)
		print(b,prod,p)

		f = open("scratch.txt", "r")
		w = float(f.read())
		print(w)
		if w<0:
			productStatus = "delete"
		elif w>0:
			productStatus ="add"
		else:
			productStatus="noChange"
		print(productStatus)
		if(productStatus!='noChange'):
			with open('records.csv', 'w', newline='') as file:
				writer = csv.writer(file)
				writer.writerow([' '.join(prod), b, 1, p, productStatus])
	except:
		pass




if __name__ == "__main__":
	vs, reduction, min_area, net, refine_net,model,converter = initialize()

	motion_detector(vs, reduction, min_area, net, refine_net,model,converter)
	cleanup()