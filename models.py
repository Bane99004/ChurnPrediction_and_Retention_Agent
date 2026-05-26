from pydantic import BaseModel, Field, validator

def CustomerRequest(BaseModel):
  customerID : str = Field(..., min_length=1, max_length=50)
  churnProbabilty : float = Field(..., ge=0.0, le=1.0)
  estimated_ltv : float = Field(default=200.0, ge = 0.0)
  tenure_months : int = Field(default=12, ge=0)
  monthly_charges: float = Field(default=50.0, ge=0.0)
  contract: str = Field(default="Month-to-Month")
  recent_tickets: int = Field(default=0, ge=0)
  name: Optional[str] = "Valued Customer"
  
  @validator('contract')
  def valid_contract(cls, v):
    allowed = ["Month-to-month", "One year", "Two year"]
    if v not in allowed:
      raise ValueError(f"contract must be one of {allowed}")
    return v 
  