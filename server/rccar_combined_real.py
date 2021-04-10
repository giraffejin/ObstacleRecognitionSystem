#!/usr/bin/env python
# coding: utf-8

# # Imports

import numpy as np
import os
import sys
import cv2
import tensorflow as tf
import time
from trafficlight_function import *
from block_function import *

from multiprocessing import Process
from utils import label_map_util
from utils import visualization_utils as vis_util
from matplotlib import pyplot as plt
from socket import *

sys.path.append("..")
PATH_TO_VIDEO="http://192.168.0.17:8080/stream/video.mjpeg"
#open socket for connection with raspberrypi rccar
HOST='192.168.0.17'
c = socket(AF_INET, SOCK_STREAM)
c.connect((HOST,3005))
print('connected\n')

def trafficlight(video_path):
  Tvideo = cv2.VideoCapture(video_path)
  PATH_TO_FROZEN_GRAPH = os.path.join('tf_graph_rcnn', 'rcnn_v2.pb')
  PATH_TO_LABELS = os.path.join('legacy/training', 'labelmap.pbtxt')
  NUM_CLASSES=2

  #load model
  label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
  categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=NUM_CLASSES, use_display_name=True)
  category_index = label_map_util.create_category_index(categories)

  detection_graph = tf.Graph()
  with detection_graph.as_default():
    od_graph_def = tf.GraphDef()
    with tf.gfile.GFile(PATH_TO_FROZEN_GRAPH, 'rb') as fid:
      serialized_graph = fid.read()
      od_graph_def.ParseFromString(serialized_graph)
      tf.import_graph_def(od_graph_def, name='')

    sess=tf.Session(graph=detection_graph)

  image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')
  detection_boxes = detection_graph.get_tensor_by_name('detection_boxes:0')
  detection_scores = detection_graph.get_tensor_by_name('detection_scores:0')
  detection_classes = detection_graph.get_tensor_by_name('detection_classes:0')
  num_detections = detection_graph.get_tensor_by_name('num_detections:0')

  k=0
  l =0
  j=0
  result_c = {'r':0,'g':0,'b':0,'n':0}
  result_s =""

  #v_result: final result for 5 seconds video
  #result_flag: result for each frame
	
  while(Tvideo.isOpened()):
    ret, frame = Tvideo.read()
    frame = cv2.resize(frame, dsize=(500,500), interpolation = cv2.INTER_AREA)
    frame_expanded = np.expand_dims(frame, axis=0)
    k+=1
    (boxes, scores, classes, num) = sess.run(
    [detection_boxes, detection_scores, detection_classes, num_detections],
    feed_dict={image_tensor: frame_expanded})
    np_classes = np.squeeze(classes).astype(np.int32)
    if(np_classes[0]==1):
      result_flag = read_traffic_lights(frame, np.squeeze(boxes), np.squeeze(scores), np.squeeze(classes).astype(np.int32))

    elif(np_classes[0]==2):
      print("bollard detected")
      result_flag = "n"

    else:
      result_flag = "n"
	    
	    
    if(k%30 ==0):      
      result_s = signal_status_string(result_c,result_flag, k, result_s)
      result_f = result_s[0]
      if(result_c[result_f]<9):
        result_s = result_s[1:]
      else:
        result_s = result_s
     
      #signal determination per second
      if('b' in result_s):
        flag = 'tb\0'
        print("blink")
        c.send(flag.encode())

      elif('g' in result_s):
        flag = 'tg\0'
        print("green")
        c.send(flag.encode())

      elif('r' in result_s):
        flag = 'tr\0'
        print("red")
        c.send(flag.encode())

      elif('n' in result_s):
        flag = 'tn\0'
        print("none")
        c.send(flag.encode())

      else:
        flag = 'tn\0'
        print("none")
        c.send(flag.encode())

      result_s = ""
      result_c={'r':0,'g':0,'b':0,'n':0}
      print('------------')
	    
    elif(k%30==1):
      result_s = signal_status_string(result_c,result_flag,k,result_s)

    else:
      result_s = signal_status_string(result_c,result_flag, k, result_s)

#block detection
def yellowblock(video_path):
  Bvideo = cv2.VideoCapture(video_path)

  point_c = {'left':0,'right':0,'stop':0,'ahead':0}
  point_f = {'left':'yl\0','right':'yr\0','stop':'ys\0','ahead':'ya\0'}
  pre_point=""
  pre_flag=""
  cur_flag=""

  while (Bvideo.isOpened()):
    ret,frame = Bvideo.read()
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
      c.send(point_f[cur_flag].encode())
      point_c[pre_flag] =0

    pre_point = cur_point
    pre_flag = cur_flag

if __name__ == "__main__":

  tf1 = Process(target = trafficlight, args=(PATH_TO_VIDEO,))
  tf2 = Process(target = yellowblock, args=(PATH_TO_VIDEO,))

  tf1.start()
  tf2.start()

  tf1.join()
  tf2.join()

