r"""Day4 全部三个任务的完整注释参考（AI 提供，2026-10-29）。

运行：.\.venv\Scripts\python.exe .\lessons\code\py\day04_tasks_reference.py
配套：docs/learning/day04.md 第 0 节。
右键按下 -> 队列 -> 主线程只读查询；Esc/到期/Ctrl+C -> 统一收尾。
只观察，不拦截、不关闭窗口；无需导入任何带关窗操作的旧练习。
"""

import queue
import time

import pywintypes
import win32con
import win32gui as w
from pynput import keyboard, mouse


# 三个值都是实验选择，单位秒，不是 Windows 常量或鼠标采样频率。
OBSERVE_SECONDS = 15
QUEUE_WAIT_SECONDS = 0.1
JOIN_SECONDS = 1.0


def show_window(point):
    """任务二：在主线程查询事件点；本次失败就返回，仍可观察下一次。"""
    print(f"  事件点：{point}")
    try:
        # win32gui.WindowFromPoint((x, y))：一个二元组参数，返回 HWND。
        # 找不到可命中的窗口可能返回 0；不重新读取 GetCursorPos()，
        # 因为用户可能已经移开鼠标。这里查询的是消费时刻该点下的窗口，
        # 不是冻结点击时刻的窗口快照；目标可能已经移动/销毁。
        hwnd = w.WindowFromPoint(point)
        # IsWindow(hwnd) 返回此刻的存在性判断，不锁定句柄或窗口身份。
        if not hwnd or not w.IsWindow(hwnd):
            print("  没有有效命中窗口，本次跳过")
            return

        # GetAncestor(hwnd, GA_ROOT)：沿 parent 链找根 HWND，失败可能为 0。
        # GA_ROOT 是 win32con 的 API 常量，不是我们自定的等待时间。
        root = w.GetAncestor(hwnd, win32con.GA_ROOT)
        if not root or not w.IsWindow(root):
            print(f"  命中 HWND={hwnd}，但没有有效根窗口，本次跳过")
            return

        # 这两个 win32gui 调用都接收一个 HWND，返回字符串。
        # 标题为空是允许的；查询期间失效/调用失败可能抛 pywintypes.error。
        # 多次调用不是原子快照；即使 IsWindow 刚成功也仍需处理失败。
        hit_title = w.GetWindowText(hwnd)
        hit_class = w.GetClassName(hwnd)
        root_title = w.GetWindowText(root)
        root_class = w.GetClassName(root)
    except pywintypes.error as error:
        # error 的三个字段分别是 Windows 错误码、API 名、系统说明。
        # 只捕获窗口查询错误；编程错误不在这里吞掉。
        print(f"  查询失败：{error.winerror} / {error.funcname} / {error.strerror}")
        return

    print(f"  命中 HWND={hwnd}，标题={hit_title!r}，类名={hit_class!r}")
    print(f"  根窗 HWND={root}，标题={root_title!r}，类名={root_class!r}")


