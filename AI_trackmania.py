import cv2
import math
import numpy as np
import d3dshot
import time
import pytesseract
import re

time.sleep(2)
#get image
d = d3dshot.create(capture_output="numpy")

# read image
#img = cv2.imread("trackmania.png")

# median blur
# median = cv2.medianBlur(img, 5)

# # threshold on black
# lower = (0,0,0)
# upper = (20,20,20)
# thresh = cv2.inRange(median, lower, upper)

# # save result
# cv2.imwrite("black_lines_threshold.jpg", thresh)

# # view result
# cv2.imshow("image", thresh)
# cv2.waitKey(0)
# cv2.destroyAllWindows()

# while True:
#     pass

def armin(tab):
    nz = np.nonzero(tab)[0]
    if len(nz) != 0:
        return nz[0].item()
    else:
        return len(tab) - 1

class Lidar:
    def __init__(self):
        im = d.screenshot()
        self._set_axis_lidar(im)
        self.black_threshold = [55,55,55]
        self.index = 0

    def _set_axis_lidar(self, im):
        h, w, _ = im.shape
        self.h = h
        self.w = w
        self.road_point = (44*h//49, w//2)
        min_dist = 20
        list_ax_x = []
        list_ax_y = []
        for angle in range(90, 280, 10):
            axis_x = []
            axis_y = []
            x = self.road_point[0]
            y = self.road_point[1]
            dx = math.cos(math.radians(angle))
            dy = math.sin(math.radians(angle))
            lenght = False
            dist = min_dist
            while not lenght:
                newx = int(x + dist * dx)
                newy = int(y + dist * dy)
                if newx <= 0 or newy <= 0 or newy >= w - 1:
                    lenght = True
                    list_ax_x.append(np.array(axis_x))
                    list_ax_y.append(np.array(axis_y))
                else:
                    axis_x.append(newx)
                    axis_y.append(newy)
                dist = dist + 1
        self.list_axis_x = list_ax_x
        self.list_axis_y = list_ax_y

    def lidar_20(self, show=False):
        img = d.screenshot()
        h, w, _ = img.shape
        if h != self.h or w != self.w:
            self._set_axis_lidar(img)
        distances = []
        if show:
            color = (255, 0, 0)
            thickness = 4
            img = cv2.cvtColor(img, cv2.COLOR_RGBA2RGB)
        for axis_x, axis_y in zip(self.list_axis_x, self.list_axis_y):
            index = armin(np.all(img[axis_x, axis_y] < self.black_threshold, axis=1))
            if show:
                img = cv2.line(img, (self.road_point[1], self.road_point[0]), (axis_y[index], axis_x[index]), color, thickness)
            index = index/682-1
            index = np.float32(index)
            distances.append(index)
        # speed = img[1005:1035, 1700:1780]
        # speed_value = analyse(speed)
        # if(speed_value>250):
        #     speed_value=250
        # distances.append(np.float32(speed_value/125-1))
        res = np.array(distances, dtype=np.float32)
        if show:
            cv2.imwrite(str(self.index) + ".png", img)
            self.index += 1
        return res

# lidar = Lidar()
# time.sleep(2)
# for i in range(300):
#     lidar.lidar_20(True)
