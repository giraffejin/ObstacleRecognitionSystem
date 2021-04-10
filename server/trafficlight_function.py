import numpy as np
import cv2

# crop traffic light from input frame
def crop_traffic_lights(image, boxes, scores, classes, max_boxes_to_draw=20, min_score_thresh=0.5,
                        traffic_light_label=1):
    for i in range(min(max_boxes_to_draw, boxes.shape[0])):
        if scores[0] > min_score_thresh and classes[0] == traffic_light_label:
            ymin, xmin, ymax, xmax = tuple(boxes[0].tolist())
            (left, right, top, bottom) = (int(xmin * 500), int(xmax * 500), int(ymin * 500), int(ymax * 500))
            crop_img = image[top:bottom, left:right]
            crop_img = cv2.cvtColor(crop_img, cv2.COLOR_BGR2RGB)
        else:
            crop_img = None

    return crop_img


# color detection(red, green) from cropped traffic light
def detect_red(img, Threshold=0.1):
    desired_dim = (30, 90)

    img = cv2.resize(np.array(img), desired_dim, interpolation=cv2.INTER_LINEAR)

    img_hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)

    lower_red = np.array([0, 70, 50])
    upper_red = np.array([10, 255, 255])
    mask0 = cv2.inRange(img_hsv, lower_red, upper_red)

    lower_red = np.array([170, 70, 50])
    upper_red = np.array([180, 255, 255])
    mask1 = cv2.inRange(img_hsv, lower_red, upper_red)

    mask = mask0 + mask1

    global rate1
    rate1 = np.count_nonzero(mask) / (desired_dim[0] * desired_dim[1])

    if rate1 > Threshold:
        return True
    else:
        return False


def detect_green(img, Threshold=0.1):
    desired_dim = (30, 90)
    img = cv2.resize(np.array(img), desired_dim, interpolation=cv2.INTER_LINEAR)
    img_hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)

    lower_green = np.array([25, 70, 50])
    upper_green = np.array([102, 255, 255])
    mask = cv2.inRange(img_hsv, lower_green, upper_green)

    global rate2
    rate2 = np.count_nonzero(mask) / (desired_dim[0] * desired_dim[1])
    if rate2 > Threshold:
        return True

    else:
        return False


# determine traffic signal for each frame
def read_traffic_lights(image, boxes, scores, classes, max_boxes_to_draw=20, min_score_thresh=0.5,
                        traffic_light_label=1):
    crop_img = crop_traffic_lights(image, np.squeeze(boxes), np.squeeze(scores), np.squeeze(classes).astype(np.int32))

    if crop_img is not None:
        if detect_red(crop_img):
            result_flag = "r"

        elif detect_green(crop_img):
            result_flag = "g"


        else:
            result_flag = "b"
    else:
        result_flag = "n"

    return result_flag


def signal_status_string(result_c,result_flag, k, result_s):
  result_c[result_flag] += 1

  if(k%30==1):
    result_s = result_s + result_flag

  else:
    recent_flag = result_s[-1]
    if(recent_flag != result_flag): 
      if(result_c[recent_flag]>result_c[result_flag]):
        result_s = result_s
      else:
        result_s = result_s + result_flag    


  return result_s




































