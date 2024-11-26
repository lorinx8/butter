from dataclasses import dataclass
from typing import Optional
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, MessagesState, START
from langchain_core.messages import HumanMessage, SystemMessage, trim_messages
from langgraph.checkpoint.postgres import PostgresSaver
from psycopg import Connection
import json
from app.core.config import settings
from app.core.logging import logger


@dataclass
class BotConfig:
    """标准机器人配置"""
    deploy_name: str               # 模型部署标识
    provider_code: str             # 模型提供方标识
    model_name: str                # 模型名称
    prompt_template: str           # 提示词模板内容
    memory_enable: bool = False    # 是否启用记忆
    memory_strategy: Optional[str] = None  # 记忆策略 (tokens/messages)
    memory_max_tokens: Optional[int] = None  # 最大token数
    memory_max_rounds: Optional[int] = None  # 最大消息轮数
    temperature: float = 0.7       # 温度
    max_tokens: int = 2000        # 最大token数
    max_retries: int = 2          # 最大重试次数


class BotStandard:
    """标准机器人实现"""

    def __init__(self, config: BotConfig):
        self.config = config
        self.workflow = StateGraph(MessagesState)
        self.workflow.add_node("call_model", self.__call_model)
        self.workflow.add_edge(START, "call_model")

        self.checkpoint = None
        if self.config.memory_enable:
            self.checkpoint = self._create_checkpoint()

        self.app = self.workflow.compile(checkpointer=self.checkpoint)

        # 初始化模型
        self.model = self._create_model()

    def _create_checkpoint(self):
        """初始化检查点"""
        # 初始化数据库连接
        connection_kwargs = {
            "autocommit": True,
            "prepare_threshold": 0,
        }
        conn = Connection.connect(
            settings.DATABASE_URI, **connection_kwargs)
        checkpoint = PostgresSaver(conn)
        checkpoint.setup()
        return checkpoint

    def __call_model(self, state: MessagesState, config: dict):
        """调用模型"""
        messages = state['messages']

        # 检查并添加系统提示词
        if not messages or not isinstance(messages[0], SystemMessage):
            system_message = SystemMessage(content=self.config.prompt_template)
            messages = [system_message] + \
                (messages if isinstance(messages, list) else [messages])

        # 根据记忆策略处理消息
        if self.config.memory_enable:
            messages = self._apply_memory_strategy(messages)

        # 调用模型
        response = self.model.invoke(messages)
        return {"messages": [response]}

    def _apply_memory_strategy(self, messages: list) -> list:
        """应用记忆策略"""
        if not self.config.memory_strategy:
            return messages

        if self.config.memory_strategy == "tokens":
            return trim_messages(
                messages,
                strategy="token",
                token_counter=self.model,
                max_tokens=self.config.memory_max_tokens or self.config.max_tokens,
                include_system=True,
                start_on="human",
                end_on=("human", "tool"),
            )
        elif self.config.memory_strategy == "messages":
            # 保留系统消息和最近的N轮对话
            system_message = messages[0]
            other_messages = messages[1:]
            max_messages = (
                self.config.memory_max_rounds or 10) * 2  # 每轮包含问答两条消息
            recent_messages = other_messages[-max_messages:] if len(
                other_messages) > max_messages else other_messages
            return [system_message] + recent_messages

        return messages

    async def chat(self, session_id: str, message_content: str) -> str:
        """同步聊天"""
        input_message = HumanMessage(content=message_content)
        config = {
            "configurable": {"thread_id": session_id}
        }
        final_state = self.app.invoke(
            {"messages": input_message}, config=config)
        return final_state["messages"][-1].content

    async def chat_stream(self, session_id: str, message_content: str):
        """流式聊天"""
        input_message = HumanMessage(content=message_content)
        config = {
            "configurable": {"thread_id": session_id}
        }
        async for msg, _ in self.app.astream(
            {"messages": [input_message]},
            stream_mode="messages",
            config=config
        ):
            yield json.dumps({"content": msg.content})
        yield json.dumps({"content": "[END]"})

    def __del__(self):
        """清理资源"""
        if hasattr(self, 'conn'):
            self.conn.close()

    def _create_model(self) -> ChatOpenAI:
        """创建模型实例"""
        if self.config.provider_code == "openai":
            return ChatOpenAI(
                model=self.config.model_name,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                max_retries=self.config.max_retries
            )
        # TODO: 支持其他模型提供商
        raise ValueError(
            f"Unsupported model provider: {self.config.provider_code}")
