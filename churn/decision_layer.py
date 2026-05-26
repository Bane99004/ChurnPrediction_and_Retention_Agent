import xgboost as xgb
import pandas as pd
from churn.utils.user_input_processing import encode_standardize_input, add_cols
MODEL_PATH = "models/churn_model_v1.json"
class ChurnDecisionEngine:
  
  def __init__(self, model_path=MODEL_PATH):
    self.model = xgb.XGBClassifier()
    self.model.load_model(model_path)
  
  def predict_churn_risk(self, customer_features: pd.DataFrame) -> dict:
    customer_features = add_cols(customer_features)
    customer_features = encode_standardize_input(customer_features)
    prob = self.model.predict_proba(customer_features)[0][1] #row[0] for class [1] prob
    return {"churn_probability": round(float(prob), 4)}
  
  def decide_action(self, customer: dict) -> dict:
    
    prob = customer['churn_probability']
    cltv = customer["estimated_ltv"]
    if not prob:
      return None
    elif prob >= 0.8 and cltv >= 500:
      return {
        "action": "immediate_retention_call",
        "priority": "critical",
        "reason":  f"High churn risk: ({prob:.0%})",
        "budget": f"$50 discount offer approved"
      }
    elif prob >= 0.65 and cltv >= 200:
      return {
        "action": "send_retention_call",
        "priority": "high",
        "reason": f"Elevated churn risk ({prob:.0%})",
        "budget": "$20 discount offer approved" 
      }
    elif prob >= 0.5:
      return {
        "action": "send_check_in email",
        "priority": "medium",
        "reason": f"Moderate churn risk ({prob:.0%})",
        "budget": "No discount, value communication only"
      }
    else:
      return {
        "action": "feedback_mail",
        "priority": "low",
        "reason": f"Low churn risk ({prob:.0%})",
        "budget": f"No discount, value communication only"
      }
  def calculate_expected_value(self, churn_prob:float, ltv: float, intervention_cost: float, success_rate: float = 0.30) -> dict:
    ev_no_action = -churn_prob * ltv
    ev_intervene = (success_rate * churn_prob * ltv) - intervention_cost
    should_intervene = ev_intervene > ev_no_action
    
    return{
      "ev_no_action": round(ev_no_action, 2),
      "ev_intervene": round(ev_intervene, 2),
      "net_gain_from_intervening": round(ev_intervene - ev_no_action, 2),
      "recomendation": "intervene" if should_intervene else "do_nothing",
      "break_even_success_rate": round(intervention_cost/ (churn_prob * ltv), 3) if (churn_prob * ltv) > 0 else None
    }
  
  
  
  
    
# customer = [{"Tenure Months": 24}]
# customer_df = pd.DataFrame(customer)``
# # print(customer)
# engine = ChurnDecisionEngine()

# risk_score = engine.predict_churn_risk(customer_df)
# test_customer = {"churn_probability": risk_score, "estimated_ltv": 650, "tenure_months":24}

# print(engine.decide_action(test_customer))
# print(engine.calculate_expected_value(churn_prob=0.75, ltv=400, intervention_cost=20))