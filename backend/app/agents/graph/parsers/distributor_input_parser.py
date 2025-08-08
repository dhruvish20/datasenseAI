from langchain_core.language_models import BaseChatModel
from langchain_core.runnables import Runnable
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser


def build_distributor_input_parser(llm: BaseChatModel, column_names: list[str]) -> Runnable:
    column_names =  ", ".join(column_names)
    prompt = ChatPromptTemplate.from_messages([
        ("system", (
            "You are a helpful assistant that extracts structured arguments for distribution plots.\n"
            f"The column names in the dataset are: {column_names}.\n"
            "Based on the user's input, extract:\n"
            "- 'column': the column to plot (required)\n\n"
            "Respond ONLY as a JSON object with key: 'column'. Do not include any explanation."
        )),
        ("human", "{question}")
    ])

    parser = JsonOutputParser()
    return prompt | llm | parser