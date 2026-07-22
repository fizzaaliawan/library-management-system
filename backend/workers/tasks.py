import sys
import os
from celery.utils.log import get_task_logger

# Ensure app directory is in Python path for worker
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from workers.celery_app import celery_app
from app.database.session import SessionLocal
from app.services.loan import LoanService

logger = get_task_logger(__name__)

@celery_app.task(name="workers.tasks.check_overdue_loans_task")
def check_overdue_loans_task():
    """
    Background worker task that queries the database for active loans exceeding due dates,
    flags their status as 'Overdue', and dispatches real-time SSE alerts.
    """
    logger.info("Starting background check for overdue book loans...")
    
    db = SessionLocal()
    try:
        loan_service = LoanService()
        overdue_loans = loan_service.check_overdue_loans(db)
        
        logger.info(f"Background check finished. Processed {len(overdue_loans)} overdue loans.")
        return f"Processed {len(overdue_loans)} overdue records."
    except Exception as e:
        logger.error(f"Error executing overdue loans check: {e}")
        raise e
    finally:
        db.close()
