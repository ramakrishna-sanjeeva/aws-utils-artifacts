import boto3 as boto3
import requests
import logging
import json

from enum import Enum
from joblib import Parallel, delayed
from jsonpath import JSONPath

# Set Logging
logger = logging.getLogger('app-healthcheck-2-aws-cw-metrics')
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

# Type of healthcheck supported
class HTTPHealthCheckType(Enum):
    STATUS_CHECK = 0
    RESPONSE_BODY_CHECK = 1
    RESPONSE_BODY_JSON_EVALUATE = 2

# HTTP Endpoint healthcheck object
class TargetHTTPService:
    name = ""
    url = ""
    health_check_type = None
    status_code_check = None
    expected_response = None
    response_json_path = None
    timeout = 1

    def __init__(self, name, url, health_check_type=None, status_code_check=None, timeout=1, expected_response=None, response_json_path=None):
        self.name = name
        self.url = url
        self.status_code_check = status_code_check
        self.health_check_type = health_check_type
        self.timeout = timeout
        self.expected_response = expected_response
        self.response_json_path = response_json_path

    def perform_health_check(self):
        health_check = False
        try:
            http_response = requests.get(self.url, timeout=self.timeout)
            status = http_response.status_code
            if self.health_check_type == HTTPHealthCheckType.STATUS_CHECK and self.status_code_check and status == self.status_code_check:
                health_check = True
            elif self.health_check_type == HTTPHealthCheckType.RESPONSE_BODY_CHECK and self.expected_response == http_response.text:
                health_check = True
            elif self.health_check_type == HTTPHealthCheckType.RESPONSE_BODY_JSON_EVALUATE:
                health_check_str = JSONPath(self.response_json_path).parse(json.loads(http_response.text))[0]
                if health_check_str == self.expected_response:
                    health_check = True
        except Exception as e:
            logger.exception("Exception in invoking healthcheck for service: " + self.name)
        return health_check

# Configure all required healths here
app_health_checks = [
    TargetHTTPService(name="Google",
                      url="http://www.google.com",
                      health_check_type=HTTPHealthCheckType.STATUS_CHECK,
                      status_code_check=200),
    TargetHTTPService(name="SpringBootApp",
                      url="http://localhost:9001/actuator/health",
                      health_check_type=HTTPHealthCheckType.RESPONSE_BODY_JSON_EVALUATE,
                      response_json_path="$.status",
                      expected_response="UP")
]

app_health_check_cloudwatch_metric_data = []
instance_id = requests.get("http://169.254.169.254/latest/meta-data/instance-id").text

# Invoke healthcheck
def perform_healthcheck(app_health_check):
    health_check_status = app_health_check.perform_health_check()
    app_health_check_cloudwatch_metric_data.append({
        'MetricName': 'Process Status',
        'Dimensions': [
            {
                'Name': 'InstanceId',
                'Value': instance_id
            }, {
                'Name': 'Process',
                'Value': app_health_check.name
            }
        ],
        'Value': health_check_status and 1 or 0
    })

# Peform required healthchecks
Parallel(backend="threading")(delayed(perform_healthcheck)(app_health_check) for app_health_check in app_health_checks)

# Publish to CloudWatch. Configure the right namespace below
cloudwatch = boto3.client('cloudwatch')
logger.debug("CW Metric Data: " + str(app_health_check_cloudwatch_metric_data))
response = cloudwatch.put_metric_data(
    Namespace='App-Workserver',
    MetricData=app_health_check_cloudwatch_metric_data
)
