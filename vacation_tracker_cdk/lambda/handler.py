import json
import boto3
import os
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
table_name = os.environ['VACATION_TABLE_NAME']
table = dynamodb.Table(table_name)  # type: ignore

def lambda_handler(event, context):
    http_method = event['httpMethod']
    # /vacations Routes
    if event['resource'] == '/vacations':
        if http_method == 'GET':
            return get_vacations_between_dates(event['queryStringParameters'])
        elif http_method == 'PUT':
            return create_vacation(event['body'])
        else:
            return {"statusCode": 405, "body": json.dumps("Method Not Allowed")}
    else:
        return {"statusCode": 404, "body": json.dumps("Resource not found")}

# /vacations GET
def get_vacations_between_dates(query_params):
    try:
        from_date = query_params.get('from')
        to_date = query_params.get('to')

        if from_date and to_date:
            try:
                datetime.fromisoformat(from_date)
                datetime.fromisoformat(to_date)
            except ValueError:
                return {"statusCode": 400, "body": json.dumps("Invalid date format. Use ISO 8601 (YYYY-MM-DD).")}

        response = table.scan(
            FilterExpression="StartDate BETWEEN :from_date AND :to_date",
            ExpressionAttributeValues={
                ":from_date": from_date,
                ":to_date": to_date
            }
        )
        return {"statusCode": 200, "body": json.dumps(response['Items'])}
    except Exception as e:
        return {"statusCode": 500, "body": json.dumps(f"Error scanning items: {e}")}

# /vaactions PUT
def create_vacation(vacation_data):
    try:
        vacation_data = json.loads(vacation_data)
        table.put_item(Item=vacation_data)
        return {"statusCode": 201, "body": json.dumps("Vacation created successfully!")}
    except Exception as e:
        return {"statusCode": 500, "body": json.dumps(f"Error creating vacation: {e}")}
