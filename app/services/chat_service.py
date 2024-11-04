from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, MessagesState, START
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from app.core.config import settings
from loguru import logger

class ChatService:
    def __init__(self):
        self.workflow = StateGraph(MessagesState)
        self.workflow.add_node("call_model", self.__call_model)
        self.workflow.add_edge(START, "call_model")
        self.memory = MemorySaver()
        self.app = self.workflow.compile(checkpointer=self.memory)   

        self.model = ChatOpenAI(
            base_url=settings.OPENAI_BASE_URL,
            api_key=settings.OPENAI_API_KEY,
            model="gpt-4o",
            temperature=0,
            max_tokens=None,    
            timeout=None,
            max_retries=2,)

    # Define the function that calls the model
    def __call_model(self, state: MessagesState):
        messages = state['messages']
        logger.info(messages)
        response = self.model.invoke(messages)
        return {"messages": [response]}

    def chat(self,  message_content: str) -> str:
        final_state = self.app.invoke({"messages": [HumanMessage(content=message_content)]}, {"configurable": {"thread_id": "42"}})  
        return final_state["messages"][-1].content