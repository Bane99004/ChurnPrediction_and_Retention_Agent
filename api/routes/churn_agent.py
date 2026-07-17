from fastapi import APIRouter, HTTPException, status
from churn.src.churn_agent import executor
from churn.src.churn_graph import graph_agent
from pydantic import BaseModel
router = APIRouter()

class AgentRequest(BaseModel):
  prompt: str

class AgentResponse(BaseModel):
  response: str
  success: bool
  error: str = None
  
@router.post("/", response_model= AgentResponse)
async def agent_response(request: AgentRequest):
  try:
    result = await graph_agent.ainvoke({'messages': [("human", request.prompt)]})
    return AgentResponse(response=result['messages'][-1].content , success=True)
  except Exception as e:
    return AgentResponse(response="", success=False, error=str(e))
  