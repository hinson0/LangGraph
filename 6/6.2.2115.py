from langsmith import traceable
from openai import Client
from langchain_openai import ChatOpenAI

openai = Client()


@traceable
def format_prompt(subject):
    return [
        {
            "role": "system",
            "content": "You are a helpful assistant.",
        },
        {
            "role": "user",
            "content": f"What's a good name for a store that sells {subject}?",
        },
    ]


@traceable(run_type="llm")
def invoke_llm(messages):
    llm = ChatOpenAI(model="Qwen/Qwen2.5-7B-Instruct", temperature=0)
    return llm.invoke(messages)


@traceable
def parse_output(response):
    return response.choices[0].message.content


@traceable
def run_pipeline():
    messages = format_prompt("colorful socks")
    response = invoke_llm(messages)
    return parse_output(response)


run_pipeline()
