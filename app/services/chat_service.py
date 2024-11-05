import json
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, MessagesState, START
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.checkpoint.postgres import PostgresSaver
from psycopg import Connection
from loguru import logger

from app.core.config import settings
from app.services.prompt_cache_service import PromptCacheService
from app.utils import singleton

connection_kwargs = {
    "autocommit": True,
    "prepare_threshold": 0,
}

@singleton
class ChatService:
    def __init__(self):
        self.workflow = StateGraph(MessagesState)
        self.workflow.add_node("call_model", self.__call_model)
        self.workflow.add_edge(START, "call_model")

        self.conn = Connection.connect(settings.DATABASE_URI, **connection_kwargs)
        self.checkpoint = PostgresSaver(self.conn)
        self.checkpoint.setup()
        self.app = self.workflow.compile(checkpointer=self.checkpoint)   

        self.model = ChatOpenAI(
            base_url=settings.OPENAI_BASE_URL,
            api_key=settings.OPENAI_API_KEY,
            model="gpt-4o",
            temperature=0,
            max_tokens=None,    
            timeout=None,
            streaming=True,
            max_retries=2,)
        
        self.prompt_cache_service = PromptCacheService()

    # Define the function that calls the model
    def __call_model(self, state: MessagesState, config: dict):
        logger.info(f'call_model: {config}')
        prompt_id = config.get("metadata").get("prompt_id") 
        messages = state['messages']
        # 判断从历史状态中来的消息中，第一条是不是系统消息
        if not messages or not isinstance(messages[0], SystemMessage):
            # 构建系统消息
            system_message = SystemMessage(content=self.__find_prompt(prompt_id))
            messages = [system_message] + (messages if isinstance(messages, list) else [messages])
        response = self.model.invoke(messages)
        return {"messages": [response]}
    
    # 从缓存中查找系统提示词
    def __find_prompt(self, prompt_id: str) -> str:
        logger.info(f'find prompt: {prompt_id}')
        prompt = self.prompt_cache_service.get(prompt_id)
        return prompt.content
    
    # 聊天(非流式)
    # prompt_id: 提示词ID
    # session_id: 会话ID
    # message_content: 消息内容
    def chat(self, prompt_id: str, session_id: str, message_content: str) -> str:
        # 构建输入消息，包括提示词
        input_message = HumanMessage(content=message_content)
        config = {
            "configurable": {"thread_id": session_id},
            "prompt_id": prompt_id,
        }
        final_state = self.app.invoke({"messages": input_message}, config=config)  
        return final_state["messages"][-1].content

    async def chat_stream(self, prompt_id: str, session_id: str, message_content: str):
        input_message = HumanMessage(content=message_content)
        config = {
            "configurable": {"thread_id": session_id},
            "prompt_id": prompt_id,
        }
        async for msg, _ in self.app.astream({"messages": [input_message]}, stream_mode="messages", config=config):
            yield json.dumps({"content": msg.content})
        yield json.dumps({"content": "[END]"})
