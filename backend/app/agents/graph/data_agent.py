from langchain_community.chat_models import ChatOpenAI
from app.agents.graph.graph_builder import build_graph
from app.agents.tools.duckdb_loader import CSVToDuckDBLoader
from app.agents.state import AgentState
from app.utils.sql_executor import SQLExecutorTool
from app.agents.tools.distribution_plotter import DistributionPlotTool
from app.agents.tools.trend_plotter import TrendPlotTool
from app.agents.tools.summary_stats import SummaryStatsTool
from typing import Optional
from dotenv import load_dotenv
load_dotenv()
import os

class DataAgent:
    def __init__(self, csv_path: str, file_id: str = None):
        self.csv_path = csv_path
        self.file_id = file_id
        self.loader = CSVToDuckDBLoader(file_id= self.file_id)
        self.loader.load_csv(csv_path)

        self.tools = [
            SQLExecutorTool(duckdb_loader=self.loader),
            DistributionPlotTool(duckdb_loader=self.loader),
            TrendPlotTool(duckdb_loader=self.loader),
            SummaryStatsTool(duckdb_loader=self.loader)
        ]

        self.llm= ChatOpenAI(
            temperature=0,
            model="llama3-70b-8192",
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            openai_api_base=os.getenv("OPENAI_API_BASE")
        )

        self.graph = build_graph(self.llm, self.loader)


    def run(self, question: str, file_id: Optional[str] = None):
        input_state: AgentState = {
            "question": question,
            "file_id": file_id,
            "tool_to_use": None,
            "answer": None,
        }

        final_state = self.graph.invoke(input_state)
        print("Final State:", final_state)
        return final_state["answer"]
    
