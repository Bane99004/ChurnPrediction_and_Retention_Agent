def get_email_system_prompt():
  return f"""You are a customer retention specialist writing a personalised email.
  INSTRUCTIONS:
  Write a retention email that:
  1. Feels personal, not automated
  2. Acknowledges the customer's history without being creepy
  3. If a discount is approved, mention it naturally — not as a bribe
  4. Is under 100 words
  5. Has a clear single call to action

  Do not mention churn probability or internal metrics. Write only the email.
"""


def get_reasoning_system_prompt():
  return f"""
  Role: Churn analyst.

  Task: Produce ONLY analytical reasoning.

  Return EXACTLY four lines, in this format based on customer characteristics:

  Risk: ...
  Tone: ...
  Value: ...
  Discount strategy: ...

  Constraints:
  - Analytical statements only
  - No greetings, no sign-offs
  - No conversational or persuasive language
  - No addressing the customer
  - No extra text before or after the four lines
  """

def get_reasoning_user_prompt(customer, decision):
  return f"""
  Analyze the customer and producing reasoning.

Customer details:
- Churn probability: {customer['churn_probability']:.0%}
- Tenure: {customer.get('tenure_months',0)} months
- Monthly charges: ${customer.get('monthly_charges',0):.2f}
- Recent tickets: {customer.get('recent_tickets',0)}
- Approved action: {decision['action']}
- Budget: {decision.get('budget','none')}

Cover:
1. Why this customer is at risk
2. Best tone to use
3. Key value proposition
4. Discount strategy (upfront or later)

Reasoning:
"""

def get_email_user_prompt(customer, decision, ev, reasoning):
  return f""" Below is a structured summary of the customer's profile, risk assessment, and recommended actions:
CUSTOMER PROFILE:
- Name: {customer.get('name', 'Valued Customer')}
- Tenure: {customer.get('tenure_months', 0)} months
- Monthly charges: ${customer.get('monthly_charges', 0):.2f}
- Contract type: {customer.get('contract', 'Month-to-month')}
- Support tickets last 3 months: {customer.get('recent_tickets', 0)}

RISK ASSESSMENT:
- Churn probability: {customer.get('churn_probability', 0):.0%}
- Priority level: {decision.get('priority', 'medium')}

APPROVED ACTION:
- {decision.get('action')}
- Budget: {decision.get('budget', 'none')}
- Reason for concern: {decision.get('reason')}

BUSINESS CONTEXT:
- Expected value of retaining this customer: ${ev.get('net_gain_from_intervening', 0):.2f}

EMAIL CONTEXT FOR CUSTOMER AFTER EVALUATION AND REASONING IS:
{reasoning}

"""
def get_user_prompt_no_cot(customer, decision, ev):
  return f""" Below is a structured summary of the customer's profile, risk assessment, and recommended actions:
CUSTOMER PROFILE:
- Name: {customer.get('name', 'Valued Customer')}
- Tenure: {customer.get('tenure_months', 0)} months
- Monthly charges: ${customer.get('monthly_charges', 0):.2f}
- Contract type: {customer.get('contract', 'Month-to-month')}
- Support tickets last 3 months: {customer.get('recent_tickets', 0)}

RISK ASSESSMENT:
- Churn probability: {customer.get('churn_probability', 0):.0%}
- Priority level: {decision.get('priority', 'medium')}

APPROVED ACTION:
- {decision.get('action')}
- Budget: {decision.get('budget', 'none')}
- Reason for concern: {decision.get('reason')}

BUSINESS CONTEXT:
- Expected value of retaining this customer: ${ev.get('net_gain_from_intervening', 0):.2f}

"""
