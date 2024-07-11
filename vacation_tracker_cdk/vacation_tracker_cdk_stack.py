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

        #managerTable
        ManagerTable = dynamodb.Table(
             self, "ManagersTable",
             table_name="ManagersTable",
             partition_key=dynamodb.Attribute(
                name="CognitoUsername",
                type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY
        )

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

        VacationTable.add_global_secondary_index(
            index_name='CompanyUUIDStartDateIndex',
            partition_key=dynamodb.Attribute(
                name='CompanyUUID',
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name='StartDate',
                type=dynamodb.AttributeType.STRING
            ),
            projection_type=dynamodb.ProjectionType.ALL
        )

        lambda_function = lambda_.Function(self, 'ProductFunction',
                                           runtime=lambda_.Runtime.PYTHON_3_12,
                                           handler='handler.lambda_handler',
                                           code=lambda_.Code.from_asset('vacation_tracker_cdk/lambda'),
                                           environment={
                                               'TABLE_NAME': ManagerTable.table_name,
                                               'VacationTable_NAME': VacationTable.table_name
                                           })

        ManagerTable.grant_read_write_data(lambda_function)
        VacationTable.grant_read_write_data(lambda_function)

        api = apigateway.RestApi(self, 'product-api',
                                 rest_api_name='Product Service',
                                 description='This service serves products.')

        lambda_integration = apigateway.LambdaIntegration(lambda_function,request_templates={"application/json": '{ "statusCode": "200" }'}) # type: ignore

        manager = api.root.add_resource('manager')
        manager.add_method('GET', lambda_integration)
        manager.add_method('POST', lambda_integration)

        # /vacations Resource
        vacations = api.root.add_resource('vacations')
        vacations.add_method('GET', lambda_integration)

        # /vacations/approvals Resource
        vacations_approvals = vacations.add_resource('approvals')
        vacations_approvals.add_method('GET', lambda_integration)