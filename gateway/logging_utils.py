"""
Compliance audit logging utilities for the Sovereign AI Gateway.
"""

import json
import logging
import os
from datetime import datetime
from typing import Optional
from .models import AuditLogEntry


class ComplianceLogger:
    """
    Handles compliance audit logging for data sovereignty enforcement.

    Logs to both file (sovereign_audit.log) and structured JSON format.
    """

    def __init__(self, log_file: str = "sovereign_audit.log"):
        self.log_file = log_file
        self.log_dir = os.path.dirname(log_file) if os.path.dirname(log_file) else "."

        # Ensure log directory exists
        os.makedirs(self.log_dir, exist_ok=True)

        # Setup structured logger
        self.logger = logging.getLogger("sovereign_audit")
        self.logger.setLevel(logging.INFO)

        # File handler for audit log
        if not self.logger.handlers:
            file_handler = logging.FileHandler(self.log_file)
            file_handler.setLevel(logging.INFO)

            # JSON formatter for structured logging
            formatter = logging.Formatter("%(message)s", datefmt="%Y-%m-%d %H:%M:%S")
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

            # Also log to console in development
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            console_formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
            )
            console_handler.setFormatter(console_formatter)
            self.logger.addHandler(console_handler)

    def log_request(
        self,
        route: str,
        pii_score: float,
        pii_types: list[str],
        model_used: str,
        prompt_length: int,
        response_length: int,
        processing_time_ms: float,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        ip_address: Optional[str] = None,
    ):
        """
        Log a gateway request for compliance auditing.

        This creates an audit trail suitable for:
        - ISO 27001 compliance
        - ASD Essential 8 evidence
        - Data sovereignty verification
        """
        entry = AuditLogEntry(
            timestamp=datetime.now(),
            route=route,
            pii_score=pii_score,
            pii_types=pii_types,
            model_used=model_used,
            user_id=user_id,
            session_id=session_id,
            ip_address=ip_address,
            prompt_length=prompt_length,
            response_length=response_length,
            processing_time_ms=processing_time_ms,
        )

        # Log as JSON for structured querying
        log_data = {
            "timestamp": entry.timestamp.isoformat(),
            "route": entry.route,
            "pii_score": entry.pii_score,
            "pii_types": entry.pii_types,
            "model_used": entry.model_used,
            "user_id": entry.user_id,
            "session_id": entry.session_id,
            "ip_address": entry.ip_address,
            "prompt_length": entry.prompt_length,
            "response_length": entry.response_length,
            "processing_time_ms": entry.processing_time_ms,
            "sovereignty_enforced": entry.route == "sovereign",
        }

        # Write JSON line to log file
        self.logger.info(json.dumps(log_data))

        # Also write human-readable summary
        summary = (
            f"[AUDIT] {entry.timestamp.isoformat()} | "
            f"Route: {entry.route.upper()} | "
            f"PII Score: {entry.pii_score:.2f} | "
            f"PII Types: {', '.join(entry.pii_types) if entry.pii_types else 'None'} | "
            f"Model: {entry.model_used} | "
            f"Processing: {entry.processing_time_ms:.1f}ms"
        )
        self.logger.info(summary)

        # Flush handlers to ensure data is written
        for handler in self.logger.handlers:
            handler.flush()

    def get_recent_logs(self, limit: int = 100) -> list[dict]:
        """
        Read recent log entries from the audit log file.

        Returns:
            List of parsed log entries (most recent first)
        """
        logs = []

        if not os.path.exists(self.log_file):
            return logs

        try:
            with open(self.log_file, "r") as f:
                lines = f.readlines()

            # Parse JSON lines (most recent at end)
            for line in reversed(lines[-limit:]):
                line = line.strip()
                if line.startswith("{"):
                    try:
                        log_entry = json.loads(line)
                        logs.append(log_entry)
                    except json.JSONDecodeError:
                        continue

        except Exception as e:
            self.logger.error(f"Error reading audit log: {e}")

        return logs
