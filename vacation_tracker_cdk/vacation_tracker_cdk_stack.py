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

        # VacationTable
        VacationTable = dynamodb.Table(
            self, 'VacationTable',
            table_name='VacationTable',
            partition_key=dynamodb.Attribute(
                name='CognitoUsername',
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name='StartDate',
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY
        )

        # VacationTable.add_global_secondary_index(
        #     index_name='CompanyUUIDStartDateIndex',
        #     partition_key=dynamodb.Attribute(
        #         name='CompanyUUID',
        #         type=dynamodb.AttributeType.STRING
        #     ),
        #     sort_key=dynamodb.Attribute(
        #         name='StartDate',
        #         type=dynamodb.AttributeType.STRING
        #     ),
        #     projection_type=dynamodb.ProjectionType.ALL
        # )

        lambda_function = lambda_.Function(self, 'ProductFunction',
                                           runtime=lambda_.Runtime.PYTHON_3_12,
                                           handler='handler.lambda_handler',
                                           code=lambda_.Code.from_asset('vacation_tracker_cdk/lambda'),
                                           environment={
                                               'VACATION_TABLE_NAME': VacationTable.table_name
                                           })

        VacationTable.grant_read_write_data(lambda_function)

        api = apigateway.RestApi(self, 'vacation-api',
                                 rest_api_name='VacationService',
                                 description='Interactions with DynamoDB tables')

        lambda_integration = apigateway.LambdaIntegration(lambda_function,request_templates={"application/json": '{ "statusCode": "200" }'}) # type: ignore

        # /vacations Resource
        vacations = api.root.add_resource('vacations')
        vacations.add_method('GET', lambda_integration)
        vacations.add_method('PUT', lambda_integration)

        # /vacations/approvals Resource
        # vacations_approvals.add_method('GET', lambda_integration) to be made Prayag backup
        # vacations_approvals.add_method('GET', lambda_integration) to be made Prayag backup