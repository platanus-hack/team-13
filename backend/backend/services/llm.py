from openai import AsyncOpenAI
from typing import Dict, Literal
from enum import Enum
import json
from os import getenv
import logging

logger = logging.getLogger(__name__)

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

class LLMService:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=getenv("OPENAI_API_KEY"))

    async def analyze_text(
        self, event_id: int, text: str, ip: str, domain: str
    ) -> Dict:
        """Analyze text using OpenAI API to detect malicious content and attack type"""
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a cybersecurity analyst specialized in detecting web-based attacks. "
                            "Analyze the following input and determine:\n"
                            "1. **is_malicious**: Whether the text is malicious (true or false).\n"
                            "2. **attack_type**: The specific type of attack if malicious. "
                            "Choose one from ['sql_injection', 'xss', 'command_injection', 'path_traversal']. "
                            "If none apply, use 'unknown'. If not malicious, use 'normal'.\n"
                            "3. **confidence_score**: A confidence score between 0 and 1.\n"
                            "Respond **only** in the JSON format specified in the schema without additional text.\n\n"
                            "Examples:\n"
                            "Input: Text: 'SELECT * FROM users WHERE id = 1;'\n"
                            "Output: {\"is_malicious\": true, \"attack_type\": \"sql_injection\", \"confidence_score\": 0.95}\n\n"
                            "Input: Text: '<script>alert(\"XSS\")</script>'\n"
                            "Output: {\"is_malicious\": true, \"attack_type\": \"xss\", \"confidence_score\": 0.98}\n\n"
                            "Input: Text: 'Hello, I need help with my account.'\n"
                            "Output: {\"is_malicious\": false, \"attack_type\": \"normal\", \"confidence_score\": 0.99}"
                        ),
                    },
                    {
                        "role": "user",
                        "content": f"Domain: {domain}\nIP: {ip}\nText: {text}",
                    },
                ],
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "security_analysis_schema",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "is_malicious": {
                                    "description": "Whether the analyzed content is malicious",
                                    "type": "boolean",
                                },
                                "attack_type": {
                                    "description": "The specific type of attack if malicious",
                                    "type": "string",
                                    "enum": [
                                        "sql_injection",
                                        "xss",
                                        "command_injection",
                                        "path_traversal",
                                        "normal",
                                        "unknown"
                                    ],
                                },
                                "confidence_score": {
                                    "description": "Confidence score of the analysis (0-1)",
                                    "type": "number",
                                    "minimum": 0,
                                    "maximum": 1
                                    }
                                },
                                "required": ["is_malicious", "attack_type", "confidence_score"],
                                "additionalProperties": False,
                            },
                        },
                    },
                )
            analysis = json.loads(response.choices[0].message.content)
            attack_type = analysis["attack_type"]
            if attack_type not in AttackType._value2member_map_:
                attack_type = AttackType.UNKNOWN.value

            return {
                "event_id": event_id,
                "is_malicious": analysis["is_malicious"],
                "type": attack_type,
                "confidence_score": analysis["confidence_score"]
            }

        except Exception as e:
            logger.error(f"Error in OpenAI analysis: {str(e)}", exc_info=True)
            return {
                "event_id": event_id,
                "is_malicious": False,
                "type": AttackType.UNKNOWN.value,
                "confidence_score": 0
            }
