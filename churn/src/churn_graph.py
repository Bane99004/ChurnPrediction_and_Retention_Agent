from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_openai import ChatOpenAI
from typing import TypedDict, Annotated
import operator, json
from churn.src.agent_tools import (predict_churn_risk, evaluate_retention_action, draft_retention_email, check_model_drift)
from dotenv import load_dotenv
import os

load_dotenv()

tools = [predict_churn_risk, evaluate_retention_action, draft_retention_email, check_model_drift]


class AgentState(TypedDict):
  messages: Annotated[list, operator.add] 
  review_required: bool

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
llm_with_tools = llm.bind_tools(tools)

def should_continue(state: AgentState):
  """Router: decide next node based on state"""
  last_msg = state['messages'][-1]
  if hasattr(last_msg, 'tool_calls') and last_msg.tool_calls:
    return "tools"
  
  if state.get('review_required'):
    return "human_review"
  
  return END

def call_llm_node(state: AgentState) -> AgentState:
  response = llm_with_tools.invoke(state['messages'])
  return {
    "messages": [response],
  }

def human_review_node(state: AgentState) -> AgentState:
  """In production: this sends a Slack/email alert to a human.
  In demo: just logs and returns the review flag."""
  
  print(f"\n Human review required for customer {state['customer_id']}")
  print("Reason: high-stakes action flagged by verification gate")
  return {"final_output": f"Human review required. Action paused for customer {state['customer_id']}."}

workflow = StateGraph(AgentState)
workflow.add_node("agent", call_llm_node)
workflow.add_node("tools", ToolNode(tools))
workflow.add_node("human_review", human_review_node)

workflow.set_entry_point("agent")

workflow.add_conditional_edges("agent", should_continue, {"tools": "tools", "human_review":"human_review", END:END})

workflow.add_edge("tools", "agent")
workflow.add_edge("human_review", END)


graph_agent = workflow.compile()
# async def main():
#   result = await graph_agent.ainvoke({
#     "messages": [
#       (
#         "human",
#         "Should we reach out to customer C005? "
#         "Use the available tools to fetch the customer data, "
#         "predict churn, evaluate the action, and draft an email if needed."
#       )
#     ]
#   })
  
#   print(result['messages'][-1].content)
#   print("========================================================>")
#   print(result)
# if __name__ == "__main__":
#   import asyncio
#   asyncio.run(main())