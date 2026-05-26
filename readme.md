# ------- Churn Prediction & Customer Retention System ------- #

## Architecture

Customer Data ⟶ [Layer 1: XGBoost] ⟶ P(churn)
                          ↓
                [Layer 2: Decision Engine + EV Math] ⟶ action + budget
                          ↓
                [Layer 3: CoT + LLM] ⟶ reasoning ⟶ email
                          ↓
                [Verification Gate] ⟶ auto-send OR human
                          ↓
                [Monitoring: Evidently drift check] ⟶ retrain alert


### Quick Start - Literally 3 commands:

1. git clone <repo>
2. cd <main_directory>
3. docker-compose up


## API Endpoints 

1. /api/customer_retention/predict_action
  - Predicts churn, Decision making for respectable action and      calculating ev, writing email for the churned customer. And then finally decide whther the email should be sent automatically or with human intervention is needed.

2. /api/model_drift_monitoring
  - Monitors the model based on trained dataset and current new data of customers and alerts accordingly.

3. /api/health
  - To check the status whether api is running.


## What makes this different:
- It not only predicts churn probability and take actins for retention but also verifies what kind of actions should be taken for retention and will it be profitable to invest on that particular customer.

- Based on customer data, decisions and expected value the model reasons and set tone, subject and retention strategy as per decisions. And then uses this reasoning to write a retention email for customer. A threshold is set whether the email should be automatically send or should be intervene by humans before sending.

- It also keep track of drift between dataset on which the model was trained and current customers data. So if drift is detected it alerts humans to retrain the model on new/current data.