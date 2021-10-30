import json
import requests


def lambda_handler(event, _context):
    """Return a success or failure to the CFN Custom Resource."""
    print(json.dumps(event))
    cfn_url = event["ExecutionInput"]["ResponseURL"]
    cfn_stack_id = event["ExecutionInput"]["StackId"]
    cfn_request_id = event["ExecutionInput"]["RequestId"]
    logical_resource_id = event["ExecutionInput"]["LogicalResourceId"]

    lambda_results = event["LambdaResults"]

    # Successful Lambda executions will look like this:
    # "LambdaResults": {
    #     "ExecutedVersion": "$LATEST",
    #     "Payload": null,
    #     ...
    # }
    #
    # While failing results look like this:
    # "LambdaResults": {
    #     "Error": "RuntimeError",
    #     "Cause": "..."
    # }
    success = "Error" not in lambda_results.keys()

    json_body = {
        "Status": "SUCCESS" if success else "FAILED",
        "Reason": f'State Machine {"succeeded" if success else "failed"}',
        "PhysicalResourceId": logical_resource_id,
        "StackId": cfn_stack_id,
        "RequestId": cfn_request_id,
        "LogicalResourceId": logical_resource_id,
    }

    requests.put(
        url=cfn_url,
        json=json_body,
    )
