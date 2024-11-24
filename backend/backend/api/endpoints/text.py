from fastapi import APIRouter, Depends, Request, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from ...core.database import get_db
from ..schemas import TextEventCreate
from ..dependencies import get_client_ip
from ...models import TextMessage, Customer, IPList
from ...services.llm import LLMService
import logging

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

router = APIRouter()
llm_service = LLMService()


async def process_text_with_llm(
    db: Session, event_id: int, text: str, ip: str, domain: str
):
    """Background task to process text with OpenAI"""
    try:
        result = await llm_service.analyze_text(event_id, text, ip, domain)
        
        with db.begin():
            event = db.query(TextMessage).filter(TextMessage.id == event_id).first()
            if not event:
                logger.error(f"Event {event_id} not found")
                return
            
            event.is_malicious = result["is_malicious"]
            event.type = result["type"]
            event.confidence_score = result["confidence_score"]
            
            if result["is_malicious"]:
                logger.info(f"Malicious text detected: {text} for IP: {ip} and domain: {domain}")
                ip_entry = (
                    db.query(IPList)
                    .filter(IPList.ip_address == ip)
                    .first()
                )
                
                logger.info(f"blocking event: {event}")
                event.caused_block = True
                logger.info(f"event blocked: {event}")
                
                if ip_entry:
                    ip_entry.is_blocked = True

    except Exception as e:
        logger.error(f"Error processing text: {str(e)}", exc_info=True)


@router.post("/text")
async def create_text_event(
    event: TextEventCreate,
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    try:
        logger.info("Starting text event creation")

        ip, domain = get_client_ip(request, db=db)
        
        with db.begin():
            # Check if domain exists
            customer = db.query(Customer).filter(Customer.domain == domain).first()
            if not customer:
                customer = Customer(domain=domain)
                db.add(customer)
                db.flush()

            # Fix the IP blocking check query
            logger.info(f"Checking IP: {ip}, Domain: {domain}")
            ip_blocked = (
                db.query(IPList)
                .filter(
                    IPList.ip_address == ip,
                    IPList.is_blocked == True
                )
                .first()
            )
            if ip_blocked:
                logger.info(f"IP blocked: {ip_blocked}")
                raise HTTPException(status_code=403, detail="IP is blocked")
            logger.info(f"IP not blocked: {ip_blocked}")

            text_event = TextMessage(
                domain=domain,
                ip_address=ip,
                message=event.message,
                type=event.type,
            )
            db.add(text_event)
            db.flush()

            # Update background task call to remove extra parameters
            background_tasks.add_task(
                process_text_with_llm,
                db,
                text_event.id,
                event.message,
                ip,
                domain,
            )

            return {"status": "success", "id": text_event.id}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in create_text_event: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
