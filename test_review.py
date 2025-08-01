# 这是一个测试文件，用于测试 AI 代码审核功能
# 故意包含一些可能的问题
# 更新：添加更多测试用例来验证 AI 审核功能

import os
import sys

# 未使用的导入
import datetime
import json

# 硬编码的密码（安全问题）
password = "123456"

# 全局变量（不推荐）
global_var = "test"

def bad_function():
    # 函数名不符合 Python 命名规范
    # 没有文档字符串
    # 硬编码的魔法数字
    for i in range(10):
        print(i)
    
    # 未使用的变量
    unused_var = "this is not used"
    
    # 异常处理过于宽泛
    try:
        result = 10 / 0
    except:
        print("error")

def another_function():
    # 函数过长，应该拆分
    # 缺少类型注解
    data = []
    for i in range(100):
        if i % 2 == 0:
            data.append(i)
        else:
            data.append(i * 2)
    
    # 复杂的嵌套循环
    for item in data:
        for j in range(len(item)):
            for k in range(j):
                print(item[j][k])

# 类名不符合规范
class badClass:
    def __init__(self):
        self.value = None
    
    # 方法名不符合规范
    def getValue(self):
        return self.value

# 主程序没有 main 函数保护
print("Hello World")
bad_function() 