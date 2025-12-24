# from openai import OpenAI

# # 客户端会自动读取macOS的OPENAI_API_KEY环境变量
# client = OpenAI()

# # 测试调用
# try:
#     response = client.chat.completions.create(
#         model="Qwen/Qwen2.5-7B-Instruct",  # 确认模型名正确
#         messages=[{"role": "user", "content": "我是杨亦成的爸爸"}],
#     )
#     print("回复：", response.choices[0].message.content)
# except Exception as e:
#     print(f"调用失败：{e}")
#     # 针对性提示，帮助定位
#     if "timeout" in str(e).lower():
#         print("提示：网络无法连接到SiliconFlow，请检查网络或代理设置")
#     elif "authentication" in str(e).lower():
#         print("提示：API密钥错误，请检查SiliconFlow密钥")
#     elif "model" in str(e).lower():
#         print("提示：模型名错误，请确认SiliconFlow上的模型名称")


# %%
from dotenv import load_dotenv
from openai import OpenAI

# 加载 .env 文件中的环境变量
load_dotenv()

# 自动读取环境变量
client = OpenAI()

# 测试调用
try:
    response = client.chat.completions.create(
        model="Qwen/Qwen2.5-7B-Instruct",  # 确认模型名正确
        messages=[{"role": "user", "content": "我是杨亦成的爸爸"}],
    )
    print("回复：", response.choices[0].message.content)
except Exception as e:
    print(f"调用失败：{e}")
    # 针对性提示，帮助定位
    if "timeout" in str(e).lower():
        print("提示：网络无法连接到SiliconFlow，请检查网络或代理设置")
    elif "authentication" in str(e).lower():
        print("提示：API密钥错误，请检查SiliconFlow密钥")
    elif "model" in str(e).lower():
        print("提示：模型名错误，请确认SiliconFlow上的模型名称")
