"""Module for the main CfnCustomResourcesBackedByStepFunctions Stack."""

# Standard library imports
import time

# Related third party imports
# -

# Local application/library specific imports
from aws_cdk import (
    core as cdk,
    aws_lambda as lambda_,
    aws_stepfunctions as sfn,
    aws_stepfunctions_tasks as sfn_tasks,
)


class CfnCustomResourcesBackedByStepFunctionsStack(cdk.Stack):
    """The CfnCustomResourcesBackedByStepFunctions Stack."""

    def __init__(
        self,
        scope: cdk.Construct,
        construct_id: str,
        config: dict,  # pylint: disable=unused-argument
        **kwargs,
    ) -> None:
        """Construct a new CfnCustomResourcesBackedByStepFunctionsStack."""
        super().__init__(scope, construct_id, **kwargs)

        # Define the Lambda functions for the state machine
        fail_50_percent_lambda = lambda_.Function(
            scope=self,
            id="Fail50PercentOfUpdates",
            code=lambda_.Code.from_asset("lambda/functions/fail_50_percent_of_updates"),
            handler="index.lambda_handler",
            runtime=lambda_.Runtime.PYTHON_3_9,
        )

        requests_layer = lambda_.LayerVersion(
            scope=self,
            id="RequestsLayer",
            code=lambda_.Code.from_asset("lambda/layers/requests_layer/python.zip"),
        )

        update_cfn_lambda = lambda_.Function(
            scope=self,
            id="UpdateCfnLambda",
            code=lambda_.Code.from_asset("lambda/functions/update_cfn_custom_resource"),
            handler="index.lambda_handler",
            runtime=lambda_.Runtime.PYTHON_3_9,
            layers=[requests_layer],
        )

        # The State Machine looks like this:
        #               Start
        #                 |
        #                 V
        #
        #   Lambda (fails 50% of the time)
        #
        #                | |
        #        success \ / catch
        #                 V
        #
        #       Lambda (update CFN)

        fail_50_percent_step = sfn_tasks.LambdaInvoke(
            scope=self,
            id="Lambda (Fail 50%)",
            lambda_function=fail_50_percent_lambda,
            retry_on_service_exceptions=False,
        )

        update_cfn_step = sfn_tasks.LambdaInvoke(
            scope=self,
            id="Update CloudFormation",
            lambda_function=update_cfn_lambda,
            # We pass both the original execution input AND the lambda execution
            # results to the Update CloudFormation Lambda. The function will use
            # the Lambda execution results to determine success or failure, and will
            # use the original Step Functions Execution Input to fetch the CloudFormation
            # callback parameters (ResponseURL, StackId, RequestId and LogicalResourceId).
            payload=sfn.TaskInput.from_object(
                {
                    "ExecutionInput": sfn.JsonPath.string_at("$$.Execution.Input"),
                    "LambdaResults.$": "$",
                }
            ),
        )

        # Make sure failures are also handled by the update_cfn_step
        fail_50_percent_step.add_catch(handler=update_cfn_step, errors=["States.ALL"])

        # Create the state machine.
        state_machine = sfn.StateMachine(
            self,
            "StateMachine",
            definition=fail_50_percent_step.next(update_cfn_step),
            timeout=cdk.Duration.minutes(1),
        )

        # The Lambda Function backing the custom resource
        custom_resource_handler_function = lambda_.Function(
            scope=self,
            id="CustomResourceHandler",
            code=lambda_.Code.from_asset("lambda/functions/custom_resource_handler"),
            handler="index.lambda_handler",
            runtime=lambda_.Runtime.PYTHON_3_9,
            environment={"STATE_MACHINE_ARN": state_machine.state_machine_arn},
        )
        state_machine.grant_start_execution(custom_resource_handler_function)

        # The CFN Custom Resource
        cdk.CustomResource(
            scope=self,
            id="CustomResource",
            service_token=custom_resource_handler_function.function_arn,
            # Passing the time as a parameter will trigger the custom
            # resource with every deployment.
            properties={"ExecutionTime": str(time.time())},
        )
