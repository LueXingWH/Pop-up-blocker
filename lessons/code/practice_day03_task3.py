import time,sys,pywintypes

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
    classname=w.GetClassName(hwnd)
    text=w.GetWindowText(hwnd)
    print("")
    print(f"根窗口 HWND：{root!r}")
else:
    print("无窗口")

print("等待1秒，再次检查窗口")
time.sleep(1)

if w.IsWindow(hwnd):
    print("" \
    "窗口仍在")
    print(f"是否尝试关闭{text!r},类名{classname!r}")#等待后确认是否关闭窗口
    ans=input("y/n:")
    if ans=="y" :
        # 你输 y 的这段时间里，目标可能已经被手动关掉了
        # 投递前按同一个句柄再查一次存在性，避免向失效句柄发消息
        if not w.IsWindow(hwnd):
            print("目标在确认前已消失,本轮不投递")
            sys.exit()
        # 句柄数值可能被系统复用，投递前重读一次属性，核对还是刚才那个窗口
        text2=w.GetWindowText(hwnd)
        classname2=w.GetClassName(hwnd)
        print(f"投递前核对{text2!r},类名{classname2!r}")
        # try 只包 PostMessage 一行，缩小捕获范围：异常发生时能确定是投递这一步失败
        try:
            w.PostMessage(hwnd,win32con.WM_CLOSE,0,0)
        # pywintypes.error 的三个字段：winerror 是 Windows 错误码（5 表示拒绝访问），
        # funcname 是失败的 API 名，strerror 是系统给出的文字说明
        except pywintypes.error as error:
            print(f"投递失败{error.winerror},{error.funcname},{error.strerror}")
            sys.exit(1)  # 句柄失效或权限不足时，重试不会改变结果
        # PostMessage 异步：返回时消息刚进入目标线程队列，目标程序还没处理
        print("已投递,等待两秒")
        time.sleep(2)
        # IsWindow 查询该句柄此刻是否对应一个存在的窗口
        # 窗口未销毁的常见原因：目标弹出了"是否保存"对话框，等待人作选择
        if not w.IsWindow(hwnd):
            print("窗口已销毁")
        else:
            print("窗口仍在,可能弹了保存提示")
    else:
        # 用户拒绝确认，本次不投递任何消息
        print("已取消,未投递")

sys.exit()
# print(f"命中窗口 HWND：{hwnd}")
# print(f"命中窗口标题：{w.GetWindowText(hwnd)!r}")
# print(f"根窗口 HWND：{root}")
# print(f"根窗口标题：{w.GetWindowText(root)!r}")
