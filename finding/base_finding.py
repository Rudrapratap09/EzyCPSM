"""
base_finding.py
Base class for all EzyCPSM security findings
"""

import json
import datetime
from abc import ABC, abstractmethod
from ..core.logging_config import logger
from ..core.exceptions import FindingEvaluationError
from .finding_utils import get_property


class BaseFinding(ABC):
    """
    Abstract base class for all findings.
    Each finding evaluates ONE resource.
    """

    def __init__(self, db, scan_id):
        self.db = db
        self.scan_id = scan_id

        self.finding_type = self.get_finding_type()
        self.title = self.get_title()
        self.description = self.get_description()
        self.remediation = self.get_remediation()
        self.severity = self.get_severity()

        logger.debug(f"Initialized finding: {self.finding_type}")

    # ---------- REQUIRED METADATA ----------

    @abstractmethod
    def get_finding_type(self):
        pass

    @abstractmethod
    def get_title(self):
        pass

    @abstractmethod
    def get_description(self):
        pass

    @abstractmethod
    def get_remediation(self):
        pass

    @abstractmethod
    def get_severity(self):
        pass

    # ---------- OPTIONAL FILTER ----------

    def applies_to_resource(self, resource) -> bool:
        """
        Override this if a finding only applies to specific services/types.
        Default: applies to all resources.
        """
        return True

    # ---------- CORE LOGIC ----------

    @abstractmethod
    def evaluate(self, resource):
        """
        MUST return:
            (True, details_dict)  -> finding exists
            (False, {})           -> no finding
        """
        raise NotImplementedError

    def execute(self, resource) -> bool:
        """
        Executes evaluation and persists finding if applicable.
        """
        try:
            if not self.applies_to_resource(resource):
                return False

            is_finding, details = self.evaluate(resource)

            if not is_finding:
                return False

            finding_props = {
                "details": details or {},
                "resource_type": resource.resource_type,
                "service": resource.service,
                "region": resource.region,
                "evaluated_at": datetime.datetime.utcnow().isoformat()
            }

            self.db.store_finding(
                scan_id=self.scan_id,
                resource_pk=resource.id,
                finding_type=self.finding_type,
                severity=self.severity,
                title=self.title,
                description=self.description,
                remediation=self.remediation,
                properties=finding_props
            )

            logger.info(
                f"[{self.severity.upper()}] {self.finding_type} "
                f"on {resource.service}:{resource.resource_id}"
            )
            return True

        except Exception as e:
            logger.error(f"Finding {self.finding_type} failed: {e}")
            raise FindingEvaluationError(self.finding_type, resource.resource_id, str(e))

    # ---------- PROPERTY ACCESS ----------

    def prop(self, resource, key, default=None):
        """
        Shortcut for safe property access.
        """
        return get_property(resource, key, default)
