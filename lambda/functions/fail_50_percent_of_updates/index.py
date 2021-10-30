"""Lambda function which generates errors, as an example state machine step."""
import random


def lambda_handler(event, _context):
    """
    Receive an event from Step Functions, fetch the RequestType,
    and generate a 50% chance to raise an exception when the CFN
    RequestType is "Update". This will allow Creates and Deletes to
    always succeed.
    """
    cfn_request_type = event["RequestType"]

    if random.choice([True, False]) and cfn_request_type == "Update":
        # 50% chance of raising an error, but only for Update calls
        raise RuntimeError("Execution failed")
