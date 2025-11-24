# Cloud Incident Response & Auto-Remediation System

## Overview

Short description (2–3 sentences).

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
- Daily incident report (Lambda + SES)
- Optional web dashboard
- CI/CD via GitHub Actions

## Project Structure

(Brief tree)

- `src/` – Lambdas (handler, remediation, reporting)
- `infra/` – IaC templates (alarms, roles, tables)
- `scripts/` – Local test & simulation scripts
- `dashboard/` – Optional HTML/JS UI
- `reports/` – Sample reports
- `.github/workflows/` – CI/CD pipeline

## How It Works

1. CloudWatch triggers alarms.
2. SNS sends alarm events to Lambda.
3. Lambda analyzes the event and runs remediation.
4. Incidents are stored in DynamoDB.
5. Daily job generates and emails a report.
6. Dashboard displays recent incidents (optional).

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

cloud-incident-auto-remediation/
├── README.md
├── architecture-diagram.png # 架构图（建议生成后放这里）
├── requirements.txt # Lambda 本地/CI 需要的依赖

├── src/
│ ├── lambda_handler.py # 主自动修复 Lambda（解析事件 -> 分发到不同 remediation）
│ ├── event_router.py # 分析事件类型（CPU, StatusCheck, 健康状态等）
│ │
│ ├── remediation/ # 自动修复模块
│ │ ├── ec2_status_check.py # StatusCheckFailed 自动修复
│ │ ├── ec2_high_cpu.py # 高 CPU 场景
│ │ ├── ec2_unexpected_stop.py # 非预期停止 -> 自动启动
│ │ └── **init**.py
│ │
│ ├── reporting/
│ │ ├── daily_report.py # 从 DynamoDB 读取 -> 生成日报
│ │ ├── send_email.py # 通过 SES 发送报告
│ │ └── **init**.py
│ │
│ ├── storage/
│ │ ├── dynamodb_client.py # 写入/读取事件日志
│ │ ├── s3_client.py # 可选：把事件写 S3 JSON
│ │ └── **init**.py
│ │
│ ├── utils/
│ │ ├── aws_clients.py # boto3 clients/resource 统一生成
│ │ ├── config.py # 配置项，例如表名、桶名、邮件地址
│ │ ├── logging_utils.py # Lambda 统一日志格式
│ │ └── **init**.py
│ │
│ └── **init**.py

├── infra/ # 基础设施定义（可以先不写 IaC，留空即可）
│ ├── cloudwatch-alarms.yaml # CloudWatch + SNS 的 IaC（可选）
│ ├── lambda-roles-policies.yaml # IAM 权限/Trust policy
│ ├── dynamodb-table.yaml # DynamoDB 表结构
│ └── eventbridge-rules.yaml # 每日报告 cron 规则

├── scripts/
│ ├── simulate_event.py # 本地模拟 CloudWatch Alarm（重要）
│ ├── seed_sample_data.py # 生成测试事件到 DynamoDB
│ └── manual_report.py # 本地手动生成日报

├── dashboard/
│ ├── index.html # 前端仪表盘（可选）
│ ├── app.js
│ └── styles.css

├── reports/
│ ├── sample-daily-report.md # 报告样例（面试官最喜欢看）
│ └── sample-event-log.json

├── docker/
│ ├── Dockerfile # 本地调试 Lambda / 事件模拟
│ └── README.md

└── .github/
└── workflows/
└── deploy.yml # GitHub Actions CI/CD：自动打包 + 更新 Lambda + 同步前端
