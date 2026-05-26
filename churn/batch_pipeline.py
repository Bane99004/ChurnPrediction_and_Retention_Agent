from decision_layer import ChurnDecisionEngine
from layer_3_Action import generate_retention_email
import pandas as pd
def batch_pipeline(customers_df: pd.DataFrame, max_emails: 50):
  engine = ChurnDecisionEngine()
  results=[]
  for _, row in customers_df.iterrows():
    customer = row.to_dict()
    decision = engine.decide_action(customer)
    ev = engine.calculate_expected_value(customer['churn_probability'], customer.get('estimated_ltv', 200), 20)
    result = {
      "customer_id": customer.get("customerID"),
      "churn_probability": customer["churn_probability"],
      "action": decision["action"],
      "priority": decision["priority"],
      "ev_intervention": ev["net_gain_from_intervening"],
    }
    if decision['priority'] in ['critical', 'high'] and max_emails > 0:
      result['email_draft'] = generate_retention_email(customer, decision, ev)
      max_emails -= 1
    else:
      result['email_draft'] = None
    results.append(result)
  
  output = pd.DataFrame(results)
  output = output.sort_values('ev_intervention', ascending=False)
  return output

print(batch_pipeline(test_df).head(10))