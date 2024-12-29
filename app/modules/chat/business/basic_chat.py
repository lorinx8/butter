from typing import List, Dict, Union, AsyncGenerator
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from app.core.logging import logger
from app.modules.llm.business.model_manager import ModelManager


class BasicChat:
    """基础聊天类,提供简单的模型调用功能"""

    @staticmethod
    async def chat(deploy_name: str, messages: List[Dict], stream: bool = False) -> Union[str, AsyncGenerator]:
        """
        执行聊天
        Args:
            deploy_name: 部署的模型名称
            messages: 消息列表,格式为 [{"role": xx, "content": xx}, ...]
            stream: 是否使用流式输出
        Returns:
            非流式模式返回字符串响应,流式模式返回生成器
        """
        if stream:
            return BasicChat.chat_stream(deploy_name, messages)
        return await BasicChat.chat_sync(deploy_name, messages)

    @staticmethod
    async def chat_sync(deploy_name: str, messages: List[Dict]) -> str:
        """执行同步聊天"""
        model = await ModelManager.get_model(deploy_name)
        langchain_messages = BasicChat._convert_messages(messages)
        try:
            response = await model.ainvoke(langchain_messages)
            return response.content
        except Exception as e:
            logger.error("Error in chat_sync: %s", str(e))
            raise

    @staticmethod
    async def chat_stream(deploy_name: str, messages: List[Dict]) -> AsyncGenerator[str, None]:
        """执行流式聊天"""

        langchain_messages = BasicChat._convert_messages(messages)
        model = await ModelManager.get_model(deploy_name)
        async for chunk in model.astream(langchain_messages):
            yield chunk.content

    @staticmethod
    def _convert_messages(messages: List[Dict]) -> List[Union[HumanMessage, SystemMessage, AIMessage]]:
        """Convert dict messages to LangChain message objects"""
        langchain_messages = []
        for msg in messages:
            content = msg["content"]
            if msg["role"] == "user":
                langchain_messages.append(HumanMessage(content=content))
            elif msg["role"] == "assistant":
                langchain_messages.append(AIMessage(content=content))
            elif msg["role"] == "system":
                langchain_messages.append(SystemMessage(content=content))
        return langchain_messages
