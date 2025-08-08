from typing import Optional, TypedDict

class AgentState(TypedDict, total=False):
    file_id: str                       
    question: str                     
    tool_to_use: Optional[str]     
    tool_input: Optional[dict]        
    intermediate_steps: list        
    answer: Optional[str]       

