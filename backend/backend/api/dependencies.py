from typing import Tuple
from fastapi import Request, HTTPException, Depends
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..models import IPList, Customer
from ipaddress import ip_address as validate_ip
import logging

logger = logging.getLogger(__name__)

def get_client_ip(
    request: Request, 
    db: Session,
    require_origin: bool = False
) -> Tuple[str, str]:
    """
    Get client IP and domain from request and ensure IP exists in database
    Returns:
        Tuple[str, str]: Tuple of (ip_address, domain)
    """
    logger.info("Starting get_client_ip function")
    
    # Get IP - check headers in priority order
    ip = None
    
    # Log all relevant headers for debugging
    logger.debug(f"Headers received: CF-Connecting-IP: {request.headers.get('CF-Connecting-IP')}, "
                f"X-Real-IP: {request.headers.get('X-Real-IP')}, "
                f"X-Forwarded-For: {request.headers.get('X-Forwarded-For')}")
    
    if request.headers.get("CF-Connecting-IP"):
        ip = request.headers.get("CF-Connecting-IP")
        logger.info(f"Using CF-Connecting-IP: {ip}")
    elif request.headers.get("X-Real-IP"):
        ip = request.headers.get("X-Real-IP")
        logger.info(f"Using X-Real-IP: {ip}")
    elif request.headers.get("X-Forwarded-For"):
        ip = request.headers.get("X-Forwarded-For").split(",")[0].strip()
        logger.info(f"Using X-Forwarded-For: {ip}")
    
    if not ip:
        ip = request.client.host
        logger.info(f"Using direct client IP: {ip}")
    
    # Validate IP format
    try:
        validate_ip(ip)
        logger.debug(f"IP validation successful for: {ip}")
    except ValueError as e:
        logger.error(f"Invalid IP address format: {ip}, error: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid IP address format")
    
    if not ip:
        logger.error("No IP address could be determined")
        raise HTTPException(status_code=400, detail="Could not determine client IP")
    
    # Domain processing
    domain = request.headers.get("Origin", "")
    logger.info(f"Original domain from Origin header: {domain}")
    
    if domain:
        try:
            domain = domain.replace("http://", "").replace("https://", "")
            domain = domain.split(":")[0].strip()
            logger.info(f"Processed domain: {domain}")
        except Exception as e:
            logger.error(f"Error processing domain: {str(e)}")
            domain = ""
    
    if require_origin and not domain:
        logger.error("Origin header required but not provided or invalid")
        raise HTTPException(status_code=400, detail="Valid Origin header is required")
    
    try:
        # Check if IP exists in database
        logger.debug(f"Querying database for IP: {ip}")
        ip_entry = db.query(IPList).filter(IPList.ip_address == str(ip)).first()
        
        if not ip_entry:
            logger.info(f"Creating new IP entry for {ip} with domain {domain}")
            ip_entry = IPList(
                ip_address=str(ip),
                domain=domain,
                is_blocked=False
            )
            db.add(ip_entry)
        else:
            logger.info(f"Found existing IP entry for {ip}")
            if domain and not ip_entry.domain:
                logger.info(f"Updating domain for existing IP from '' to {domain}")
                ip_entry.domain = domain
        
        logger.debug("Attempting to commit changes to database")
        db.commit()
        logger.info("Database commit successful")
        
    except Exception as e:
        logger.error(f"Database operation failed: {str(e)}", exc_info=True)
        db.rollback()
        logger.info("Database rollback completed")
        raise HTTPException(status_code=500, detail="Failed to update IP database")
    
    logger.info(f"Successfully returning IP: {ip} and domain: {domain}")
    return ip, domain