# 创建一个简单的提示词优化示例
from langmem import create_prompt_optimizer

# 创建提示词优化器实例
optimizer = create_prompt_optimizer(
    "openai:Qwen/Qwen2.5-7B-Instruct",  # 使用的模型
    kind="prompt_memory",  # 优化类型
    config={"max_reflection_steps": 5, "min_reflection_steps": 1},
)

# 定义对话轨迹，用于训练和优化提示词
trajectories = [
    # 示例1: 没有标注的对话
    (
        [
            {"role": "user", "content": "请告诉我Python的优点"},
            {"role": "assistant", "content": "Python是一种易于学习和使用的编程语言"},
            {"role": "user", "content": "能详细说说它的库支持吗？"},
        ],
        None,  # 没有反馈
    ),
    # 示例2: 带有反馈的对话
    (
        [
            {"role": "user", "content": "Python有哪些流行的库"},
            {
                "role": "assistant",
                "content": "Python有很多流行的库，比如NumPy，pandas等",
            },
        ],
        {"score": 0.8, "comment": "可以增加库的应用场景和更多细节"},
    ),
    # 示例3: 另一个带反馈的对话
    (
        [
            {"role": "user", "content": "如何学习Python？"},
            {
                "role": "assistant",
                "content": "首先安装Python，然后学习基础语法，多练习编程。",
            },
        ],
        {"score": 0.9, "comment": "回答简洁明了，但可以添加一些学习资源推荐"},
    ),
]

# 初始提示词
initial_prompt = "你是一个乐于助人的Python编程助手"

# 执行优化
optimized_prompt = optimizer.invoke(
    {"trajectories": trajectories, "prompt": initial_prompt}
)

print("优化后的提示词:", optimized_prompt)
