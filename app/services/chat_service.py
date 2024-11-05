import json
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, MessagesState, START
from langchain_core.messages import HumanMessage, SystemMessage, trim_messages
from langgraph.checkpoint.postgres import PostgresSaver
from psycopg import Connection
from loguru import logger
from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.config import settings
from app.utils import singleton
from app.repositories.prompt_repository import PromptRepository
from app.core.database import get_db

connection_kwargs = {
    "autocommit": True,
    "prepare_threshold": 0,
}

@singleton
class ChatService:
    def __init__(self, db: Session = Depends(get_db)):
        self.model_name = "gpt-4o"
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
            model=self.model_name,
            temperature=0,
            max_tokens=16000,    
            timeout=None,
            streaming=True,
            max_retries=2,)
        
        self.prompt_repository = PromptRepository(db)

    # Define the function that calls the model
    def __call_model(self, state: MessagesState, config: dict):
        prompt_id = config.get("metadata").get("prompt_id") 
        messages = state['messages']
        # 判断从历史状态中来的消息中，第一条是不是系统消息
        if not messages or not isinstance(messages[0], SystemMessage):
            # 构建系统消息
            prompt = self.__find_prompt(prompt_id)
            if not prompt or prompt == "":
                logger.warning(f'prompt not found: {prompt_id}')
            else:
                system_message = SystemMessage(content=prompt)
                messages = [system_message] + (messages if isinstance(messages, list) else [messages])
        messages = trim_messages(messages, 
                                 strategy="last",
                                 token_counter=self.model,
                                 max_tokens=self.model.max_tokens, 
                                 include_system=True, 
                                 start_on="human",
                                 end_on=("human", "tool"),)
        response = self.model.invoke(messages)
        return {"messages": [response]}
    
    # 从缓存中查找系统提示词
    def __find_prompt(self, prompt_id: str) -> str:
        prompt = self.prompt_repository.get_by_id(prompt_id)
        return prompt.content if prompt else ""
    
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
