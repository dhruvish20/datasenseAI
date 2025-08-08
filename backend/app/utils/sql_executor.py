from typing import Optional, ClassVar , Type
from pydantic import BaseModel
from langchain_core.tools import BaseTool
from app.agents.tools.duckdb_loader import CSVToDuckDBLoader
from app.utils.plot_uploader import store_text_result
import json

class SQLQueryInput(BaseModel):
    query: str
    file_id: str

class SQLExecutorTool(BaseTool):
    name: ClassVar[str] = "sql_executor"
    description: ClassVar[str] = "Executes SQL queries on a DuckDB table loaded from a CSV file."
    args_schema : ClassVar[Type[BaseModel]] = SQLQueryInput
    duckdb_loader: Optional[CSVToDuckDBLoader] = None


    def _run(self, query, file_id: str):
        if not self.duckdb_loader or self.duckdb_loader.conn is None:
            return "DuckDB not initialized. Please load a CSV first."

        try:
            result_df = self.duckdb_loader.query(query)
            result_str = result_df.to_string(index=False)

            # Store the result in S3
            store_text_result(file_id, result_df.to_json(orient="records", indent=2), filename="sql_result.json")

            return f"SQL query executed successfully. Result:\n{result_str}"
        except Exception as e:
            return f"SQL execution failed: {str(e)}"
        
    def _arun(self, *args, **kwargs):
        raise NotImplementedError("Async not supported for this tool.")
    


