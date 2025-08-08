from typing import ClassVar, Optional, Type, List
from pydantic import BaseModel
from langchain_core.tools import BaseTool
from app.utils.plot_uploader import store_text_result
from app.agents.tools.duckdb_loader import CSVToDuckDBLoader
import json

class SummaryStatsInput(BaseModel):
    columns: Optional[List[str]] = None
    metrics: Optional[List[str]] = None
    file_id: str

class SummaryStatsTool(BaseTool):
    name: ClassVar[str] = "summary_statistics"
    description: ClassVar[str] = "Returns summary statistics (e.g., mean, std, min, max) of selected columns."
    args_schema: ClassVar[Type[BaseModel]] = SummaryStatsInput

    duckdb_loader: Optional[CSVToDuckDBLoader] = None

    def _run(self, columns: Optional[List[str]] = None, metrics: Optional[List[str]] = None, file_id: str = "") -> str:
        if not self.duckdb_loader or self.duckdb_loader.conn is None:
            return "DuckDB not initialized."

        df = self.duckdb_loader.conn.execute("SELECT * FROM data").fetchdf()
        missing = [col for col in columns if col not in df.columns]
        if missing:
            return f"Invalid columns: {missing}"

        allowed_metrics = {"mean", "std", "min", "max", "median"}
        synonym_map = {
            "average": "mean", "standard deviation": "std",
            "minimum": "min", "maximum": "max"
        }
        final_metrics = []
        for m in metrics:
            norm = synonym_map.get(m.lower(), m.lower())
            if norm in allowed_metrics:
                final_metrics.append(norm)

        if not final_metrics:
            final_metrics = ["mean", "std"]

        result = {}
        for col in columns:
            result[col] = {}
            for metric in final_metrics:
                try:
                    value = getattr(df[col], metric)()
                    result[col][metric] = round(float(value), 4)
                except Exception:
                    result[col][metric] = "N/A"
        
        try:
            json_content = json.dumps({"summary_statistics": result}, indent=2)
            store_text_result(file_id, json_content)
        except Exception as e:
            return f"Summary stats calculated but failed to upload to S3: {e}"

        return f"Summary stats:\n{result}"

    def _arun(self, *args, **kwargs):
        raise NotImplementedError("Async not supported.")

