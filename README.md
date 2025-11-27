# 🌩️ Cloud Incident Response & Auto-Remediation System

> A hands-on, portfolio-ready cloud automation project featuring an EC2 auto-remediation engine, daily incident reporting, and a deployed Cloud Incident Dashboard (S3 + CloudFront).

---

## 🧭 Overview

A cloud-native Incident Response system designed to detect EC2 issues, run automated remediation, and generate daily human-readable incident reports.

The repository includes:

- A full Python auto-remediation engine (locally tested)

- A Markdown-based daily reporting pipeline

- A deployed Cloud Incident Dashboard (S3 + CloudFront), visualising daily reports stored in S3

---

## 📸 Screenshot

<img width="700" src="screenshots/dashboard-overview.png" />

---

## 🚀 Live Demo

The incident dashboard is deployed and accessible here:

👉 **https://d1uh2al28gwt3d.cloudfront.net/**

(Select a date to load a sample daily incident report.)

---

## 🔧 Current Status (As of Phase 5 Completion)

- ✅ Event routing and parsing (locally tested)
- ✅ Multi-rule auto-remediation engine (StatusCheckFailed, High CPU, Unexpected Stop)
- ✅ Structured incident logging layer (DynamoDB-ready; currently running in local/mock mode)
- ✅ Local event testing via manual CloudWatch-style JSON inputs (`lambda_handler.py`)
- ✅ Daily incident reporting pipeline (DynamoDB-like → Markdown → SES + S3) implemented and tested locally
- ✅ Cloud Incident Dashboard fully implemented and deployed (S3 + CloudFront)
- ✅ Dashboard UI: dark theme, metric cards, breakdown cards, incident table, raw Markdown viewer
- ✅ Sample daily reports generated locally and loaded from S3 into the dashboard

### 🧱 Next Phase (In progress)

- EventBridge scheduled reporting (daily automation)
- Web dashboard enhancements (charts, filters, optional auth)
- CI/CD automatic deployment

---

## 🏗 Architecture (Target design)

<img width="700" src="architecture-diagram.png" />

> Note: this is the target end-to-end architecture. At the moment, only the Dashboard (S3 + CloudFront) and S3-stored reports are deployed; the rest is implemented and tested locally.

- CloudWatch Alarms → SNS/EventBridge → Auto-Remediation Lambda
- Auto-Remediation Lambda → DynamoDB (incident log)
- EventBridge (daily cron) → Report Lambda → SES + S3
- Dashboard (S3 + CloudFront) → Renders daily reports from S3

---

## ✨ Features

### 🔁 Auto-Remediation Engine

- EC2 StatusCheckFailed → automatic reboot (DryRun)
- EC2 High CPU → structured logging
- EC2 Unexpected Stop → automatic start (DryRun)
- Unified event routing (CloudWatch payload → internal event type)

### 🗂 Incident Logging (DynamoDB-ready)

- Structured incident record:
  - id / created_at / event_type / remediation_type
  - instance_id / action / message / raw_event

### 📅 Daily Incident Report (Markdown → SES + S3)

- Query by date prefix
- Generates Markdown summary:
  - Total incidents
  - Success / Failed
  - Unique instances
  - By event type
  - By remediation type
- Archives to S3: daily-reports/YYYY-MM-DD.md
- (SES + scheduling ready but not yet deployed)

### 💻 Cloud Incident Dashboard (Deployed)

- Fetches Markdown from S3
- Parses and renders:
  - Metric cards
  - Breakdown cards
  - Incident details table
- Hosted on S3 + CloudFront (HTTPS CDN)

---

## 🔍 How It Works

1. CloudWatch Alarms publish events (simulated locally during development).
2. The Lambda handler parses the raw CloudWatch event, extracts the EC2 instance ID, and identifies the event type.
3. The event is routed to the correct remediation rule (StatusCheckFailed / HighCPU / UnexpectedStop).
4. Each remediation module performs an action (reboot, start instance, or logging).
5. The full incident record — including raw event, remediation result, timestamps — is saved into DynamoDB (`incident_events` table).
6. Daily report Lambda queries DynamoDB and generates human-readable summaries (Markdown).
7. Markdown is uploaded to S3
8. CloudFront dashboard fetches & renders the report

---

## 🛠 Tech Stack

- AWS: CloudWatch, SNS, Lambda, EC2, DynamoDB, EventBridge, SES, S3, CloudFront
- Python: boto3, structured remediation modules
- Frontend: HTML + CSS + Vanilla JS
- Tooling: GitHub Actions (planned), Docker (local Lambda testing)

---

## 📦 Setup (High Level)

- Create required AWS resources (Lambda, DynamoDB, SES, S3, alarms).
- Configure environment variables / IAM roles.
- Deploy Lambda code.
- Upload Markdown reports to S3
- Deploy dashboard to S3 + CloudFront

---

## 🚀 Future Improvements

- More remediation rules (RDS, ALB, CloudFront)
- Slack/Teams notification integration
- Fully-deployed backend (Lambda + DynamoDB + SES)
- EventBridge daily automated reporting
- Charts & trend analysis in dashboard
- One-click IaC deployment

---

## 🗂 Project Structure

```
cloud-incident-auto-remediation/
├── README.md
├── architecture-diagram.png              # ✅ Architecture diagram
├── requirements.txt                      # ✅ Lambda local/CI dependencies

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
│ ├── index.html                          # ✅ Dashboard page (S3 + CloudFront)
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
