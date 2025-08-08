from app.agents.graph.data_agent import DataAgent

def run_agent_on_csv(csv_path: str, question: str, file_id: str):
    agent = DataAgent(csv_path)
    return agent.run(question, file_id=file_id)
