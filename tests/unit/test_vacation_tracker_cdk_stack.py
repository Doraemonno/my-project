import aws_cdk as core
import aws_cdk.assertions as assertions

from vacation_tracker_cdk.vacation_tracker_cdk_stack import VacationTrackerCdkStack

# example tests. To run these tests, uncomment this file along with the example
# resource in vacation_tracker_cdk/vacation_tracker_cdk_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = VacationTrackerCdkStack(app, "vacation-tracker-cdk")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
