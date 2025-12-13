"""
scanner_runner.py
Run scanner classes across regions for EzyCPSM.
"""

import datetime
from typing import List, Optional, Type
from ..core.logging_config import logger
from ..core.aws_client import AWSClient
from ..core.parallel_executor import ParallelExecutor


class ScannerRunner:
    """
    Orchestrates scanner classes across regions.

    scanner_classes: list of scanner classes (not instances). Each scanner_class should accept:
        scanner_class(aws_client, account_id, region, db_manager=None, scan_id=None)
    """

    def __init__(
        self,
        scanner_classes: Optional[List[Type]] = None,
        regions: Optional[List[str]] = None,
        db_manager=None,
        scan_id: Optional[str] = None,
        aws_creds: dict = None,
        parallel_workers: int = 8,
    ):
        self.scanner_classes = scanner_classes or []
        self.provided_regions = regions
        self.db_manager = db_manager
        self.aws_creds = aws_creds or {}
        self.parallel_workers = parallel_workers
        self.scan_id = scan_id or f"ezycspm_{int(datetime.datetime.now().timestamp())}"

        if self.db_manager is None:
            logger.warning("No DB manager provided — resources/findings won't be saved")

        logger.info(f"ScannerRunner initialized (scan_id={self.scan_id})")

    def create_aws_client(self, region: Optional[str] = None) -> AWSClient:
        creds = self.aws_creds or {}
        return AWSClient(
            aws_access_key_id=creds.get("aws_access_key_id"),
            aws_secret_access_key=creds.get("aws_secret_access_key"),
            aws_session_token=creds.get("aws_session_token"),
            region=region or creds.get("region") or "us-east-1",
        )

    def run_region(self, region: str) -> None:
        """Run all configured scanner classes in a single region."""
        logger.info(f"Processing region: {region}")
        try:
            aws_client = self.create_aws_client(region)
            account_id = aws_client.account_id
            logger.info(f"AWS client ready for account {account_id} in region {region}")

            for scanner_class in self.scanner_classes:
                try:
                    scanner = scanner_class(
                        aws_client,
                        account_id,
                        region,
                        db_manager=self.db_manager,
                        scan_id=self.scan_id,
                    )
                    logger.info(f"Running {scanner_class.__name__} in {region}")
                    scanner.execute()
                except Exception as e:
                    logger.error(f"Scanner {scanner_class.__name__} failed in {region}: {e}")
        except Exception as e:
            logger.error(f"Failed to run region {region}: {e}")

    def run_all_regions(self, regions: Optional[List[str]] = None, use_parallel: bool = True) -> None:
        """
        Run scanners across provided regions, or auto-detect from AWS if not provided.
        """
        regions_to_run = regions or self.provided_regions
        if not regions_to_run:
            # auto-detect using default AWS client
            aws = self.create_aws_client()
            try:
                regions_to_run = aws.get_account_regions()
            except Exception as e:
                logger.error(f"Could not auto-detect regions: {e}")
                regions_to_run = [aws.region]  # fallback to default region

        logger.info(f"Starting scan across {len(regions_to_run)} regions")

        if use_parallel:
            executor = ParallelExecutor(max_workers=self.parallel_workers, description="Scanning Regions")
            tasks = [(self.run_region, (r,), {}) for r in regions_to_run]
            executor.execute(tasks, show_progress=True)
        else:
            for r in regions_to_run:
                self.run_region(r)
