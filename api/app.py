from fastapi import FastAPI
from api.routes import customer_retention, model_drift_monitoring, churn_agent

app = FastAPI(title="Churn Prediction and retention workflow")

app.include_router(customer_retention.router, prefix = "/api/customer_retention", tags=["customer_retention"])
app.include_router(model_drift_monitoring.router, prefix="/api/model_drift_monitoring", tags=["model_drift_monitoring"])
app.include_router(churn_agent.router, prefix="/api/churn_agent", tags=["churn_agent"])
@app.get('/health')
def read_root():
  return {"status": "Running"}

if __name__ == "__main__":
  import uvicorn
  uvicorn.run(app, host="0.0.0.0", port = 8000)