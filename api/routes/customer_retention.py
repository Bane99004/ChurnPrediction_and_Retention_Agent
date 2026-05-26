from fastapi import APIRouter, HTTPException, status, requests
from models import CustomerRequest
from churn.decision_layer import ChurnDecisionEngine
from churn.layer_3_Action import should_require_human_intervene, llm_reasoning_for_email
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getlogger(__name__)
router = APIRouter()
engine = ChurnDecisionEngine()

@router.get("/predict_action")
def prediction_action(customer: CustomerRequest):
  try:
    logger.info(f"Processing customer {customer.customerID}")
    data = customer.dict()
    decision = engine.decide_action(data)
    ev = engine.calculate_expected_value(customer.churnProbability, customer.estimated_ltv, 20)
    llm_decision = llm_reasoning_for_email(customer, decision, ev)
    review = should_require_human_intervene(llm_decision)
    return {
      "customer_id": customer.customerID,
      "decision": decision,
      "expected_value": ev,
      "should_human_intervene": review,
      "reasoning": llm_decision['reasoning'],
      "email": llm_decision['email']
      }
  except Exception as e:
    logger.error(f"Pipeline failed for customer: {customer.customerID}: {e}")
    raise HTTPException(status_code=500, detail=str(e))
  