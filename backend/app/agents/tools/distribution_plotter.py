from typing import Optional, Type, ClassVar
from pydantic import BaseModel
from langchain.tools import BaseTool
import matplotlib.pyplot as plt
import os
from uuid import uuid4
from app.agents.tools.duckdb_loader import CSVToDuckDBLoader
import matplotlib
matplotlib.use('Agg') 
import pandas as pd
import matplotlib.pyplot as plt
from app.utils.plot_uploader import upload_plot_to_s3


class DistributionPlotInput(BaseModel):
    column: str
    file_id: str


class DistributionPlotTool(BaseTool):
    name: ClassVar[str] = "distribution_plot"
    description: ClassVar[str] = "Plot the distribution of a numerical column in the dataset"
    args_schema: ClassVar[Type[BaseModel]] = DistributionPlotInput

    duckdb_loader: Optional[CSVToDuckDBLoader] = None

    def _run(self, column: str , file_id: str) -> str:
        if not self.duckdb_loader or self.duckdb_loader.conn is None:
            return "DuckDB not initialized."

        try:
            df = self.duckdb_loader.conn.execute("SELECT * FROM data").fetchdf()

            if column not in df.columns:
                return f"Column '{column}' not found in the data"
            
            if not pd.api.types.is_numeric_dtype(df[column]):
                return f"Column '{column}' is not numeric and cannot be plotted as a distribution."

            plt.figure(figsize=(12, 6))
            plt.style.use("ggplot")

            plt.hist(df[column].dropna(), bins=30, color='blue', alpha=0.7)
            plt.xlabel(column)
            plt.ylabel("Frequency")
            plt.title(f"Distribution of {column}", fontsize=14)
            plt.tight_layout()
            plt.grid(True)

            fig = plt.gcf()
            s3_url = upload_plot_to_s3(fig, file_id, prefix="dist_plots")
            plt.close(fig)

            if s3_url:
                return s3_url
            else:
                return "Plot generated but failed to upload to S3."
        
        except Exception as e:
            return f"Error generating distribution plot: {str(e)}"
        
    def _arun(self, *args, **kwargs):
        raise NotImplementedError("Async not supported for this tool.")
