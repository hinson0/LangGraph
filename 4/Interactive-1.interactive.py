{
    "step": 1,
    "timestamp": "2025-12-20T03:10:45.412620+00:00",
    "type": "task",  # 表示节点执行的开始
    "payload": {
        "id": "b677bb1d-faca-ce73-fda2-2545d00d2f44",
        "name": "generate_a_joke",  # 节点名称
        "input": {"topic": "天气"},  # 节点输入
        "triggers": ("branch:to:generate_a_joke",),  # 出发条件
    },
}  # pyright: ignore[reportUnusedExpression]
{
    "step": 1,
    "timestamp": "2025-12-20T03:10:46.286565+00:00",
    "type": "task_result",  # 表示节点执行的结束
    "payload": {
        "id": "b677bb1d-faca-ce73-fda2-2545d00d2f44",
        "name": "generate_a_joke",  # 节点名称
        "error": None,
        "result": {  # 节点结果
            "joke": AIMessage(
                content="您好，我目前无法直接查询实时天气情况。不过，您可以通过查询天气的网站或应用程序（如中国气象局官网、微博天气、UU天气等）来获取今天的江西抚州天气情况。这些平台通常能够提供详细的气温、天气状况、湿度、风速和紫外线指数等信息。希望您能找到满意的信息。",
                additional_kwargs={"refusal": None},
                response_metadata={
                    "token_usage": {
                        "completion_tokens": 71,
                        "prompt_tokens": 35,
                        "total_tokens": 106,
                        "completion_tokens_details": None,
                        "prompt_tokens_details": None,
                    },
                    "model_provider": "openai",
                    "model_name": "Qwen/Qwen2.5-7B-Instruct",
                    "system_fingerprint": "",
                    "id": "019b39bcfd9ecb0ed3dfc06122adc396",
                    "finish_reason": "stop",
                    "logprobs": None,
                },
                id="lc_run--019b39bc-fca5-7541-abfb-2b2f7db63662-0",
                usage_metadata={
                    "input_tokens": 35,
                    "output_tokens": 71,
                    "total_tokens": 106,
                    "input_token_details": {},
                    "output_token_details": {},
                },
            )
        },
        "interrupts": [],
    },
}  # pyright: ignore[reportUnusedExpression]
