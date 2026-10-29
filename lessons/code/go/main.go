package main

import (
	"fmt"
	"my/version"
)

var age = 100000

func hello() {
	fmt.Println("你好啊")
}

func main() {
	fmt.Println(version.Version)
	var name0 string
	name0 = "Hello World"
	fmt.Println(name0)

	var name1 = "ice"
	name2 := "真好吃"
	fmt.Println(age, "岁的", name1, name2)
	hello()
}
