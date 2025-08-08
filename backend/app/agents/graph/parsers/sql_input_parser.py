from langchain_core.language_models import BaseChatModel
from langchain_core.runnables import Runnable
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

def sql_input_parser(llm: BaseChatModel, column_names: list[str]) -> Runnable:
    column_list_str = ", ".join(column_names)

    prompt = ChatPromptTemplate.from_messages([
        ("system", (
            "You are a helpful assistant that extracts structured arguments for SQL queries.\n"
            "The table name is: `data`.\n"
            f"The column names in the dataset are: {column_list_str}.\n"
            "Based on the user's input, extract:\n"
            "- 'query': the SQL query to execute (required)\n\n"
            "Use only the table name `data` in the query.\n"
            "Do not invent or hallucinate column or table names.\n"
            "Respond ONLY as a JSON object with key: 'query'."
        )),
        ("human", "{question}")
    ])


    parser = JsonOutputParser()  
    return prompt | llm | parser