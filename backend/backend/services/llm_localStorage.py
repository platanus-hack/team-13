from openai import AsyncOpenAI
from typing import Dict
from enum import Enum
import json
from os import getenv
import logging

logger = logging.getLogger(__name__)

class StorageAttackType(str, Enum):
    XSS_STORAGE = "xss_storage"
    DATA_THEFT = "data_theft"
    SESSION_HIJACKING = "session_hijacking"
    TOKEN_THEFT = "token_theft"
    STORAGE_POISONING = "storage_poisoning"
    NORMAL = "normal"
    UNKNOWN = "unknown"

class LLMStorageService:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=getenv("OPENAI_API_KEY"))

    async def analyze_storage(
        self, event_id: int, storage_data: Dict, ip: str, domain: str
    ) -> Dict:
        """Analyze localStorage changes to detect malicious behavior"""
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a cybersecurity analyst specialized in detecting client-side storage attacks. "
                            "Analyze the following localStorage changes and determine:\n"
                            "1. **is_malicious**: Whether the storage modification is suspicious (true or false).\n"
                            "2. **attack_type**: The specific type of attack if malicious. "
                            "Choose from ['xss_storage', 'data_theft', 'session_hijacking', 'token_theft', 'storage_poisoning']. "
                            "If none apply, use 'unknown'. If not malicious, use 'normal'.\n"
                            "3. **confidence_score**: A confidence score between 0 and 1.\n"
                            "Pay special attention to:\n"
                            "- Attempts to store XSS payloads\n"
                            "- Unauthorized token or session data modifications\n"
                            "- Suspicious data exfiltration patterns\n"
                            "- Modifications to security-related keys\n"
                            "Respond in JSON format only.\n\n"
                            "Examples:\n"
                            "Input: {\"key\": \"userToken\", \"old\": \"abc123\", \"new\": \"\"}\n"
                            "Output: {\"is_malicious\": true, \"attack_type\": \"token_theft\", \"confidence_score\": 0.85}\n\n"
                            "Input: {\"key\": \"theme\", \"old\": \"light\", \"new\": \"dark\"}\n"
                            "Output: {\"is_malicious\": false, \"attack_type\": \"normal\", \"confidence_score\": 0.95}"
                        ),
                    },
                    {
                        "role": "user",
                        "content": f"Domain: {domain}\nIP: {ip}\nStorage Changes: {json.dumps(storage_data, indent=2)}",
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
                                "type": "boolean",
                                },
                                "attack_type": {
                                    "type": "string",
                                    "enum": [
                                        "xss_storage",
                                        "data_theft",
                                        "session_hijacking",
                                        "token_theft",
                                        "storage_poisoning",
                                        "normal",   
                                        "unknown"
                                    ],
                                },
                                "confidence_score": {
                                    "type": "number",
                                    "minimum": 0,
                                    "maximum": 1
                                }
                            },
                            "required": ["is_malicious", "attack_type", "confidence_score"],
                        },
                    },
                },
            )

            analysis = json.loads(response.choices[0].message.content)
            attack_type = analysis["attack_type"]
            if attack_type not in StorageAttackType._value2member_map_:
                attack_type = StorageAttackType.UNKNOWN.value

            return {
                "event_id": event_id,
                "is_malicious": analysis["is_malicious"],
                "type": attack_type,
                "confidence_score": analysis["confidence_score"]
            }

        except Exception as e:
            logger.error(f"Error in OpenAI storage analysis: {str(e)}", exc_info=True)
            return {
                "event_id": event_id,
                "is_malicious": False,
                "type": StorageAttackType.UNKNOWN.value,
                "confidence_score": 0
            }