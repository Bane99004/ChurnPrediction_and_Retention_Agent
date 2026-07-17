from fastapi import APIRouter, HTTPException, status, requests
from models import CustomerRequest
from churn.decision_layer import ChurnDecisionEngine
from churn.layer_3_Action import should_require_human_intervene, llm_reasoning_for_email
from database.crud import get_customer, get_all_customers
import logging
from pydantic import BaseModel, ConfigDict
from typing import Optional
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
router = APIRouter()
engine = ChurnDecisionEngine()

class CustomerResponse(BaseModel):
  id: str
  customer_id: str

  gender: Optional[str] = None
  senior_citizen: Optional[str] = None
  partner: Optional[str] = None
  dependents: Optional[str] = None

  tenure_months: Optional[int] = None

  phone_service: Optional[str] = None
  multiple_lines: Optional[str] = None
  internet_service: Optional[str] = None

  online_security: Optional[str] = None
  online_backup: Optional[str] = None
  device_protection: Optional[str] = None
  tech_support: Optional[str] = None

  streaming_tv: Optional[str] = None
  streaming_movies: Optional[str] = None

  contract: Optional[str] = None
  paperless_billing: Optional[str] = None
  payment_method: Optional[str] = None

  monthly_charges: Optional[float] = None
  total_charges: Optional[float] = None

  churn_label: Optional[str] = None
  churn_value: Optional[int] = None
  churn_score: Optional[int] = None
  estimated_ltv: Optional[float] = None
  churn_reason: Optional[str] = None

  zip_code: Optional[str] = None
  city: Optional[str] = None
  state: Optional[str] = None

  latitude: Optional[float] = None
  longitude: Optional[float] = None
  lat_long: Optional[str] = None

  count: Optional[int] = None
  country: Optional[str] = None

  created_at: Optional[str] = None

  model_config = ConfigDict(from_attributes=True)
    
@router.get("/get_customer/{id}", response_model=CustomerResponse)
async def _get_customer(id: str):
  try:
    customer = await get_customer(id)
    return customer
  except Exception as e:
    return HTTPException(status_code=404, detail="Customer with id {id} not found")

@router.get("/all_customers")
async def _get_all_customers():
  try:
    customer = await get_all_customers()
    return customer
  except Exception as e:
    return HTTPException(status_code=404, detail="No customer found.")
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
  