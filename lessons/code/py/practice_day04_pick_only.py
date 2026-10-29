import queue
import time

from pynput import keyboard, mouse

events = queue.Queue()
OBSERVE_SECONDS = 15  # 实验时长，单位秒；这是人为选择，不是 Windows 常量。
def on_click(x, y, button, pressed):
    events.put_nowait(("click", (x, y, button, pressed)))


def on_release(key):
    if key == keyboard.Key.esc:
        events.put_nowait(("exit", None))  # 自定退出通知，不需要额外数据。


# 传 on_click 函数本身，不能写 on_click()；参数将由库提供。
# suppress=False：只观察；点击和 Esc 仍会传到前台应用。
mouse_listener = mouse.Listener(on_click=on_click, suppress=False)
key_listener = keyboard.Listener(on_release=on_release, suppress=False)

try:
    mouse_listener.start()  # 发起后台线程，主线程继续向下运行。
    key_listener.start()
                    # monotonic() 返回单调时钟秒数；加 15 得到本次期限，不是日期时间。
    deadline = time.monotonic() + OBSERVE_SECONDS
    print("观察已启动：点击其他窗口；松开 Esc 或等待 15 秒结束。")

    # 期限每轮都检查，持续有事件也能退出；start 不代表已实测收到输入。
    while time.monotonic() < deadline:
        if not mouse_listener.is_alive() or not key_listener.is_alive():
            raise RuntimeError("监听线程提前结束，请检查收尾时的完整报错")
        try:
            kind, payload = events.get(timeout=0.1)
        except queue.Empty:
            continue  # 没有事件也返回循环，检查期限和线程存活。
        if kind == "exit":
            print("收到 Esc 退出通知")
            break
        x, y, button, pressed = payload
        print(button, "按下" if pressed else "松开", (x, y))
except KeyboardInterrupt:
    print("收到终端 Ctrl+C")
finally:
    # stop 请求停止；join 等待线程退出，超时参数单位为秒。
    mouse_listener.stop()
    key_listener.stop()
    try:
        mouse_listener.join(timeout=1.0)
    finally:
        # 鼠标 join 即使抛出回调异常，也尝试等待键盘收尾。
        key_listener.join(timeout=1.0)
    # join 返回 None，是否已退出要另查；正常收尾应为 False False。
    print("收尾后仍存活：", mouse_listener.is_alive(), key_listener.is_alive())
