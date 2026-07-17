from database.database import SessionLocal
from database.database_models import AgentInteractions, Customer
from sqlalchemy import select
async def get_customer(customer_id:str):
  async with SessionLocal() as session:
    result=  await session.execute(select(Customer).where(Customer.customer_id == customer_id))
    customer = result.scalar_one_or_none()
    
  return customer

async def get_all_customers():
  async with SessionLocal() as session:
    result = await session.execute(select(Customer))
    customers=result.scalars().all()
    return customers

async def log_agent_interaction(customer_id: str, churn_prob:float, action:str, email_sent:bool, review_required:bool, ev:float):
  async with SessionLocal() as session:
    interaction = AgentInteractions(
      customer_id=customer_id,
      churn_probability=churn_prob,
      action=action,
      email_sent=email_sent,
      review_required=review_required,
      ev=ev
    )
    await session.add(interaction)
    await session.commit()

async def get_interactions_history(customer_id):
  async with SessionLocal() as session:
    results = await session.execute(select(AgentInteractions).where(AgentInteractions.customer_id == customer_id))
    history = results.scalars().all()
    return history
  