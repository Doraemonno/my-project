from constructs import Construct
from aws_cdk import (
    Stack,
    aws_dynamodb as dynamodb,
    aws_lambda as lambda_,
    aws_apigateway as apigateway,
    RemovalPolicy
)
class VacationTrackerCdkStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # LeaveTable
        LeaveTable = dynamodb.Table(
            self, 'LeaveTable',
            table_name='LeaveTable',
            partition_key=dynamodb.Attribute(
                name='CognitoUsername',
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY
        )

        lambda_function = lambda_.Function(self, 'ProductFunction',
                                           runtime=lambda_.Runtime.PYTHON_3_12,
                                           handler='handler.lambda_handler',
                                           code=lambda_.Code.from_asset('vacation_tracker_cdk/lambda'),
                                           environment={
                                               'VACATION_TABLE_NAME': LeaveTable.table_name
                                           })

        LeaveTable.grant_read_write_data(lambda_function)

        api = apigateway.RestApi(self, 'vacation-api',
                                 rest_api_name='VacationService',
                                 description='Interactions with DynamoDB tables')

        lambda_integration = apigateway.LambdaIntegration(lambda_function,request_templates={"application/json": '{ "statusCode": "200" }'}) # type: ignore

        # /vacations Resource
        vacations = api.root.add_resource("vacations")
        vacations.add_method("GET", lambda_integration)
        vacations.add_method("POST", lambda_integration)
        add_cors_options(vacations)

def add_cors_options(resource):
    resource.add_method(
        'OPTIONS',
        apigateway.MockIntegration(
            integration_responses=[{
                'statusCode': '200',
                'responseParameters': {
                    'method.response.header.Access-Control-Allow-Headers': "'Content-Type'",
                    'method.response.header.Access-Control-Allow-Methods': "'GET,POST,OPTIONS'",
                    'method.response.header.Access-Control-Allow-Origin': "'*'",
                }
            }],
            passthrough_behavior=apigateway.PassthroughBehavior.WHEN_NO_MATCH,
            request_templates={"application/json": '{"statusCode": 200}'}
        ),
        method_responses=[{
            'statusCode': '200',
            'responseParameters': {
                'method.response.header.Access-Control-Allow-Headers': True,
                'method.response.header.Access-Control-Allow-Methods': True,
                'method.response.header.Access-Control-Allow-Origin': True,
            }
        }]
    )

        # /vacations/approvals Resource
        # vacations_approvals.add_method('GET', lambda_integration) - FRI Prayag backup
        # vacations_approvals.add_method('GET', lambda_integration) to  Prayag backup