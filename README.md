# EzyCPSM

EzyCPSM is a lightweight Cloud Security Posture Management (CSPM) tool for AWS.
It is fully modular, fast, and designed for personal learning or production-grade automation.

## Features
- Modular scanner architecture — easily extend S3 / EC2 / IAM / VPC scanners
- SQLite backend (default: `ezycspm.db`)
- Parallel region scanning with live progress
- Clean logging system with colored console output and log files
- Designed for extensibility and readable codebase

## Quick Start
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
