import cv2
import d3dshot
import time
import pytesseract
import re

start_time = time.time()
time.sleep(2)

d = d3dshot.create(capture_output="numpy")
d.display = d.displays[1]

def analyse(img):
    text = pytesseract.image_to_string(img, lang = 'eng', config='--psm 8 -c tessedit_char_whitelist=0123456789.')
    text = re.sub(r'[^\d.]', "", text)
    if text.replace('.','',1).isnumeric():
        # print(text)
        return(float(text))
    else:
        print(f"Not a number : {text}")
        return(0)

while True:
    time.sleep(0.1)
    #get image
    img = d.screenshot()
    accel = img[710:730, 1845:1885]
    deccel = img[910:935, 1845:1890]
    speed = img[950:1000, 1605:1680]
    turn = img[950:1000, 1710:1790]

    print(f"Generated at time {time.time()- start_time}")
    print(f"Acceleration : {analyse(accel)}")
    #print(f"Decceleration : {analyse(deccel)}")
    #print(f"Turn : {analyse(turn)}")
    print(f"Speed : {analyse(speed)}")
