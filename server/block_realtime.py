#!/usr/bin/env python
#coding: utf-8

import numpy as np
import cv2
import sys
import os
import time
import csv
from socket import *

sys.path.append("..")
PATH_TO_VIDEO="http://192.168.0.17:8080/stream/video.mjpeg"
video = cv2.VideoCapture(PATH_TO_VIDEO)


#Detect yellow on the image
def mask_yellow(img): 
  img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
  lower_range = (10,60,130)
  upper_range = (30,255,255)

  img_mask = cv2.inRange(img_hsv, lower_range, upper_range)

  return img_mask


#find yellow road location from input frame
def contour_yellow(img):
  img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
 
  #Using threshold for line detection
  ret,img_binary = cv2.threshold(img_gray,127,255,0)
  
  img_mask = mask_yellow(img)
  
  yellowcnts = cv2.findContours(img_mask.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)[-2]

  if len(yellowcnts)>0:
    
    yellow_area = max(yellowcnts, key=cv2.contourArea)
    (xg,yg,wg,hg) = cv2.boundingRect(yellow_area)
    loc = (xg,yg,wg,hg)
  
  else:
    loc = (0,0,0,0)
 
  return loc

def yellow_location(frame):
  y_loc = contour_yellow(frame)
  xg,yg,wg,hg = y_loc[0],y_loc[1],y_loc[2],y_loc[3]

  #case1: curved yellow block detected
  if(wg>=220):
    cw = 1
    cx = xg+int(1/2*wg)
    cy = yg+int(1/2*hg)
    cv2.line(frame, (cx,cy),(cx,cy),(255,0,0),5)

  #case2: straight yellow block detected
  elif(wg>=100):
    cw = 0
    cx = xg+int(1/2*wg)
    cy = yg+int(1/2*hg)
    cv2.line(frame, (cx,cy),(cx,cy),(255,0,0),5)
  
  else:
    cw = 0
    cx = 0
  
  y_point = (cw,cx)

  return y_point

def find_location(point):
  cw,cx = point[0],point[1]
  if(cw==1):
    if(cx<200):
      location = "left "
    elif(cx>300):
      location = "right"
    else:
      location = "stop "

  elif(cw==0 and cx>0):
    location = "ahead"
  
  else:
    location = "stop "
  
  return location



#connect socket
HOST='192.168.0.17'
c = socket(AF_INET, SOCK_STREAM)
c.connect((HOST,3003))

print('raspberry pi car connected\n')

point_c = {'left ':0,'right':0,'stop ':0,'ahead':0}
pre_point=""
pre_flag=""
cur_flag=""

while (video.isOpened()):
  ret,frame = video.read()
  frame = cv2.resize(frame, dsize=(500,500), interpolation = cv2.INTER_AREA)
  roi_frame = frame[250:500, 0:500]
  yellow_point = yellow_location(roi_frame)
  cur_point = find_location(yellow_point)
  point_c[cur_point] += 1 

  #check when the point is different from the past
  if(cur_point == pre_point):
    if(point_c[cur_point]>=9):
      cur_flag = cur_point


  if(cur_flag != pre_flag):
    print("--------"+cur_flag)
    c.send(cur_flag.encode())
    point_c[pre_flag] =0

  pre_point = cur_point
  pre_flag = cur_flag
  cv2.imshow('point_frame',roi_frame)

  if cv2.waitKey(33)>0:
    break

#Clean up video
c.close()
video.release()
cv2.destroyAllWindows()
