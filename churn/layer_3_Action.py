from openai import OpenAI
from dotenv import load_dotenv
from churn.layer3_context_template import get_email_system_prompt, get_email_user_prompt, get_reasoning_system_prompt,get_reasoning_user_prompt,get_user_prompt_no_cot
import os, json
from churn.utils.user_input_processing import calculate_cltv
from churn.decision_layer import ChurnDecisionEngine
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

def generate_with_majority_vote(customer,decision,ev,n_samples=3):
  """Test time compute scaling run N reasoning chains, pick the most consistent conclusion.
  Based on Snell et al. 2024 - more inference compute = better output"""
  results = []
  for i in range(n_samples):
    result = llm_reasoning_for_email(customer, decision, ev)
    results.append(result)

  def score_reasoning(r, customer, decision, ev):
    reasoning = r["reasoning"].lower()
    score = 0

    # 1. Mentions the correct churn level
    if customer["churn_probability"] >= 0.8:
        if "high" in reasoning or "very high" in reasoning:
            score += 10
        elif "low" in reasoning:
            score -= 30
    # 2. Uses customer evidence
    if str(customer["tenure_months"]) in reasoning:
        score += 5
    if str(customer["monthly_charges"]) in reasoning:
        score += 5
    if str(customer["recent_tickets"]) in reasoning:
        score += 5
    # 3. Action matches decision engine
    if decision["action"].replace("_", " ") in reasoning:
        score += 15
    # 4. Discount consistency
    if "discount" in reasoning:
        if decision["budget"] != "No discount":
            score += 10
        else:
            score -= 20
    # 5. Expected value mentioned
    if "value" in reasoning or "roi" in reasoning:
        score += 5
    # 6. Penalize contradictions
    if "low risk" in reasoning and customer["churn_probability"] > 0.8:
        score -= 50
    if "do not intervene" in reasoning and ev["recomendation"] == "intervene":
        score -= 50
    return score, reasoning
  
  best = max( 
      results,
      key=lambda r: score_reasoning(r, customer, decision, ev)[0]
  )  
  best['n_samples'] = n_samples
  best['resoning_scores'] = [score_reasoning(r, customer, decision, ev) for r in results]
  best['consistency'] = len(set(r['reasoning'].split()[0] for r in results)) == 1
  return best


# def without_cot(customer, decision, ev):
#   system_prompt= get_email_system_prompt()
#   user_prompt= get_user_prompt_no_cot(customer, decision, ev)
#   results = call_llm(system_prompt,user_prompt, max_tokens=100)
#   return {
#     'no_cot_email': results
#   }

# from decision_layer import ChurnDecisionEngine

engine = ChurnDecisionEngine()
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

# result = generate_with_majority_vote(customer, decision, ev, n_samples=3)
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

results = []
customers = [
    {
        "name": "Customer A",
        "churn_probability": 0.85,
        "tenure_months": 3,
        "monthly_charges": 95,
        "recent_tickets": 3,
        "estimated_ltv": 285,
        "contract": "Month-to-month"
    },
    # {
    #     "name": "Customer B",
    #     "churn_probability": 0.72,
    #     "tenure_months": 24,
    #     "monthly_charges": 45,
    #     "recent_tickets": 0,
    #     "estimated_ltv": 1080,
    #     "contract": "Two year"
    # },
    # {
    #     "name": "Customer C",
    #     "churn_probability": 0.40,
    #     "tenure_months": 12,
    #     "monthly_charges": 60,
    #     "recent_tickets": 1,
    #     "estimated_ltv": 720,
    #     "contract": "One year"
    # },
    # {
    #     "name": "Customer D",
    #     "churn_probability": 0.90,
    #     "tenure_months": 2,
    #     "monthly_charges": 110,
    #     "recent_tickets": 5,
    #     "estimated_ltv": 220,
    #     "contract": "Month-to-month"
    # },
    # {
    #     "name": "Customer E",
    #     "churn_probability": 0.55,
    #     "tenure_months": 36,
    #     "monthly_charges": 70,
    #     "recent_tickets": 0,
    #     "estimated_ltv": 2520,
    #     "contract": "Two year"
    # }
]

for customer in customers:
  decision = engine.decide_action(customer)
  ev = engine.calculate_expected_value(customer['churn_probability'], customer['estimated_ltv'], 20)
  
  results_cot = generate_with_majority_vote(customer,decision, ev, n_samples=3)
  # results_no_cot = without_cot(customer, decision, ev)
  results.append({
    "customer": customer,
    "decision": decision,
    "ev": ev,
    "results_cot": results_cot,
    # "results_no_cot": results_no_cot
  })
  
with open('cot_vs_noCot.json', 'w', encoding='utf-8') as f:
  json.dump(results,f, indent=4)
  