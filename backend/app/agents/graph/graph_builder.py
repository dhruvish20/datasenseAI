from langgraph.graph import StateGraph
from langchain_core.language_models import BaseChatModel
from app.agents.state import AgentState
from app.agents.graph.nodes.tool_selector import build_tool_selector_node
from app.utils.sql_executor import SQLExecutorTool
from app.agents.tools.distribution_plotter import DistributionPlotTool
from app.agents.tools.trend_plotter import TrendPlotTool
from app.agents.tools.summary_stats import SummaryStatsTool
from app.agents.tools.duckdb_loader import CSVToDuckDBLoader
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.exceptions import OutputParserException
from app.agents.graph.parsers.trend_input_parser import TrendPlotInput
from app.agents.tools.distribution_plotter import DistributionPlotInput
from app.agents.tools.summary_stats import SummaryStatsInput
from app.agents.graph.parsers.trend_input_parser import build_trend_input_parser
from app.agents.graph.parsers.sql_input_parser import sql_input_parser
from app.agents.graph.parsers.distributor_input_parser import build_distributor_input_parser
from app.agents.graph.parsers.stats_input_parser import build_stats_input_parser


def build_graph(llm: BaseChatModel, duckdb_loader: CSVToDuckDBLoader):
    sql_tool = SQLExecutorTool(duckdb_loader=duckdb_loader)
    distribution_tool = DistributionPlotTool(duckdb_loader=duckdb_loader)
    trend_tool = TrendPlotTool(duckdb_loader=duckdb_loader)
    summary_stats_tool = SummaryStatsTool(duckdb_loader=duckdb_loader)

    def sql_node(state: AgentState):
        print("SQL Executor running...")
        loader = sql_tool.duckdb_loader

        try:
            columns_df = loader.conn.execute("PRAGMA table_info('data')").fetchdf()
            column_names = columns_df["name"].tolist()
        except Exception as e:
            state["answer"] = f"Failed to fetch columns: {str(e)}"
            return state
        
        parse_chain = sql_input_parser(llm, column_names)

        try:
            parsed = parse_chain.invoke({"question": state["question"]})

            if not parsed.get("query", "").lower().strip().startswith("select"):
                state["answer"] = f"Invalid SQL generated: {parsed.get('query')}"
                return state
            parsed["file_id"] = state["file_id"]
            print("Parsed input:", parsed)
            validated_input = sql_tool.args_schema(**parsed)
            result = sql_tool.invoke(validated_input.dict())

            state["answer"] = result
            return state
        except OutputParserException as e:
            state["answer"] = f"Failed to parse SQL input: {str(e)}"
            return state
        

    def dist_node(state: AgentState):
        print("Distribution Plot running...")
        loader = distribution_tool.duckdb_loader

        try:
            columns_df = loader.conn.execute("PRAGMA table_info('data')").fetchdf()
            column_names = columns_df["name"].tolist()
        except Exception as e:
            state["answer"] = f"Failed to fetch columns: {str(e)}"
            return state
        
        parser_chain = build_distributor_input_parser(llm, column_names)
        try:
            parsed = parser_chain.invoke({"question": state["question"]})
            print("Parsed input for distribution plot:", parsed)

            column = parsed.get("column")
            if column not in column_names:
                state["answer"] = f"Invalid column selected: {column}"
                return state
            parsed["file_id"] = state["file_id"]

            validated_input = DistributionPlotInput(**parsed)
            result = distribution_tool.invoke(validated_input.dict())

            state["answer"] = result
            return state
        
        except OutputParserException as e:
            state["answer"] = f"Failed to parse distribution input: {str(e)}"
            return state

    def trend_node(state: AgentState):
        loader = trend_tool.duckdb_loader

        try:
            columns_df = loader.conn.execute("PRAGMA table_info('data')").fetchdf()
            column_names = columns_df["name"].tolist()
        except Exception as e:
            state["answer"] = f"Failed to fetch columns: {str(e)}"
            return state

        parser_chain = build_trend_input_parser(llm, column_names)

        try:
            parsed = parser_chain.invoke({"question": state["question"]})
            parsed["file_id"] = state["file_id"]

            validated_input = TrendPlotInput(**parsed)
            result = trend_tool.invoke(validated_input.dict())

            state["answer"] = result
            return state

        except Exception as e:
            state["answer"] = f"Trend plot failed: {str(e)}"
            return state     

    def summary_node(state: AgentState):
        print("Summary Stats running...")
        loader = summary_stats_tool.duckdb_loader

        try:
            columns_df = loader.conn.execute("PRAGMA table_info('data')").fetchdf()
            column_names = columns_df["name"].tolist()
        except Exception as e:
            state["answer"] = f"Failed to fetch columns: {str(e)}"
            return state

        parser_chain = build_stats_input_parser(llm, column_names)

        try:
            parsed = parser_chain.invoke({"question": state["question"]})
            print("Parsed summary input:", parsed)

            # Graceful validation
            if not parsed.get("columns"):
                state["answer"] = "No columns selected for summary stats."
                return state

            parsed["file_id"] = state["file_id"]
            validated_input = SummaryStatsInput(**parsed)
            result = summary_stats_tool.invoke(validated_input.dict())

            state["answer"] = result
            return state

        except OutputParserException as e:
            state["answer"] = f"Failed to parse summary input: {str(e)}"
            return state
        
    tool_selector_node = build_tool_selector_node(llm)

    builder = StateGraph(AgentState)
    builder.add_node("tool_selector", tool_selector_node)
    builder.add_node("sql_executor", sql_node)
    builder.add_node("distribution_plot", dist_node)
    builder.add_node("trend_plot", trend_node)
    builder.add_node("summary_stats", summary_node)

    builder.set_entry_point("tool_selector")

    builder.add_conditional_edges(
        "tool_selector",
        lambda state: state["tool_to_use"],
        {
            "sql_executor": "sql_executor",
            "distribution_plot": "distribution_plot",
            "trend_plot": "trend_plot",
            "summary_stats": "summary_stats"
        }
    )

    builder.set_finish_point("sql_executor")
    builder.set_finish_point("distribution_plot")
    builder.set_finish_point("trend_plot")
    builder.set_finish_point("summary_stats")

    return builder.compile()