// Day5 单机制参考：用结构体与多返回值表达目标记录的成功/失败。
// AI 教学参考，不是产品过滤器。所有数值都是虚构输入；不调用 Windows API。
// 从 lessons/code/go 运行：go run ./examples/day05_target_record
package main

import (
	"errors"
	"fmt"
)

// Target 把同一次采集的数据放在一起，避免只传标题而丢失窗口/进程信息。
// uintptr 是可容纳指针位宽的无符号整数；这里仅示意 HWND 的数值表示。
// 它不是 Go 指针，不会让窗口保活，也不代表已核对原生 API 的绑定。
// uint32 是 32 位无符号整数，用于示意 Windows PID；两者不能互换。
type Target struct {
	HWND  uintptr
	PID   uint32
	Title string
}

// makeTarget 是本例自定义函数，不属于 Go 或 Windows 库。
// 输入 hwnd/pid 是虚构标识，无时间单位；title 可为空（无标题不等于无窗口）。
// 返回 (Target, error)：失败给零值记录和错误；成功给记录和 nil。
// 这只检查字段是否缺失，不证明真实窗口存在、身份可靠或允许操作。
func makeTarget(hwnd uintptr, pid uint32, title string) (Target, error) {
	if hwnd == 0 {
		// errors.New(text string) 属于标准库 errors，返回携带该文字的 error。
		// 它不会自动抛异常或结束程序；必须由调用方检查返回的错误。
		return Target{}, errors.New("缺少 HWND")
	}
	if pid == 0 {
		return Target{}, errors.New("缺少 PID")
	}
	return Target{HWND: hwnd, PID: pid, Title: title}, nil
}

func main() {
	// target、err 分别接住两个返回值。字段省略时为零值：0、0、空字符串。
	target, err := makeTarget(101, 202, "练习窗口")
	if err != nil {
		// fmt.Println(...any) 来自标准库 fmt：空格分隔输出，末尾换行。
		// 返回写出的字节数与写出错误；本教学输出不接收这两个返回值。
		fmt.Println("记录失败：", err)
		return
	}
	fmt.Println("记录字段齐备：", target.HWND, target.PID, target.Title)

	// 第二组故意失败。不要因为拿到了 target 变量就绕过 err 使用它。
	target, err = makeTarget(0, 202, "缺句柄的练习")
	if err != nil {
		fmt.Println("记录失败：", err)
		return
	}
	fmt.Println("记录字段齐备：", target.HWND, target.PID, target.Title)
}
