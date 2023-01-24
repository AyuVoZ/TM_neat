import vgamepad as vg
import time
import keyboard

time.sleep(2)
gamepad = vg.VX360Gamepad()
keyboard.press_and_release("r")
time.sleep(0.1)
gamepad.left_joystick_float(x_value_float=0, y_value_float=1)
gamepad.update()
time.sleep(0.1)
gamepad.reset()
del gamepad
keyboard.press_and_release("enter")
time.sleep(0.1)
keyboard.press_and_release("enter")
time.sleep(0.1)
keyboard.press_and_release("escape")
gamepad = vg.VX360Gamepad()
time.sleep(0.1)
gamepad.left_joystick_float(x_value_float=0, y_value_float=1)
gamepad.update()
time.sleep(0.1)
gamepad.reset()
time.sleep(0.1)
keyboard.press_and_release("enter")
time.sleep(1)
keyboard.press_and_release("enter")
time.sleep(4)