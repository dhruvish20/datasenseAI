import duckdb
import pandas as pd

class CSVToDuckDBLoader:
    def __init__(self, file_id: str = None):
        self.conn = None
        self.file_id = file_id

    def load_csv(self, csv_path: str):
        try:
            df = pd.read_csv(csv_path, encoding="latin1", on_bad_lines="skip")  # Handles malformed lines
        except Exception as e:
            raise Exception(f"Pandas failed to read CSV: {e}")

        try:
            self.conn = duckdb.connect()
            self.conn.register("df_view", df)  # Create in-memory view
            self.conn.execute("CREATE TABLE data AS SELECT * FROM df_view")
        except Exception as e:
            raise Exception(f"DuckDB failed to load DataFrame: {e}")

    def query(self, query: str):
        if not self.conn:
            raise Exception("DuckDB connection not initialized")
        return self.conn.execute(query).fetchdf()

    def get_file_id(self):
        return self.file_id
