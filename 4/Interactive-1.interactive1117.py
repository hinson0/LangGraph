{
    "step": 1,
    "timestamp": "2025-12-20T03:17:00.416084+00:00",
    "type": "task",
    "payload": {
        "id": "e86d5023-b030-d2ef-2f51-e30dc6c5f090",
        "name": "generate_a_joke",
        "input": {"topic": "天气"},
        "triggers": ("branch:to:generate_a_joke",),
    },
}  # pyright: ignore[reportUnusedExpression]
{
    "step": 1,
    "timestamp": "2025-12-20T03:17:01.945574+00:00",
    "type": "task_result",
    "payload": {
        "id": "e86d5023-b030-d2ef-2f51-e30dc6c5f090",
        "name": "generate_a_joke",
        "error": None,
        "result": {
            "joke": AIMessage(
                content="为了提供今天江西抚州的天气信息，我需要访问最新的气象数据。不过，作为一个无法实时访问外部数据的模型，我无法直接获取最新的天气情况。建议您查看本地气象站或可靠的天气预报网站、App（如中国气象局官网站、微博、微信等官方渠道）以获取最准确的信息。",
                additional_kwargs={"refusal": None},
                response_metadata={
                    "token_usage": {
                        "completion_tokens": 70,
                        "prompt_tokens": 35,
                        "total_tokens": 105,
                        "completion_tokens_details": None,
                        "prompt_tokens_details": None,
                    },
                    "model_provider": "openai",
                    "model_name": "Qwen/Qwen2.5-7B-Instruct",
                    "system_fingerprint": "",
                    "id": "019b39c2b739e91895214da6589e0a9a",
                    "finish_reason": "stop",
                    "logprobs": None,
                },
                id="lc_run--019b39c2-b581-7d83-8a86-d807ce058c7d-0",
                usage_metadata={
                    "input_tokens": 35,
                    "output_tokens": 70,
                    "total_tokens": 105,
                    "input_token_details": {},
                    "output_token_details": {},
                },
            )
        },
        "interrupts": [],
    },
}  # pyright: ignore[reportUnusedExpression]
