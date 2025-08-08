from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable
from langchain_core.output_parsers import JsonOutputParser
from typing import Dict, List, Optional
from pydantic import BaseModel


def build_stats_input_parser(llm: BaseChatModel, column_names: list[str]) -> Runnable:
    column_list_str = ", ".join(column_names)

    prompt = ChatPromptTemplate.from_messages([
        ("system", (
            "You are a helpful assistant that extracts structured inputs for computing summary statistics on a dataset.\n"
            f"The available columns are: {column_list_str}.\n"
            "Supported metrics include: mean, median, min, max, std (standard deviation).\n"
            "Given a question, extract:\n"
            "- 'columns': list of relevant columns (required)\n"
            "- 'metrics': list of metrics to compute (optional)\n\n"
            "Respond ONLY as a JSON object with keys 'columns' and 'metrics'."
        )),
        ("human", "{question}")
    ])

    parser = JsonOutputParser()
    return prompt | llm | parser