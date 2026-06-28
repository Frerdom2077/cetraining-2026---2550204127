def average(numbers):
    """计算数字列表的平均值"""
    if not numbers:  # 空列表检查
        return 0
    return sum(numbers) / len(numbers)


# 使用示例
data = [85, 92, 78, 90, 88]
result = average(data)
print(f"平均值：{result}")  # 输出：平均值：86.6