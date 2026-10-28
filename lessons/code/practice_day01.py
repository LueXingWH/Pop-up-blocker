import win32gui
import math,time
print("请在 3 秒内移动鼠标")
time.sleep(3)
x,y=win32gui.GetCursorPos()
print(x,y)