def main():
    # queue.Queue() 返回 FIFO 队列对象，默认 maxsize=0：不设条数上限。
    # 内部同步允许两个回调线程生产、主线程消费；队列不自动执行业务。
    # 这里只收右键按下和 Esc，不收高频移动；长时间积压仍会占用内存。
    events = queue.Queue()

    def on_click(x, y, button, pressed):
        # 任务一：pynput 在点击时传入屏幕坐标、Button 枚举和按下状态。
        # True=按下，False=松开。左键和右键松开不进入 if。
        if button == mouse.Button.right and pressed:
            # Queue.put_nowait(item)：存一条记录，成功返回 None。
            # 若队列限制容量且已满会抛 queue.Full；本例不设容量上限。
            # ("pick", (100, 200)) 表示一条候选，不是四条独立数据。
            # 不等待空位不等于绝对零耗时；查询/打印留给消费者。
            events.put_nowait(("pick", (x, y)))

    def on_release(key):
        # 任务三：keyboard.Key.esc 是特殊键枚举；只关注 Esc 松开。
        # put 只是通知主线程，退出和两个 listener 的收尾仍由主线程做。
        if key == keyboard.Key.esc:
            events.put_nowait(("exit", None))

    # Listener(...) 创建监听对象，尚未启动；回调传函数，不加调用括号。
    # suppress=False：系统输入正常传给前台，所以右键菜单仍可能弹出。
    # 不记录普通键；on_release 回调只用于 Esc 退出。
    mouse_listener = mouse.Listener(on_click=on_click, suppress=False)
    key_listener = keyboard.Listener(on_release=on_release, suppress=False)
    started = []  # 只收尾启动成功的对象，避免 join 未启动线程。
    count = 0
    reason = "异常或启动失败"

    try:
        # start() 发起后台线程，正常返回 None；主线程继续执行。
        # 本例未 wait 就绪：启动提示不是已收到真实输入的证据。
        for listener in (mouse_listener, key_listener):
            listener.start()
            started.append(listener)

        # monotonic() 无参，返回单调时钟浮点秒数，适合比较时长。
        # 假设当前为 100.0，观察 15 秒则 deadline=115.0；不是日期时间。
        deadline = time.monotonic() + OBSERVE_SECONDS
        print(f"观察已启动：右键查询；松开 Esc 或等待 {OBSERVE_SECONDS} 秒退出。")
        print("本例只读观察，右键菜单仍可出现，左键照常使用。")
        reason = "观察到期"

        # 主循环每轮都检查时限，有/没有点击均能到期；不是精确硬截止。
        while time.monotonic() < deadline:
            # is_alive() 无参，返回线程是否仍存活的布尔值。
            # 意外停止要明确报告；回调异常还可能通过 join 再抛出。
            if not mouse_listener.is_alive() or not key_listener.is_alive():
                raise RuntimeError("监听线程提前结束，请保留完整报错")
            try:
                # Queue.get(timeout=0.1)：取出并移除最早一条记录。
                # 有数据即返回该 item；空时最多等约 0.1 秒，再抛 Empty。
                # 如返回 ("pick", (100, 200))，kind="pick"，payload=(100, 200)。
                kind, payload = events.get(timeout=QUEUE_WAIT_SECONDS)
            except queue.Empty:
                # Empty 是 queue 模块的异常类，不是返回值或检测函数。
                continue  # 没点击也回到 while，检查期限和线程状态。

            if kind == "exit":
                reason = "Esc 松开"
                break
            if kind == "pick":
                count += 1
                print(f"候选 #{count}")  # 计数代表收到候选，不代表查询成功。
                show_window(payload)  # 主线程执行，payload 就是事件点。
    except KeyboardInterrupt:
        # 终端 Ctrl+C 通常触发此内置异常，不是通过 Esc 回调通知。
        reason = "终端 Ctrl+C"
    except Exception:
        reason = "异常或启动失败"
        raise  # 保留原始错误；finally 仍会执行，不假装正常完成。
    finally:
        # stop() 无参，正常返回 None：请求停止，不等于已经退出。
        # 先请求全部停止；一个失败也继续处理另一个，最终明确报错。
        cleanup_errors = []
        for listener in started:
            try:
                listener.stop()
            except Exception as error:
                cleanup_errors.append(error)

        # join(timeout=1.0)：在主线程等该线程结束，单位秒，返回 None。
        # 超时返回不代表成功；回调中的异常也可能在这里重新抛出。
        # 这里捕获 Exception 只为完成另一个 listener 的收尾，最后重报。
        for listener in started:
            try:
                listener.join(timeout=JOIN_SECONDS)
            except Exception as error:
                cleanup_errors.append(error)

        mouse_alive = mouse_listener.is_alive()
        key_alive = key_listener.is_alive()
        print(f"退出原因：{reason}；共收到 {count} 个候选")
        print(f"收尾后仍存活：鼠标={mouse_alive}，键盘={key_alive}")
        if cleanup_errors:
            for error in cleanup_errors:
                print(f"收尾异常：{error!r}")
            raise RuntimeError("收尾发生异常，不能记为通过") from cleanup_errors[0]
        if mouse_alive or key_alive:
            raise RuntimeError("等待结束后仍有监听线程存活，不能记为通过")


# 直接运行脚本才启动；导入本文件只定义函数，不启动钩子。
if __name__ == "__main__":
    main()
