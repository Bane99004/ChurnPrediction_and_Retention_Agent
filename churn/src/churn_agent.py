from langchain_openai import ChatOpenAI
from langchain_classic.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate
from churn.src.agent_tools import (predict_churn_risk, evaluate_retention_action, draft_retention_email, check_model_drift)
import asyncio
tools = [predict_churn_risk, evaluate_retention_action, draft_retention_email, check_model_drift]
llm = ChatOpenAI(model = "gpt-4o-mini", temperature=0)

system_prompt = """You are a customer retention AI agent for a SaaS comapny. 
TOOLS AVAILABLE: predict_churn_risk, get_customer_history, evaluate_retention_action, draft_retention, log_completed_action, check_model_drift

MADNATORY EXECUTION ORDER:
1. predict_churn_risk - always first, no exceptions
2. get_customer_history - check if customer was contacted in last 7 days -> If contacted within 7 days: STOP. Do not act. Explain why.
3. evaluate_retention_action - only proceed if not recently contacted
4. draft_retention_email - only if action is send_retention_email or call.
5. log_completed_Action - ALWAYS last, after any actoin is taken

VERIFIABLE AI RULES:
- If review_gate.requires_review is true: flag for human, do not auto-approve
- If churn_probability < 0.48: explain no_action decision, do not auto_approve
- If model drift is detected: pause all actions, alert human operator
- Never skip the EV check - no action is taken without positive expected value

Be transparent about your reasoning at very step.
"""
prompt = ChatPromptTemplate.from_messages([
  ("system", system_prompt),
  ("human", "{input}"),
  ("placeholder", "{agent_scratchpad}")
])
agent = create_tool_calling_agent(llm, tools, prompt)
executor = AgentExecutor(agent=agent, tools=tools, verbose=True, max_iterations=6, handle_parsing_errors=True)
async def main():
  result = await executor.ainvoke({
    "input": "Customer C001 hasn't logged in for 3 weeks. Should we reach out?"
  })
  print(result['output'])

asyncio.run(main())