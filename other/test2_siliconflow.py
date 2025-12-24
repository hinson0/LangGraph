from openai import OpenAI

# 增加超时时间配置，便于排查（可选）
import httpx

# 初始化客户端：显式指定SiliconFlow的地址、密钥，同时设置超时时间
client = OpenAI(
    api_key="sk-szyjzwvtikkxrxfvazgzsyetseeetiofncpiowmanfvkgcwd",  # 替换为真实的SiliconFlow密钥
    base_url="https://api.siliconflow.cn/v1",  # SiliconFlow的核心地址
    # 可选：设置更长的超时时间（比如30秒），避免因网络慢导致超时
    http_client=httpx.Client(timeout=30.0),
)

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
