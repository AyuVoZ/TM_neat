import cv2
import math
import numpy as np
import d3dshot
import time

#Create instance of d3dshot
d = d3dshot.create(capture_output="numpy")
d.display = d.displays[0]

#func to detect a black pixel
def pixel_zero(tab):
    nz = np.nonzero(tab)[0]
    if len(nz) != 0:
        return nz[0].item()
    else:
        return len(tab) - 1

#New class for Lidar
class Lidar:

    #Set the axis of the lidars and variables
    def __init__(self):
        im = d.screenshot()
        self._set_axis_lidar(im)
        #Threshold for the black pixel due to the lightning
        self.black_threshold = [55,55,55]
        self.index = 0

    def _set_axis_lidar(self, im):
        h, w, _ = im.shape
        #get base point just above the timer in the middle
        self.road_point = (44*h//49, w//2)
        min_dist = 20
        list_ax_x = []
        list_ax_y = []
        #From the left to the right get 19 Lidars
        for angle in range(90, 280, 10):
            axis_x = []
            axis_y = []
            x = self.road_point[0]
            y = self.road_point[1]
            dx = math.cos(math.radians(angle))
            dy = math.sin(math.radians(angle))
            lenght = False
            dist = min_dist
            #Add in a list all the coords of the lidars
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
        #Get sceenshot
        img = d.screenshot()
        distances = []
        if show:
            color = (255, 0, 0)
            thickness = 4
            img = cv2.cvtColor(img, cv2.COLOR_RGBA2RGB)
        for axis_x, axis_y in zip(self.list_axis_x, self.list_axis_y):
            #Verify the pixels on the image
            index = pixel_zero(np.all(img[axis_x, axis_y] < self.black_threshold, axis=1))
            if show:
                img = cv2.line(img, (self.road_point[1], self.road_point[0]), (axis_y[index], axis_x[index]), color, thickness)
            
            #normalize between -1 and 1
            index = index/682-1
            index = np.float32(index)
            distances.append(index)
        #Put the values in an array
        res = np.array(distances, dtype=np.float32)
        if show:
            cv2.imshow("Lidar", img)
            self.index += 1
        return res

# #get multiple screen shots for gif
# lidar = Lidar()
# time.sleep(2)
# for i in range(300):
#     lidar.lidar_20(True)
