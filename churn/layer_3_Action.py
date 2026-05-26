from openai import OpenAI
from dotenv import load_dotenv
from churn.layer3_context_template import get_email_system_prompt, get_email_user_prompt, get_reasoning_system_prompt,get_reasoning_user_prompt,get_user_prompt_no_cot
import os, json
from churn.utils.user_input_processing import calculate_cltv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
openai = OpenAI(api_key=api_key)
MODEL="gpt-5-nano"
def llm_reasoning_for_email(customer, decision, ev):
  
  reasoning_system_prompt = get_reasoning_system_prompt()
  reasoning_user_prompt = get_reasoning_user_prompt(customer, decision)
   
  reasoning = call_llm(reasoning_system_prompt, reasoning_user_prompt, max_tokens = 200)
  
  email_system_prompt = get_email_system_prompt()
  email_user_prompt = get_email_user_prompt(customer, decision, ev, reasoning)
  email = call_llm(email_system_prompt, email_user_prompt, max_tokens = 200)
  return {
    "reasoning" : reasoning,
    "churn_probability": customer['churn_probability'],
    "action": decision['action'],
    "email": email,
    "ev": ev['net_gain_from_intervening']
    
  }
def call_llm(system_prompt, user_prompt, max_tokens):
  res = openai.chat.completions.create(
    model=MODEL,
    messages=[
      {"role": "system", "content": system_prompt},
      {"role": "user", "content": user_prompt}
    ]
  )
  return res.choices[0].message.content

def without_cot(customer, decision, ev):
  system_prompt= get_email_system_prompt()
  user_prompt= get_user_prompt_no_cot(customer, decision, ev)
  results = call_llm(system_prompt,user_prompt, max_tokens=100)
  return {
    'no_cot_email': results
  }

def should_require_human_intervene(result: dict) -> dict:
  flags = []
  if result['churn_probability'] >= 0.90:
    flags.append("extreme churn risk - verify reasoning")
  if result['ev'] > 300:
    flags.append("high EV customer - confirm discount level")
  if "discount" in result['email'].lower() and result['ev'] < 50:
    flags.append("discount offerend on low-EV customer - check buisness logic")
  if len(result['reasoning'].split()) < 30:
    flags.append("reasoning too short - LLM may have shortcut")
  return {
    "requires_review": len(flags) > 0,
    "flags": flags,
    "auto_send": len(flags) == 0
  }
  

# from decision_layer import ChurnDecisionEngine

# engine = ChurnDecisionEngine()
# cltv = calculate_cltv(0.84,60,104.80,0.1)
# print(f"CLTV: {cltv}")
# customer = {
#   "name": "John Doe",
#   "tenure_months": 14,
#   "monthly_charges": 105.50,
#   "contract": "Month=to-Month",
#   "recent_tickets": 3,
#   "estimated_ltv": 500,
#   "churn_probability": 0.8
# }


# decision = engine.decide_action(customer)
# ev = engine.calculate_expected_value(customer['churn_probability'], customer["estimated_ltv"], 20)

# result = llm_reasoning_for_email(customer, decision, ev)
# print(result)
# print(should_require_human_intervene(result))
# email = generate_retention_email(customer, decision, ev)

# print("=== LAYER 1 OUTPUT ===")
# print(f"Churn probsbility: {customer["churn_probability"]:.0%}")
# print("\n==== LAYER 2 OUTPUT ===")
# print(decision)
# print(f"EV of intervention: ${ev["net_gain_from_intervening"]:.2f}")
# print("\n=== LAYER 3 OUTPUT ===")
# print(email)

# results = []
# customers = [
#     {
#         "name": "Customer A",
#         "churn_probability": 0.85,
#         "tenure_months": 3,
#         "monthly_charges": 95,
#         "recent_tickets": 3,
#         "estimated_ltv": 285,
#         "contract": "Month-to-month"
#     },
#     {
#         "name": "Customer B",
#         "churn_probability": 0.72,
#         "tenure_months": 24,
#         "monthly_charges": 45,
#         "recent_tickets": 0,
#         "estimated_ltv": 1080,
#         "contract": "Two year"
#     },
#     {
#         "name": "Customer C",
#         "churn_probability": 0.40,
#         "tenure_months": 12,
#         "monthly_charges": 60,
#         "recent_tickets": 1,
#         "estimated_ltv": 720,
#         "contract": "One year"
#     },
#     {
#         "name": "Customer D",
#         "churn_probability": 0.90,
#         "tenure_months": 2,
#         "monthly_charges": 110,
#         "recent_tickets": 5,
#         "estimated_ltv": 220,
#         "contract": "Month-to-month"
#     },
#     {
#         "name": "Customer E",
#         "churn_probability": 0.55,
#         "tenure_months": 36,
#         "monthly_charges": 70,
#         "recent_tickets": 0,
#         "estimated_ltv": 2520,
#         "contract": "Two year"
#     }
# ]

# for customer in customers:
#   decision = engine.decide_action(customer)
#   ev = engine.calculate_expected_value(customer['churn_probability'], customer['estimated_ltv'], 20)
  
#   results_cot = llm_reasoning_for_email(customer,decision, ev)
#   results_no_cot = without_cot(customer, decision, ev)
#   results.append({
#     'customer_name': customer['name'],
#     'churn_probability': customer['churn_probability'],
#     'no_cot_email': results_no_cot['no_cot_email'],
#     'cot_resoning': results_cot['reasoning'],
#     'cot_email': results_cot['email']
#   })
  
# with open('cot_vs_noCot.json', 'w', encoding='utf-8') as f:
#   json.dump(results,f, indent=4)
  