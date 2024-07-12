from decimal import Decimal
import json
import boto3
import os
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
table_name = os.environ['VACATION_TABLE_NAME']
table = dynamodb.Table(table_name)  # type: ignore

def lambda_handler(event, context):
    http_method = event['httpMethod']
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, PUT, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type'
    }

    if event['resource'] == '/vacations':
        if http_method == 'GET':
            response = get_vacations_between_dates(event['queryStringParameters'])
        elif http_method == 'PUT':
            response = create_vacation(event['body'])
        else:
            response = {"statusCode": 405, "body": json.dumps("Method Not Allowed")}
    else:
        response = {"statusCode": 404, "body": json.dumps("Resource not found")}

    # Add headers to the response
    response['headers'] = headers
    return response

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

        # Convert Decimal to float for JSON serialization
        items = response['Items']
        for item in items:
            for key, value in item.items():
                if isinstance(value, Decimal):
                    item[key] = float(value)

        return {"statusCode": 200, "body": json.dumps(items)}

    except Exception as e:
        return {"statusCode": 500, "body": json.dumps(f"Error scanning items: {e}")}

def create_vacation(vacation_data):
    try:
        vacation_data = json.loads(vacation_data)
        table.put_item(Item=vacation_data)
        return {"statusCode": 201, "body": json.dumps("Vacation created successfully!")}
    except Exception as e:
        return {"statusCode": 500, "body": json.dumps(f"Error creating vacation: {e}")}
