import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))
from src.lambda_handler import lambda_handler


def load_sample_event():

    return {
        "version": "0",
        "id": "abcd-efgh-1234-5678",
        "detail-type": "CloudWatch Alarm State Change",
        "source": "aws.cloudwatch",
        "account": "123456789012",
        "time": "2025-01-01T00:00:00Z",
        "region": "ap-southeast-2",
        "resources": [
            "arn:aws:cloudwatch:ap-southeast-2:123456789012:alarm:StatusCheckFailed"
        ],
        "detail": {
            "alarmName": "StatusCheckFailed",
            "state": {
                "value": "ALARM",
                "reason": "StatusCheckFailed > 0 for 1 datapoints...",
            },
            "configuration": {
                "metrics": [
                    {
                        "metricStat": {
                            "metric": {
                                "namespace": "AWS/EC2",
                                "metricName": "StatusCheckFailed",
                                "dimensions": [
                                    {
                                        "name": "InstanceId",
                                        "value": "i-1234567890abcdef0",
                                    }
                                ],
                            },
                            "period": 60,
                            "stat": "Minimum",
                        }
                    }
                ]
            },
        },
    }


if __name__ == "__main__":
    # sample
    event = load_sample_event()

    # src/lambda_handler.py
    result = lambda_handler(event, context=None)

    # print result
    print("=== Lambda Result ===")
    print(json.dumps(result, indent=2, ensure_ascii=False))
