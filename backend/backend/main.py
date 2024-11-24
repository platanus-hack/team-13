from fastapi import FastAPI, HTTPException, Depends, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime
from zoneinfo import ZoneInfo
from sqlalchemy import desc
from typing import List
from .models import Base, TextMessage, IPList, Customer, LocalStorage
from .core.database import get_db, engine
from .api.endpoints import text, localStorage
import logging
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from .api.dependencies import get_client_ip
from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import Dict
from pydantic import BaseModel
import json
from os import getenv
import boto3


logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Anomal.AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=600,
)

app.include_router(text.router, prefix="/api")
app.include_router(localStorage.router, prefix="/api")


@app.options("/{full_path:path}")
async def options_handler(request: Request):
    return JSONResponse(
        content="OK",
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Headers": "Content-Type, Authorization, Origin, Accept",
            "Access-Control-Max-Age": "600",
        },
    )


@app.get("/is_blocked")
async def is_blocked(request: Request, db: Session = Depends(get_db)):
    ip, domain = get_client_ip(request, db=db)

    with db.begin():
        # Check if domain exists
        customer = db.query(Customer).filter(Customer.domain == domain).first()
        if not customer:
            customer = Customer(domain=domain)
            db.add(customer)
            db.flush()

        logger.info(f"Checking IP: {ip}, Domain: {domain}")
        ip_blocked = (
            db.query(IPList)
            .filter(IPList.ip_address == ip, IPList.is_blocked == True)
            .first()
        )

    if ip_blocked:
        logger.info(f"IP blocked: {ip_blocked}")
        raise HTTPException(status_code=403, detail="IP is blocked")
    logger.info(f"IP not blocked: {ip_blocked}")
    return {"ip": ip, "domain": domain, "is_blocked": bool(ip_blocked)}


@app.get("/")
async def read_root(db: Session = Depends(get_db)):
    try:
        db.execute("SELECT 1")
        return {"msg": "Health Ok", "database": "connected"}
    except Exception as e:
        return {"msg": "Health Ok", "database": "not connected", "error": str(e)}


# Pydantic models for response
class AttackLog(BaseModel):
    ip: str
    type_of_attack: str
    timestamp: datetime | None = None
    blocked: bool
    confidence_score: float | None = None
    is_malicious: bool | None = None
    is_local_storage: bool = False


class AttackLogsResponse(BaseModel):
    timestamp: datetime
    logs: List[AttackLog]


@app.get("/attack-logs", response_model=AttackLogsResponse)
async def get_attack_logs(db: Session = Depends(get_db)):
    # Get the current timestamp in UTC
    current_time = datetime.now(ZoneInfo("UTC"))

    # Query both TextMessage and LocalStorage tables
    text_messages = (
        db.query(TextMessage).order_by(desc(TextMessage.created_at)).limit(2550).all()
    )

    local_storage_messages = (
        db.query(LocalStorage).order_by(desc(LocalStorage.created_at)).limit(2550).all()
    )

    # Transform text messages
    text_logs = [
        AttackLog(
            ip=message.ip_address,
            type_of_attack=message.type,
            timestamp=message.created_at,
            blocked=message.caused_block if message.caused_block is not None else False,
            confidence_score=message.confidence_score,
            is_local_storage=False,
        )
        for message in text_messages
    ]

    # Transform localStorage messages
    storage_logs = [
        AttackLog(
            ip=message.ip_address,
            type_of_attack="localStorage",
            timestamp=message.created_at,
            blocked=message.blocked_at is not None,  # Use blocked_at to determine if it was blocked
            confidence_score=message.confidence_score,  # Use the actual confidence score
            is_malicious=message.is_malicious,  # Add is_malicious flag
            is_local_storage=True,
        )
        for message in local_storage_messages
    ]

    # Combine and sort both types of logs by timestamp
    all_logs = sorted(
        text_logs + storage_logs,
        key=lambda x: x.timestamp if x.timestamp else datetime.min,
        reverse=True,
    )[
        :2550
    ]  # Keep only the most recent 850 combined entries

    return AttackLogsResponse(timestamp=current_time, logs=all_logs)


@app.post("/unban-all")
async def unban_all(db: Session = Depends(get_db)):
    with db.begin():
        db.query(IPList).filter(IPList.is_blocked == True).update(
            {IPList.is_blocked: False}
        )
        db.flush()
    return {"msg": "All IPs unbanned"}


class AttackStats(BaseModel):
    total_attacks: int
    types_of_attacks: Dict[str, int]
    average_malicious_confidence: float
    total_blocked: int


@app.get("/stats", response_model=AttackStats)
async def get_attack_stats(db: Session = Depends(get_db)):
    # Get total number of attacks
    total_attacks = db.query(TextMessage).count()

    # Get counts of different types of attacks using group by
    type_counts = (
        db.query(TextMessage.type, func.count(TextMessage.id).label("count"))
        .group_by(TextMessage.type)
        .all()
    )

    # Convert the query results into a dictionary
    types_of_attacks = {attack_type: count for attack_type, count in type_counts}

    # Calculate average confidence score for malicious messages only
    avg_malicious_confidence = (
        db.query(func.avg(TextMessage.confidence_score))
        .filter(
            TextMessage.is_malicious is True, TextMessage.confidence_score.isnot(None)
        )
        .scalar()
        or 0.0
    )

    # Get total number of blocked attacks
    total_blocked = (
        db.query(TextMessage).filter(TextMessage.caused_block == True).count()
    )

    return AttackStats(
        total_attacks=total_attacks,
        types_of_attacks=types_of_attacks,
        average_malicious_confidence=round(avg_malicious_confidence, 2),
        total_blocked=total_blocked,
    )


@app.post("/replays-test")
async def save_html(request: Request):

    content = await request.body()
    parsed_data = ""

    CF_TOKEN = getenv("CF_TOKEN")
    CF_ACCESS_ID = getenv("CF_ACCESS_ID")
    CF_SECRET_ACCESS_KEY = getenv("CF_SECRET_ACCESS_KEY")
    CF_S3_ENDPOINT = getenv("CF_S3_ENDPOINT")

    s3_client = boto3.client(
        "s3",
        aws_access_key_id=CF_ACCESS_ID,
        aws_secret_access_key=CF_SECRET_ACCESS_KEY,
        endpoint_url=CF_S3_ENDPOINT,
    )

    content_str = content.decode("utf-8")
    content_dict = json.loads(content_str)

    for event in content_dict["events"]:
        parsed_data += json.dumps(event) + ","

    html_template = f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <meta http-equiv="X-UA-Compatible" content="ie=edge" />
    <title>Recording @IP</title>
    <link rel="stylesheet" href="../dist/style.css" />
  </head>
  <body>
    <script src="../dist/rrweb.umd.cjs"></script>
    <script>
      const events = [{parsed_data}];
      const replayer = new rrweb.Replayer(events, {{
        UNSAFE_replayCanvas: true,
      }});
      replayer.play();
    </script>
  </body>
</html>"""

    file_path = "/tmp/replay.html"
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(html_template)

    bucket_name = "replays-test-pv-hack"
    object_name = "test-replay/replay.html"

    try:
        s3_client.upload_file(file_path, bucket_name, object_name)
        print(f"File uploaded successfully to {bucket_name}/{object_name}")
    except Exception as e:
        print(f"Error uploading file: {e}")

    return {"status": "success", "id": 1}
