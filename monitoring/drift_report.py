import pandas as pd
from evidently import Report
from evidently.presets import DataDriftPreset, ClassificationPreset
from evidently.metrics import DatasetMissingValueCount
from datetime import datetime
import json
def monitor_model_drift():
  reference = pd.read_excel('datasets/Telco_customer_churn.xlsx')
  current = pd.read_excel('datasets/Telco_customer_churn.xlsx')
  reference = reference.sample(frac=1).reset_index(drop=True)
  current = current.sample(frac=1).reset_index(drop=True)
  reference = reference.drop('Churn Reason', axis=1)
  current = current.drop('Churn Reason', axis=1)
  reference['Churn_binary'] = (reference['Churn Label'] == 'Yes').astype(int)
  current['Churn_binary'] = (current['Churn Label'] == 'Yes').astype(int)

  report_d = Report(metrics=[
    DataDriftPreset(),
    DatasetMissingValueCount(),
  ]) 


  report = report_d.run(reference_data=reference, current_data=current)

  result = json.loads(report.json())
  drift_detected = result['metrics'][0]['value']['count']
  drift_share = result['metrics'][0]['value']['share']
  return {
    "drift_detected": drift_detected,
    "drifted_feature_share": drift_share,
    "recommendation": "retrain_model" if drift_detected else "model_stable",
    "action_required": drift_detected,
    "last_checked": datetime.utcnow().strftime("%d-%m-%Y %H:%M")
  }
