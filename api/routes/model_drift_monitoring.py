from fastapi import HttpException, Depends, status, APIRouter
import logging
from monitoring.drift_report import monitor_model_drift

logging.Basicconfig(level=logging.INFO)
logger = logging.getLogger(__name__)
route  = APIRouter()

@router.get()
def model_drift_monitoring():
  try:
    result = monitor_model_drift()
    return result
  except Exception as e:
    logger.error(f"Model monitoring failed: {e}")
    raise HttpException(status=500, detail=e)
  
