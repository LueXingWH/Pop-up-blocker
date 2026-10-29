import time

import win32con
import win32gui as w


MOVE_DELAY_SECONDS = 3

# 三轮分别观察：A 的标题栏、A 的内容区、B 的可见区域。
target_labels = (
    "窗口 A 的标题栏",
    "窗口 A 的内容区",
    "窗口 B 的可见区域",
)

window_handles = []
root_handles = []

for index in range(len(target_labels)):
    print(
        f"第 {index + 1} 轮：把鼠标放到{target_labels[index]}，"
        f"{MOVE_DELAY_SECONDS} 秒后采样"
    )
    time.sleep(MOVE_DELAY_SECONDS)

    # 保存本轮唯一的坐标样本；后续查询都使用这个点。
    point = w.GetCursorPos()
    x, y = point
    print(f"屏幕坐标：x={x}, y={y}")

    hwnd = w.WindowFromPoint(point)
    window_handles.append(hwnd)

    if not hwnd:
        print("该坐标没有可查询的窗口。")
        root_handles.append(0)
        continue

    root = w.GetAncestor(hwnd, win32con.GA_ROOT)
    root_handles.append(root)

    if not root:
        print(f"命中 HWND={hwnd}，但没有取得有效的根窗口句柄。")
        continue

    print(f"命中窗口 HWND：{hwnd}")
    print(f"命中窗口标题：{w.GetWindowText(hwnd)!r}")
    print(f"命中窗口类名：{w.GetClassName(hwnd)!r}")
    print(f"根窗口 HWND：{root}")
    print(f"根窗口标题：{w.GetWindowText(root)!r}")
    print(f"根窗口类名：{w.GetClassName(root)!r}")


print("\n相邻采样结果比较：")

for index in range(len(target_labels) - 1):
    first_hwnd = window_handles[index]
    second_hwnd = window_handles[index + 1]
    first_root = root_handles[index]
    second_root = root_handles[index + 1]

    print(f"\n{index + 1} 轮与 {index + 2} 轮：")

    if first_hwnd and second_hwnd:
        if first_hwnd == second_hwnd:
            print("命中窗口句柄相同。")
        else:
            print("命中窗口句柄不同。")
    else:
        print("至少一轮没有有效的命中句柄，跳过命中句柄比较。")

    if first_root and second_root:
        if first_root == second_root:
            print("根窗口句柄相同。")
        else:
            print("根窗口句柄不同。")
    else:
        print("至少一轮没有有效的根窗口句柄，跳过根窗口比较。")