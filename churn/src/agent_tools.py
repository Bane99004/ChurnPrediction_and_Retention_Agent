from langchain.tools import tool
from churn.decision_layer import ChurnDecisionEngine
from churn.layer_3_Action import llm_reasoning_for_email, should_require_human_intervene
from monitoring.drift_report import monitor_model_drift
import pandas as pd
import sqlite3, json
from database.crud import get_customer, log_agent_interaction, get_interactions_history
engine = ChurnDecisionEngine()

@tool
async def predict_churn_risk(customer_id:str) ->str:
  """Look up a customer from the database and predict their churn probability.
    Use this tool first when asked about any specific customer.
  """
  customer = await get_customer(customer_id)
  if not customer:
    return f"Customer {customer_id} not found in database"
  customer= tuple(getattr(customer, column.name) for column in customer.__table__.columns[1:])
  # print(customer)
  customer = dict(zip([
"CustomerID",
"Gender",
"Senior Citizen",
"Partner",
"Dependents",
"Tenure Months",
"Phone Service",
"Multiple Lines",
"Internet Service",
"Online Security",
"Online Backup",
"Device Protection",
"Tech Support",
"Streaming TV",
"Streaming Movies",
"Contract",
"Paperless Billing",
"Payment Method",
"Monthly Charges",
"Total Charges",
"Churn Label",
"Churn Value",
"Churn Score",
"estimated_ltv",
"Churn Reason",
"Zip Code",
"City",
"State",
"Latitude",
"Longitude",
"Lat Long",
"Count"
], customer))
  customer_df = pd.DataFrame([customer])
  prob = engine.predict_churn_risk(customer_df)['churn_probability']
  customer['churn_probability'] = prob
  return json.dumps(customer)

@tool
async def get_customer_history(customer_id:str):
  """Retrieve the last 5 agent interactions for a customer. Call this if you need to know whether the customer was recently contacted, or if a a previous email was sent without response."""
  history = await get_interactions_history(customer_id)
  if not history:
    return json.dumps({"history":[], "message": "History of interactions for this customer not found."})
  return json.dumps({
    "history": history,
    "last_interaction": history[0]['created_at'],
    "last_action": history[0]['action']
  })
@tool
async def evaluate_retention_action(customer_json:str) -> str:
  """Given a customer JSON with churn_probability, evaluate the best retention action and its expected value. Call this after predict_churn_risk."""
  customer = json.loads(customer_json)
  decision = engine.decide_action(customer)
  ev = engine.calculate_expected_value(customer['churn_probability'], customer.get('estimated_ltv', 200.0), 20)
  return json.dumps({
    "decision": decision,
    "expected_value": ev
  })

@tool
async def draft_retention_email(complete_customer_details: str, decision_json: str, expected_value: str) -> str:
  """Draft a personalised retention email with CoT reasoning. 
  Only call this if evaluate_retention_action recommends send_retention_email or immediate_retention_call or send_check_in_email"""
  print(complete_customer_details)
  customer = json.loads(complete_customer_details)
  decision = json.loads(decision_json)
  ev = json.loads(expected_value)
  print(ev)
  print(decision)
  result = llm_reasoning_for_email(customer, decision, ev)
  review = should_require_human_intervene(result)
  result['review_gate'] = review
  return json.dumps(result)

@tool
async def check_model_drift() -> str:
  """Call this if asked about model's health"""
  results = monitor_model_drift()
  return json.dumps(results)

@tool
async def log_completed_action(complete_customer_details :str, action: str, email_sent:bool, review_required: bool, ev: float):
  """Log a completed agent action to the database.
  ALWAYS call this after taking any action - this is the audit trail."""
  customer= json.loads(complete_customer_details)
  customer_id=customer['CustomerID']
  await log_agent_interaction(customer_id=customer_id,
      churn_probability=customer['churn_probability'],
      action=action,
      email_sent=email_sent,
      review_required=review_required,
      ev=ev)
  
  return json.dumps({"logged": True, "customer_id": customer_id, "action": action})
