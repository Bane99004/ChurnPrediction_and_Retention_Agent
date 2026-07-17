import pandas as pd
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
import joblib

def encode_standardize_input(df):
  
  ct = joblib.load('churn/utils/transformer.pkl')
  df = ct.transform(df)
  return df

def calculate_cltv(prob: float, horizon: 24, monthly_revenue: float, discounted_rate = 0.1):
  cltv = 0
  for t in range(1, horizon + 1):
    prob_t = (1 - prob)**t
    discounted_revenue = monthly_revenue / (1+ discounted_rate)**t
    cltv += prob_t * discounted_revenue
  return cltv
  
def add_cols(df):
  df["Total Charges"] = pd.to_numeric(df["Total Charges"], errors='coerce')
  df["Tenure Group"] = pd.cut(
    df["Tenure Months"],
    bins=[0,12,24,36,48,60,72],
    labels=["0-1yr", "1-2yr", "2-3yr", "3-4yr", "4-5yr", "5-6yr"]
  )

  services = [
      "Phone Service", "Internet Service", "Online Security",
      "Tech Support", "Streaming TV", "Streaming Movies", "Online Backup", "Device Protection", 
  ]
  
  df["Total Services"] = (df[services] == "Yes").sum(axis=1).astype(str)
  return df

