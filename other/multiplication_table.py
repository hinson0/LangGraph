# 99乘法表
print("=" * 50)
print("99乘法表")
print("=" * 50)

for i in range(1, 10):
    for j in range(1, i + 1):
        # 使用格式化字符串确保对齐
        print(f"{j} × {i} = {i * j:2d}", end="  ")
    print()  # 换行

print("=" * 50)
