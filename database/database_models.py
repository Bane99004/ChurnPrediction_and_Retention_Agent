from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Text, Boolean, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from database.database import Base

def generate_uuid():
  return str(uuid.uuid4())

class Customer(Base):
  __tablename__ = "customer"

  id = Column(String, primary_key=True, default=generate_uuid)

  customer_id = Column(String, primary_key=True, nullable=False)

  gender = Column(String)
  senior_citizen = Column(String)
  partner = Column(String)
  dependents = Column(String)
  
  tenure_months = Column(Integer)

  phone_service = Column(String)
  multiple_lines = Column(String)
  internet_service = Column(String)

  online_security = Column(String)
  online_backup = Column(String)
  device_protection = Column(String)
  tech_support = Column(String)

  streaming_tv = Column(String)
  streaming_movies = Column(String)

  contract = Column(String)
  paperless_billing = Column(String)
  payment_method = Column(String)

  monthly_charges = Column(Float)
  total_charges = Column(Float)

  churn_label = Column(String)
  churn_value = Column(Integer)
  churn_score = Column(Integer)
  estimated_ltv = Column(Float)
  churn_reason = Column(Text)

  zip_code = Column(String)
  city = Column(String)
  state = Column(String)

  latitude = Column(Float)
  longitude = Column(Float)
  lat_long = Column(String)

  count = Column(Integer)
  country = Column(String)
  created_at = Column(String, default=lambda: datetime.utcnow().isoformat())
  
class AgentInteractions(Base):
  __tablename__ = "agent_interactions"
  id = Column(String, primary_key=True, default=generate_uuid())
  customer_id = Column(String, ForeignKey("customer.customer_id"), nullable=False)
  churn_probability = Column(Float)
  action = Column(String)
  email_sent = Column(Boolean)
  review_required = Column(Boolean)
  ev = Column(Float)
  created_at = Column(DateTime, default=datetime.utcnow().isoformat())
  
  