from langchain_core.runnables import Runnable
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.language_models import BaseChatModel

from typing import Dict

tool_names = ["sql_executor", "distribution_plot", "trend_plot", "summary_stats"]

TOOL_ROUTER_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are an intelligent tool selector for a CSV analysis agent. "
        "Given a user question, choose the most appropriate tool to answer it from this list:\n\n"
        f"{', '.join(tool_names)}\n\n"
        "Respond ONLY with the tool name. No explanation. No extra words."
    ),
    MessagesPlaceholder("chat_history"),
    ("human", "{question}")
])

def build_tool_selector_node(llm: BaseChatModel) -> Runnable:
    chain = TOOL_ROUTER_PROMPT | llm

    def tool_selector_node(state: Dict) -> Dict:
        question = state["question"]
        tool_name = chain.invoke({"question": question, "chat_history": []})

        # Just in case it's a Message object (older versions)
        if hasattr(tool_name, "content"):
            tool_name = tool_name.content

        tool_name = tool_name.strip().lower()

        print("🧭 Tool selected by LLM:", tool_name)  # Optional debug

        return {**state, "tool_to_use": tool_name}

    return tool_selector_node