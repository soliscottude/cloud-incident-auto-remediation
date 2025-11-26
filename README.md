# Cloud Incident Response & Auto-Remediation System

## Overview

A fully serverless Cloud Incident Response system that automatically detects EC2 issues, runs remediation actions, and logs every incident into DynamoDB.  
Supports multiple remediation rules (StatusCheckFailed, High CPU, Unexpected Stop), event routing, and structured incident logging ready for daily reporting and dashboard visualization.

## Current Status (Completed)

- ✅ Event routing and parsing
- ✅ Full remediation engine with multiple EC2 rules
- ✅ DynamoDB incident logging
- ✅ Local event simulation working (simulate_event.py)
- ✅ Daily incident reporting system (DynamoDB → Markdown → SES + S3)

### Next Phase (In progress)

- EventBridge scheduled reporting (daily automation)
- Web dashboard (S3 + CloudFront)
- CI/CD automatic deployment

## Architecture

(Insert architecture-diagram.png here)

- CloudWatch Alarms → SNS → Lambda
- Lambda → DynamoDB (incident log)
- EventBridge → Daily Report Lambda → SES + S3
- Optional: Dashboard (S3 + CloudFront)

## Features

- Real-time monitoring (EC2 health & metrics)
- Auto-remediation (e.g. reboot on StatusCheckFailed)
- Incident logging (DynamoDB)

### Daily incident report (Lambda + SES + S3)

- On-demand execution (ready for automation)
- Generates Markdown summary for a target date
- Queries DynamoDB by date (`created_at` prefix)
- Sends formatted report via Amazon SES
- Archives each report to S3 (`daily-reports/YYYY-MM-DD.md`)
- Fully serverless architecture
- _(EventBridge scheduled automation planned)_

- Optional web dashboard
- CI/CD via GitHub Actions

- Multi-rule auto-remediation engine
  - EC2 StatusCheckFailed → automatic reboot (DryRun)
  - EC2 High CPU → detection and structured logging
  - EC2 Unexpected Stop → automatic start (DryRun)
- Event router (parse & classify CloudWatch payloads)

- Structured incident logging (DynamoDB)
- Raw event archiving for audit/debugging

## Project Structure

(Brief tree)

- `src/` – Lambdas (handler, remediation, reporting)
- `infra/` – IaC templates (alarms, roles, tables)
- `scripts/` – Local test & simulation scripts
- `dashboard/` – Optional HTML/JS UI
- `reports/` – Sample reports
- `.github/workflows/` – CI/CD pipeline

## How It Works

1. CloudWatch Alarms publish events (simulated locally during development).
2. The Lambda handler parses the raw CloudWatch event, extracts the EC2 instance ID, and identifies the event type.
3. The event is routed to the correct remediation rule (StatusCheckFailed / HighCPU / UnexpectedStop).
4. Each remediation module performs an action (reboot, start instance, or logging).
5. The full incident record — including raw event, remediation result, timestamps — is saved into DynamoDB (`incident_events` table).
6. Daily report Lambda queries DynamoDB and generates human-readable summaries (Markdown).

## Tech Stack

- AWS: CloudWatch, SNS, Lambda, EC2, DynamoDB, EventBridge, SES, S3, CloudFront
- Python + boto3
- GitHub Actions

## Setup (High Level)

- Create required AWS resources (Lambda, DynamoDB, SES, S3, alarms).
- Configure environment variables / IAM roles.
- Deploy Lambda code.
- (Optional) Deploy dashboard & CI/CD workflow.

## Future Improvements

- More remediation rules (RDS, S3, CloudFront…)
- Slack/Teams notifications
- Advanced anomaly detection

## Structure

```
cloud-incident-auto-remediation/
├── README.md
├── architecture-diagram.png              # Architecture diagram (recommended)
├── requirements.txt                      # Lambda local/CI dependencies

├── src/
│ ├── lambda_handler.py                   # ✅ Main remediation Lambda (parse → route → remediate)
│ ├── event_router.py                     # ✅ Event type classifier (CPU, StatusCheckFailed, Stop)
│ ├── daily_report_lambda.py              # ✅ Daily report Lambda (DynamoDB → SES + S3)
│ │
│ ├── remediation/                        # Auto-remediation rules
│ │ ├── ec2_status_check.py               # ✅ StatusCheckFailed remediation
│ │ ├── ec2_high_cpu.py                   # ✅ High CPU remediation (MVP)
│ │ ├── ec2_unexpected_stop.py            # ✅ Unexpected Stop → auto-start (DryRun)
│ │ └── __init__.py
│ │
│ ├── reporting/                          # Daily report modules (Phase 4)
│ │ ├── daily_report.py                   # ✅ Generate daily report from DynamoDB
│ │ ├── send_email.py                     # ✅ Send report via SES
│ │ └── __init__.py
│ │
│ ├── storage/
│ │ ├── dynamodb_client.py                # ✅ Write/read incidents (incident_events table)
│ │ └── __init__.py
│ │
│ ├── utils/
│ │ ├── aws_clients.py                    # ✅ boto3 client/resource factory
│ │ ├── config.py                         # ☐ Configuration (table names, buckets, emails)
│ │ ├── logging_utils.py                  # ☐ Unified Lambda logging format
│ │ └── __init__.py
│ │
│ └── __init__.py

├── infra/                                # IaC definitions (optional for now)
│ ├── cloudwatch-alarms.yaml              # ☐ CloudWatch + SNS alarm definitions
│ ├── lambda-roles-policies.yaml          # ☐ IAM permissions / trust policies
│ ├── dynamodb-table.yaml                 # ☐ incident_events table definition
│ └── eventbridge-rules.yaml              # ☐ Daily cron rule for report Lambda

├── scripts/
│ ├── simulate_event.py                   # ✅ Local CloudWatch event simulator
│ ├── seed_sample_data.py                 # ☐ Write sample incidents to DynamoDB
│ └── manual_report.py                    # ☐ Local manual report generator

├── dashboard/                            # Optional front-end dashboard
│ ├── index.html                          # ☐ Dashboard page (S3 + CloudFront)
│ ├── app.js
│ └── styles.css

├── reports/
│ ├── sample-daily-report.md              # ✅ Example of daily report (for recruiters)
│ └── sample-event-log.json               # ✅ Example of logged incident

├── docker/
│ ├── Dockerfile                          # ☐ Local Lambda/testing Docker image
│ └── README.md

└── .github/
    └── workflows/
        └── deploy.yml                    # ☐ GitHub Actions CI/CD pipeline

```
