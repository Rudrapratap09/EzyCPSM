"""
finding_runner.py
Runs all findings against collected resources
"""

from ..core.logging_config import logger


class FindingRunner:
    """
    Evaluates findings for all resources in a given account & region.
    """

    def __init__(self, db, scan_id, finding_classes):
        self.db = db
        self.scan_id = scan_id
        self.finding_classes = finding_classes
        self.results = []

    def run(self, account_id, region):
        """
        Run all findings against resources in an account + region.
        """
        resources = self.db.get_resources_by_account_and_region(account_id, region)

        logger.info(
            f"Running {len(self.finding_classes)} findings "
            f"against {len(resources)} resources "
            f"in {account_id}:{region}"
        )

        for resource in resources:
            for finding_cls in self.finding_classes:
                try:
                    finding = finding_cls(self.db, self.scan_id)
                    if finding.execute(resource):
                        self.results.append({
                            "resource_id": resource.resource_id,
                            "finding_type": finding.finding_type,
                            "severity": finding.severity
                        })
                except Exception as e:
                    logger.error(
                        f"Finding {finding_cls.__name__} failed "
                        f"for resource {resource.resource_id}: {e}"
                    )

        logger.info(f"Findings completed: {len(self.results)} issues found")
        return self.results
