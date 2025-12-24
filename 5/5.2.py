# %% 使用InMemoryStore实例化记忆存储

from langgraph.store.memory import InMemoryStore

ms = InMemoryStore()


# %% 使用put()方法来保存记忆
import uuid
from langgraph.store.memory import InMemoryStore

store = InMemoryStore()

# namespace
namespace_for_user_data = ("user_id", "user_info")

# key
memory_key = str(uuid.uuid4())

# value
memory_value = {"user_name": "yzb", "gender": "male", "age": 38}

a = store.put(namespace_for_user_data, memory_key, memory_value)


# %% get
store.get(namespace_for_user_data, memory_key)

# %% search
all_user_memories = store.search(namespace_for_user_data)
for record in all_user_memories:
    print(record.dict())

# %% 5-11 自定义TextFileStore示例的用法

from langgraph.store.base import (
    BaseStore,
    Item,
    SearchItem,
    Op,
    Result,
    IndexConfig,
    NamespacePath,
)
from typing import Any
import json
import os
import uuid
from datetime import datetime, timezone


class TextFileStore(BaseStore):
    def __init__(self, base_dir: str):
        self.base_dir = base_dir

    def put(
        self,
        namespace: NamespacePath,
        key: str,
        value: dict[str, Any],
        index: bool | list[str] = True,
    ) -> None:
        """
        将键值对存储到指定命名空间的持久化存储中

        参数:
            namespace (NamespacePath): 命名空间路径，用于组织和隔离不同的数据集合
            key (str): 存储数据的唯一标识符，将作为文件名使用
            value (dict[str, Any]): 要存储的实际数据，以字典形式提供
            index (bool | list[str], 可选): 指定是否创建索引或要索引的字段列表
                                        默认为 True，表示为所有字段创建索引

        功能:
            1. 根据基础目录和命名空间路径创建目录结构
            2. 将值以 JSON 格式写入到命名空间路径下的 {key}.json 文件中
            3. 如果需要，创建相应的索引以提高查询效率

        异常:
            可能抛出文件操作相关的异常，如权限不足或磁盘空间不足等
        """
        namespace_path = os.path.join(self.base_dir, *namespace)
        os.makedirs(namespace_path, exist_ok=True)
        file_path = os.path.join(namespace_path, f"{key}.json")
        with open(file_path, "w") as f:
            json.dump(value, f)

    def get(self, namespace: NamespacePath, key: str) -> Item | None:
        """
        从指定命名空间中根据键获取存储的项目

        参数:
            namespace (NamespacePath): 命名空间路径，用于定位数据存储位置
            key (str): 要获取的项目的唯一标识符

        返回:
            Item | None: 如果找到对应的项目则返回Item对象，否则返回None

        功能:
            1. 构建完整的文件路径
            2. 检查文件是否存在
            3. 如果存在，读取JSON格式的数据
            4. 获取文件的创建时间和更新时间
            5. 返回包含所有信息的Item对象

        异常:
            可能抛出文件读取相关的异常，如权限不足或JSON解析错误等
        """
        file_path = os.path.join(self.base_dir, *namespace, f"{key}.json")
        if not os.path.exists(file_path):
            return None
        with open(file_path, "r") as f:
            value = json.load(f)
        created_at = datetime.fromtimestamp(
            os.path.getctime(file_path), tz=timezone.utc
        )
        updated_at = datetime.fromtimestamp(
            os.path.getmtime(file_path), tz=timezone.utc
        )

        return Item(
            namespace=namespace,
            key=key,
            value=value,
            created_at=created_at,
            updated_at=updated_at,
        )

    def batch(self): ...

    def abatch(self) -> list[Result]: ...


# %% 自定义TextFileStore的示例用法
file_store = TextFileStore(base_dir="./my_filestore")
file_store.put(
    ("user_data",), "user_profile_1", {"name": "自定义存储用户", "preference": "files"}
)
retrieved_item = file_store.get(("user_data",), "user_profile_1")
print(retrieved_item.dict())  # type: ignore

# %% 5-8使用BGE-M3向量化模型配置InMemoryStore以进行语义搜索
from langchain_openai import OpenAIEmbeddings
from langgraph.store.memory import InMemoryStore

# 初始化BGE-M3向量化模型
embeddings = OpenAIEmbeddings(model="BAAI/bge-m3")

# 使用语义搜索索引配置InMemoryStore
store_with_semantic_search = InMemoryStore(
    index={
        "embed": embeddings.embed_documents,
        "dims": 1024,
        "fields": ["memory_content"],
    }  # pyright: ignore[reportArgumentType]
)

# %% 5-9 使用put保存记忆
store_with_semantic_search.put(
    ("user_789", "food_memories"), "memory_1", {"memory_content": "我很喜欢吃辣椒炒肉"}
)

store_with_semantic_search.put(
    ("user_789", "system_metadata"),
    "memory_2",
    {"memory_content": "用户入职完成。", "status": "completed"},
    index=False,
)

store_with_semantic_search.put(
    ("user_789", "restaurant_reviews"),
    "memory_3",
    {"memory_content": "服务很慢，食物不错", "context": "对餐厅的评价"},
    index=["context"],
)

# %% 5-10 使用search执行语义搜索

semantic_search_results = store_with_semantic_search.search(
    ("user_789", "food_memories"), query="喜欢那种食物", limit=2
)
# [
#     Item(namespace=['user_789', 'food_memories'], key='memory_1', value={'memory_content': '我很喜欢吃辣椒炒肉'}, created_at='2025-12-23T02:29:44.279983+00:00', updated_at='2025-12-23T02:29:44.279988+00:00', score=0.6334337078508484)
# ]

record = semantic_search_results[0]
record.key, record.value, record.score
# ('memory_1', {'memory_content': '我很喜欢吃辣椒炒肉'}, 0.6334337078508484

# %%
results = store_with_semantic_search.search(("user_789", "system_metadata"))
results
# [
#     Item(namespace=['user_789', 'system_metadata'], key='memory_2', value={'memory_content': '用户入职完成。', 'status': 'completed'}, created_at='2025-12-23T02:29:44.280079+00:00', updated_at='2025-12-23T02:29:44.280080+00:00', score=None)
# ]

# %%
results2 = store_with_semantic_search.search(
    ("user_789", "system_metadata"), query="用户入职情况"
)
results2

# %%
results3 = store_with_semantic_search.search(
    ("user_789", "restaurant_reviews"), query="服务"
)
results3
# [
#     Item(namespace=['user_789', 'restaurant_reviews'], key='memory_3', value={'memory_content': '服务很慢，食物不错', 'context': '对餐厅的评价'}, created_at='2025-12-23T02:54:34.272481+00:00', updated_at='2025-12-23T02:54:34.272484+00:00', score=0.27773786969578934)
# ]

"""
还是可以搜索到撒。什么情况。。。
"""

# %%
results4 = store_with_semantic_search.search(
    ("user_789", "restaurant_reviews"), query="评论"
)
results4
# [
#     Item(namespace=['user_789', 'restaurant_reviews'], key='memory_3', value={'memory_content': '服务很慢，食物不错', 'context': '对餐厅的评价'}, created_at='2025-12-23T02:54:34.272481+00:00', updated_at='2025-12-23T02:54:34.272484+00:00', score=0.1516938458392215)
# ]
