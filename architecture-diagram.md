flowchart TD

    subgraph CloudWatch Monitoring
        A1[CloudWatch Alarm<br/>EC2 CPU/Status/Stop] --> A2[SNS Notification]
    end

    A2 --> B1[Auto-Remediation Lambda<br/>src/lambda_handler.py]

    subgraph Remediation
        B1 --> B2[event_router.py]
        B1 --> B3[Remediation Rules<br/>ec2_status_check.py<br/>ec2_high_cpu.py<br/>ec2_unexpected_stop.py]
    end

    B1 --> C1[(DynamoDB<br/>incident_events)]

    %% Daily Report System
    subgraph Daily_Report_System
        D1[EventBridge<br/>Daily Schedule] --> D2[Daily Report Lambda<br/>daily_report_lambda.py]

        D2 --> D3[daily_report.py<br/>Generate Markdown]
        D2 --> D4[send_email.py<br/>SES Email]
        D2 --> D5[S3 Upload<br/>daily-reports/YYYY-MM-DD.md]
    end

    C1 -. query incidents .-> D2

    D4 --> E1[(Amazon SES)]
    D5 --> E2[(Amazon S3)]
