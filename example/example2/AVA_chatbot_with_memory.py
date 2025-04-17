from langchain_openai import ChatOpenAI
from settings.config import LLM_CONF
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.messages import SystemMessage, AIMessage, HumanMessage

# Bộ nhớ lưu State của Graph
from langgraph.checkpoint.memory import MemorySaver
memory = MemorySaver() # sử dụng bộ nhớ mặc định của Langgraph, khi triển khai thực tế sẽ sử dụng Redis hoặc MongoDB

llm = ChatOpenAI(
    base_url=LLM_CONF["openai"]["base_url"],
    api_key=LLM_CONF["openai"]["api_key"],
    model=LLM_CONF["openai"]["model"],
    # temperature=0,
    # stream_usage=True,
)

class State(TypedDict):
    # messages sẽ lưu trữ các tin nhắn của người dùng và AVA trong 1 turn hỏi - đáp
    messages: Annotated[list, add_messages] # hàm add_messages sẽ tự động thêm các tin nhắn vào messages khi node trả về một tin nhắn mới


graph_builder = StateGraph(State)

AVA_PROMPT = """Bạn là AVA, trợ lý số của công ty Cổ phần MISA. Nhiệm vụ của bạn là giải đáp các thắc mắc của người dùng"""

# Tất cả các node trong Langgraph sẽ nhận vào một State, và trả về giá trị update cho State.
def chatbot(state: State):
    return {"messages": [llm.invoke([SystemMessage(AVA_PROMPT)] + state["messages"])]}


graph_builder.add_node("AVA", chatbot)
graph_builder.add_edge(START, "AVA")
graph_builder.add_edge("AVA", END)

graph = graph_builder.compile(checkpointer=memory)

session_id = "qwert"
config = {"configurable": {"thread_id": session_id}}
def stream_graph_updates(user_input: str):
    for event in graph.stream(input={"messages": [{"role": "user", "content": user_input}]}, config=config):
        for value in event.values():
            print("AVA:", value["messages"][-1].content)

"""Hãy thử chat với AVA, xem nó có nhớ được lịch sử chat không"""
while True:
    try:
        user_input = input("User: ")
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break
        stream_graph_updates(user_input)
    except:
        # fallback if input() is not available
        user_input = "Bạn tên là gì?"
        print("User: " + user_input)
        stream_graph_updates(user_input)
        break