from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from app.agents.tools.trend_plotter import TrendPlotInput
from langchain_core.runnables import Runnable
from langchain_core.output_parsers import JsonOutputParser


def build_trend_input_parser(llm: BaseChatModel, column_names: list[str]) -> Runnable:
    column_list_str = ", ".join(column_names)

    prompt = ChatPromptTemplate.from_messages([
        ("system", (
            "You are a helpful assistant that extracts structured arguments for plotting trends in tabular data.\n"
            f"The column names in the dataset are: {column_list_str}.\n"
            "Based on the user's input, extract:\n"
            "- 'y': the column to plot on the Y-axis (required)\n"
            "- 'x': the column to plot on the X-axis (optional)\n\n"
            "Respond ONLY as a JSON object with keys: 'y' and 'x'. Do not include any explanation."
        )),
        ("human", "{question}")
    ])

    parser = JsonOutputParser()  # Get plain dict
    return prompt | llm | parser