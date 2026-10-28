import time,sys

import win32con
import win32gui as w

MOVE_DELAY_SECONDS = 2

print(f"{MOVE_DELAY_SECONDS} 秒后采样")
time.sleep(MOVE_DELAY_SECONDS)

# 保存本轮唯一的坐标样本；后续查询都使用这个点。
point = w.GetCursorPos()
hwnd = w.WindowFromPoint(point)#句柄
if w.IsWindow(hwnd):
    root = w.GetAncestor(hwnd, win32con.GA_ROOT)#根句柄
    print(f"命中窗口 HWND：{hwnd!r}")
    print("")
    leiming=w.GetClassName(hwnd)
    text=w.GetWindowText(hwnd)
    print("")
    print(f"根窗口 HWND：{root!r}")
else:
    print("无窗口")

print("等待5秒")
time.sleep(5)

if w.IsWindow(hwnd):
    print("" \
    "窗口仍在")
else:
    print("" \
    "窗口被关闭")

sys.exit()
# print(f"命中窗口 HWND：{hwnd}")
# print(f"命中窗口标题：{w.GetWindowText(hwnd)!r}")
# print(f"根窗口 HWND：{root}")
# print(f"根窗口标题：{w.GetWindowText(root)!r}")
