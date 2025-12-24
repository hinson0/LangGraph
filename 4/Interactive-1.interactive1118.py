{
    "step": 1,
    "timestamp": "2025-12-20T03:18:22.050116+00:00",
    "type": "task",
    "payload": {
        "id": "d85287ab-d9a1-fc65-eb7e-0339ca989229",
        "name": "generate_a_joke",
        "input": {"topic": "天气"},
        "triggers": ("branch:to:generate_a_joke",),
    },
}  # pyright: ignore[reportUnusedExpression]
{
    "step": 1,
    "timestamp": "2025-12-20T03:18:23.486118+00:00",
    "type": "task_result",
    "payload": {
        "id": "d85287ab-d9a1-fc65-eb7e-0339ca989229",
        "name": "generate_a_joke",
        "error": None,
        "result": {
            "joke": AIMessage(
                content="我需要您提供具体日期，因为天气情况会每天发生变化。如果您不指定日期，我将提供最近一天的数据或者您可以访问气象网站或使用相关的天气应用查看最新的天气预报。您可以在网上查找“抚州今天天气”来获取最新的天气信息。如果是在气象网站或应用上，通常会直接显示出当地的温度、天气状况、湿度、风速等信息。",
                additional_kwargs={"refusal": None},
                response_metadata={
                    "token_usage": {
                        "completion_tokens": 80,
                        "prompt_tokens": 35,
                        "total_tokens": 115,
                        "completion_tokens_details": None,
                        "prompt_tokens_details": None,
                    },
                    "model_provider": "openai",
                    "model_name": "Qwen/Qwen2.5-7B-Instruct",
                    "system_fingerprint": "",
                    "id": "019b39c3f5c35a6115541534e685704a",
                    "finish_reason": "stop",
                    "logprobs": None,
                },
                id="lc_run--019b39c3-f462-7760-b866-2fc203e17ff5-0",
                usage_metadata={
                    "input_tokens": 35,
                    "output_tokens": 80,
                    "total_tokens": 115,
                    "input_token_details": {},
                    "output_token_details": {},
                },
            )
        },
        "interrupts": [],
    },
}  # pyright: ignore[reportUnusedExpression]
