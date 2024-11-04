from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, MessagesState, START
from langchain_core.messages import HumanMessage
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class ChatService:
    def __init__(self):
        workflow = StateGraph(MessagesState)
        workflow.add_node("call_model", self.__call_model)
        workflow.add_edge(START, "call_model")
        self.app = workflow.compile()   

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
        response = self.model.invoke(messages)
        return {"messages": [response]}

    def chat(self,  message_content: str) -> str:
        final_state = self.app.invoke({"messages": [HumanMessage(content=message_content)]})
        logger.info(final_state)    
        return final_state["messages"][-1].content