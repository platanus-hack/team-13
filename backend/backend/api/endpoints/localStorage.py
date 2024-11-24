from fastapi import APIRouter, Depends, Request, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from ...core.database import get_db
from ..dependencies import get_client_ip
from ...models import LocalStorage, Customer, IPList
from ...services.llm_localStorage import LLMStorageService
from pydantic import BaseModel
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
llm_storage_service = LLMStorageService()

class LocalStorageEventCreate(BaseModel):
    key: str
    old_value: str | None = None
    new_value: str | None = None
    timestamp: datetime

async def process_storage_with_llm(
    db: Session, event_id: int, content: dict, ip: str, domain: str
):
    try:
        result = await llm_storage_service.analyze_storage(event_id, content, ip, domain)
        
        with db.begin():
            event = db.query(LocalStorage).filter(LocalStorage.id == event_id).first()
            if event:
                event.is_malicious = result["is_malicious"]
                event.confidence_score = result["confidence_score"]
                
                if result["is_malicious"]:
                    logger.info(f"Malicious localStorage event detected: {event_id} for IP: {ip}")
                    ip_entry = db.query(IPList).filter(
                        IPList.ip_address == ip
                    ).first()
                    if ip_entry:
                        logger.info(f"Blocking IP: {ip}")
                        ip_entry.is_blocked = True

    except Exception as e:
        logger.error(f"Error processing localStorage: {str(e)}", exc_info=True)

@router.post("/localStorage")
async def create_localStorage_event(
    event: LocalStorageEventCreate,
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    try:
        ip, domain = get_client_ip(request, db=db)
        logger.info(f"Received localStorage event from IP: {ip}, Domain: {domain}")
        logger.info(f"Event data - Key: {event.key}, Old: {event.old_value}, New: {event.new_value}, Timestamp: {event.timestamp}")
        
        with db.begin():
            # Check for blocked IP
            ip_blocked = db.query(IPList).filter(
                IPList.ip_address == ip,
                IPList.is_blocked == True
            ).first()
            
            if ip_blocked:
                logger.warning(f"Blocked IP {ip} attempted to create localStorage event")
                raise HTTPException(status_code=403, detail="IP is blocked")

            # Create content JSON
            content = {
                event.key: {
                    "old": event.old_value,
                    "new": event.new_value,
                    "timestamp": event.timestamp.isoformat()
                }
            }
            logger.debug(f"Created content payload: {content}")

            storage_event = LocalStorage(
                domain=domain,
                ip_address=ip,
                content=content
            )
            db.add(storage_event)
            db.flush()
            logger.info(f"Created localStorage event with ID: {storage_event.id}")

            background_tasks.add_task(
                process_storage_with_llm,
                db,
                storage_event.id,
                content,
                ip,
                domain,
            )
            logger.debug(f"Scheduled LLM analysis for event ID: {storage_event.id}")

            return {"status": "success", "id": storage_event.id}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in create_localStorage_event: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")