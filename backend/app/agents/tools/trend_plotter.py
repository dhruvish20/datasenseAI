from typing import ClassVar, Optional, Type
from pydantic import BaseModel
from langchain.tools import BaseTool
from app.agents.tools.duckdb_loader import CSVToDuckDBLoader
from app.utils.plot_uploader import upload_plot_to_s3
import matplotlib
matplotlib.use('Agg')  
import matplotlib.pyplot as plt
import pandas as pd


class TrendPlotInput(BaseModel):
    y: str
    x: Optional[str] = None
    file_id: str


class TrendPlotTool(BaseTool):
    name: ClassVar[str] = "trend_plot"
    description: ClassVar[str] = "Plot trends in numerical data"
    args_schema: ClassVar[Type[BaseModel]] = TrendPlotInput
    duckdb_loader: Optional[CSVToDuckDBLoader] = None

    def _run(self, y: str, file_id: str, x: Optional[str] = None) -> str:
        if not self.duckdb_loader or self.duckdb_loader.conn is None:
            return "DuckDB not initialized."

        try:
            df = self.duckdb_loader.conn.execute("SELECT * FROM data").fetchdf()

            if y not in df.columns:
                return f"Column '{y}' not found in the data."
            if x and x not in df.columns:
                return f"Column '{x}' not found in the data."

            plt.figure(figsize=(12, 6))
            plt.style.use("ggplot")

            title = f"{y} over {x}" if x else f"{y} Trend (Row-wise)"

            if x:
                if pd.api.types.is_datetime64_any_dtype(df[x]) or "date" in x.lower():
                    df[x] = pd.to_datetime(df[x], errors="coerce")
                    df = df.dropna(subset=[x, y])
                    df = df.sort_values(x)
                    df.set_index(x, inplace=True)
                    df = df.resample("W").sum(numeric_only=True)
                    plt.plot(df.index, df[y], marker='o', linewidth=2)
                    plt.xlabel(x)

                elif pd.api.types.is_numeric_dtype(df[x]):
                    df = df.dropna(subset=[x, y])
                    df = df.sort_values(x)
                    plt.plot(df[x], df[y])
                    plt.xlabel(x)

                else:
                    df = df.dropna(subset=[x, y])
                    grouped = df.groupby(x)[y].mean().reset_index()
                    plt.bar(grouped[x], grouped[y])
                    plt.xlabel(x)

            else:
                df = df.dropna(subset=[y])
                plt.plot(df[y])
                plt.xlabel("Index")

            plt.ylabel(y)
            plt.title(title, fontsize=14)
            plt.tight_layout()
            plt.grid(True)

            fig = plt.gcf()
            s3_url = upload_plot_to_s3(fig, file_id=file_id, prefix="trend_plots")  # ✅ Removed trailing slash
            plt.close(fig)

            return s3_url if s3_url else "Plot generated but failed to upload to S3."

        except Exception as e:
            return f"Plotting failed: {str(e)}"

    def _arun(self, *args, **kwargs):
        raise NotImplementedError("Async not supported.")
