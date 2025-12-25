hello = 1

# %%
from rich import print as rprint
from rich.pretty import install as rich_install

rich_install()


# %%
class Foo:
    def __init__(self) -> None:
        self.bar = None


f = Foo()
f.bar

if getattr(f, "bar"):
    print(1)
else:
    print(0)

# %%
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="Qwen/Qwen2.5-7B-Instruct")
llm_response = llm.invoke(
    [{"role": "user", "content": f"generate a joke about ice cream and cats"}]
)
llm_response

# %%
response2 = llm.invoke("hello")
response2

# %%
from langchain.messages import HumanMessage

response3 = llm.invoke({"messages": [HumanMessage("hello")]})  # type: ignore
response3


# %%

# %%
# 导入 rich 的 print 函数（替换默认 print）
from rich import print as rprint
from rich.pretty import install
from rich.table import Table


# 示例1：美化打印字典（彩色、缩进）
info = {
    "name": "张三",
    "age": 25,
    "skills": ["Python", "SQL", "ML"],
    "salary": 10000,
    "projects": [
        {"name": "数据可视化", "status": "完成"},
        {"name": "模型训练", "status": "进行中"},
    ],
}
rprint(info)  # 彩色输出，嵌套结构自动缩进

# 示例2：创建自定义彩色表格
table = Table(title="员工信息表", style="cyan")
table.add_column("姓名", style="magenta")
table.add_column("年龄", style="green")
table.add_column("薪资", style="yellow")
table.add_row("张三", "25", "10000")
table.add_row("李四", "30", "15000")
rprint(table)  # 带标题、彩色列的表格

# 示例3：美化打印 pandas 数据框
import pandas as pd

df = pd.DataFrame(
    {
        "姓名": ["张三", "李四", "王五"],
        "年龄": [25, 30, 28],
        "薪资": [10000, 15000, 12000],
    }
)
rprint(df)  # 格式化的表格输出


# %%
messages = [1, 2, 3]
rprint("\n".join(str(item) for item in messages))


# %%
class className:
    def __init__(self, name):
        self.name = name


cls = className("yangzhibing")
cls.name

# %%


class hehe(className):
    def __init__(self, name):
        self.name = name


# %%
import json

# 原始字符串
str_data = "{'preferred_product_categories': ['运动', '跑步']}"

# 步骤1：替换单引号为双引号（注意：如果字符串内包含单引号，此方法会出错）
str_data_fixed = str_data.replace("'", '"')

# 步骤2：解析为dict
dict_data = json.loads(str_data_fixed)

# 验证
print(type(dict_data))  # 输出：<class 'dict'>
print(dict_data["preferred_product_categories"])  # 输出：['运动', '跑步']


# %%
d = {
    "姓名": ["张三", "李四", "王五"],
    "年龄": [25, 30, 28],
    "薪资": [10000, 15000, 12000],
}

print(d)

d

# %%
import builtins
import sys
from rich.pretty import install  # 明确导入 install 函数

# ========== 关键：仅在第一次运行时缓存原生函数（只执行1次） ==========
# 用全局变量/常量保存原生函数，避免被覆盖
_ORIGINAL_PRINT = builtins.print  # 永久缓存原生 print
_ORIGINAL_DISPLAYHOOK = sys.displayhook  # 永久缓存原生 displayhook

# 第一次启用 Rich 增强
install()
print("✅ 第一次启用 Rich print（有颜色/格式化）")
# 验证：输出会带 Rich 样式（彩色、缩进等）
print({"name": "test", "age": 18})

# 第一次恢复原生 print
builtins.print = _ORIGINAL_PRINT
sys.displayhook = _ORIGINAL_DISPLAYHOOK
print("✅ 恢复原生 print（无增强）")
# 验证：输出是纯文本 {'name': 'test', 'age': 18}，无任何样式
print({"name": "test", "age": 18})

# 再次启用 Rich print（即使多次调用，也能恢复）
install()
print("✅ 再次启用 Rich print")
# 验证：又恢复彩色样式
print({"name": "test", "age": 18})

# 第二次恢复原生 print（依然有效）
builtins.print = _ORIGINAL_PRINT
sys.displayhook = _ORIGINAL_DISPLAYHOOK
print("✅ 再次恢复原生 print")
# 验证：回到纯文本输出
print({"name": "test", "age": 18})


# %%
