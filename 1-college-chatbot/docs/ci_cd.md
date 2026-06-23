# CI/CD Guide

## Overview
This project includes a GitHub Actions workflow at `.github/workflows/ci.yml`.

## Pipeline Stages
1. Test matrix on Python 3.11 and 3.12
2. Install dependencies from `requirements.txt`
3. Run test suite with `pytest -q`
4. Build Docker image to validate deployment artifact

## Trigger Conditions
- Push to `main` or `master`
- Pull request to `main` or `master`

## Notes
- Docker image is built for validation only (not pushed).
- Add registry login + push step later when deployment target is finalized.
